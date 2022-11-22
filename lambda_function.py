"""CrowdStrike: AWS Lambda: CloudTrail events to Falcon LogScale

   Send AWS Cloudtrail events to Logscale HEC ingestion api

   Required variable:
    LOGSCALEHOST - LogScale server
    REPOSITORY - LogScale repository
    TOKEN - LogScale ingest token

   Assumption:
        Triggered by AWS SNS (Simple Notification Service)
"""

import os
import io
import time
import gzip
import json
import boto3
import logging
from logscale import IngestApi, HecEvent, Payload, S3Exception
from xmlrpc.client import Boolean

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logging.Formatter.converter = time.gmtime
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')

# Required:
#   LOGSCALEHOST - LogScale server
#     REPOSITORY - LogScale repository
#          TOKEN - LogScale ingest token
LOGSCALEHOST = os.environ.get('HOST')
REPOSITORY = os.environ.get('REPOSITORY')
TOKEN = os.environ.get('TOKEN')

def lambda_handler(event, context):
    logscale = IngestApi(host=LOGSCALEHOST, repository=REPOSITORY, token=TOKEN)

    # suggestion: set the source field to uniquely identify the CloudTrail stream
    source = "my-cloudtrail-stream"
    # requirment: set the sourcetype to the target ingest parser name
    sourcetype = "cloudtrail"
    hec_event = HecEvent(host=LOGSCALEHOST, index=REPOSITORY, source=source, sourcetype=sourcetype)
    payload = Payload()

    # Extract the S3 bucket from SNS triggering event
    sns_message = json.loads(event['Records'][0]['Sns']['Message'])
    s3bucket = str(sns_message['s3Bucket'])
    s3key = str(sns_message['s3ObjectKey'][0])

    # Fetch the S3 bucket
    try:
        response = s3.get_object(Bucket=s3bucket, Key=s3key)
    except S3Exception as s3e:
        e_message = f"""
            Exception getting S3 bucket object:
                bucket: {s3bucket}
                object: {s3key}
        """
        logger.error(e_message)
        raise s3e

    # Extract the bucket contents
    content = response['Body'].read()
    with gzip.GzipFile(fileobj=io.BytesIO(content), mode='rb') as fh:
        cloudtrail_event_json = json.load(fh)

    # pack records; send batches
    for record in cloudtrail_event_json['Records']:
        # create base hec event
        hev = hec_event.create(message=record)

        # optional: additional hec fields
        # example
        #   hev['fields'].update({"trigger": "sns"})

        # add event to POST payload
        payload.pack(hev)
        if payload.full: # send event batch
            logger.debug("post events: {ec}, payload: {b}".format(ec=payload.event_count, b=payload.size_bytes))
            logscale.send_event("hec", payload.packed)
            payload.reset()

    # send residual events
    if not payload.empty:
        logger.debug("post events: {ec}, payload: {b}".format(ec=payload.event_count, b=payload.size_bytes))
        logscale.send_event("hec", payload.packed)