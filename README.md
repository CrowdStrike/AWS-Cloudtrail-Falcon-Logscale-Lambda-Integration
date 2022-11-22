![CrowdStrike CloudTrail Lambda](https://raw.githubusercontent.com/CrowdStrike/AWS-Cloudtrail-Falcon-Logscale-Lambda-Integration/main/docs/assets/cs-logo.png)

[![Twitter URL](https://img.shields.io/twitter/url?label=Follow%20%40CrowdStrike&style=social&url=https%3A%2F%2Ftwitter.com%2FCrowdStrike)](https://twitter.com/CrowdStrike)<br/>

# AWS Lambda Function: CloudTrail to Falcon LogScale Shipper

A SNS triggered Python AWS Lambda function to send AWS CloudTrail stream events to Falcon LogScale.

## Installation and Setup
### Prepare AWS CloudTrail
- select or create a source CloudTrail event data stream

### Prepare the AWS Lambda Function
- create a new Python (`python3.9`) AWS Lambda function to host the code
    - copy/paste the `lambda_function.py` code to the new Lambda function `lambda_function.py`
- create a new file named `logscale.py`, in the Lambda function file tree
    - copy/paste the `logscale.py` code
<p align="left"><img width="200px" src="https://raw.githubusercontent.com/CrowdStrike/AWS-Cloudtrail-Falcon-Logscale-Lambda-Integration/main/docs/assets/lambda_src_tree.png"></p>

- configure required Lambda environmental variables
    - HOST - target LogScale server
    - REPOSITORY - target LogScale repository
    - TOKEN - LogScale ingest token
<p align="left"><img width="500px" src="https://raw.githubusercontent.com/CrowdStrike/AWS-Cloudtrail-Falcon-Logscale-Lambda-Integration/main/docs/assets/env_vars.png"></p>

- configure the lambda run timeout setting
    - increase the function timeout value above the default (3 secs)
        - recommend at least thirty (30) seconds.  monitor logs for timeouts.

### Prepare LogScale

#### Setup the Ingest Repository
- select, or create a target ingest repository
<p align="left"><img width="500px" src="https://raw.githubusercontent.com/CrowdStrike/AWS-Cloudtrail-Falcon-Logscale-Lambda-Integration/main/docs/assets/new_repo.png"></p>

- create an ingest token, or use the default token
- configure ingest parsing
    - install the aws/cloudtrail package from the LogScale Marketplace.
        - assign the cloudtrail parser to the repository

<p align="left"><img width="500px" src="https://raw.githubusercontent.com/CrowdStrike/AWS-Cloudtrail-Falcon-Logscale-Lambda-Integration/main/docs/assets/aws_cloudtrail_pkg.png"></p>
<p align="left"><img width="500px" src="https://raw.githubusercontent.com/CrowdStrike/AWS-Cloudtrail-Falcon-Logscale-Lambda-Integration/main/docs/assets/aws_cloudtrail_pkg_install_1.png"></p>
<p align="left"><img width="500px" src="https://raw.githubusercontent.com/CrowdStrike/AWS-Cloudtrail-Falcon-Logscale-Lambda-Integration/main/docs/assets/aws_cloudtrail_pkg_install_2.png"></p>
<p align="left"><img width="500px" src="https://raw.githubusercontent.com/CrowdStrike/AWS-Cloudtrail-Falcon-Logscale-Lambda-Integration/main/docs/assets/ingest_token_parser.png"></p>

#### Edit `lambda_function.py`
##### set the HecEvent source and sourcetype
- source - set to a unique name for the cloudtrail stream
- sourcetype - set to the destination LogScale ingest parser name
```python
    # suggestion: set the source field to uniquely identify the CloudTrail stream
    source = "my-cloudtrail-stream"
    # requirment: set the sourcetype to the target ingest parser name
    sourcetype = "cloudtrail"
    hec_event = HecEvent(host=LOGSCALEHOST, index=REPOSITORY, source=source, sourcetype=sourcetype)
```
##### create additional HEC event fields (optional)
```python
    # optional: additional hec fields
    # example
    #   hev['fields'].update({"trigger": "sns"})
    #   field name: "trigger"; field value: "sns"
    hev['fields'].update({"trigger": "sns"})
```
#### Attach Requests Lambda Layer
- Attach a Lambda layer that contains the python requests library
    - create a new layer; upload zipfile that contains requests library
    - or, attach and existing requests layer to the Lambda

#### Create Lambda Test Events
- create test events; test the Lambda function


### Add a CloudTrail Lambda Trigger
- add a SNS notification delivery trigger
<p align="left"><img width="500px" src="https://raw.githubusercontent.com/CrowdStrike/AWS-Cloudtrail-Falcon-Logscale-Lambda-Integration/main/docs/assets/lambda_trigger.png"></p>

Once CloudTrail logging is enabled, events should appear in LogScale.
Review the Lambda logs for errors.  Enable DEBUG logging in the lambda
function to view POST details per lambda run.

---

<p align="center"><img src="https://raw.githubusercontent.com/CrowdStrike/AWS-Cloudtrail-Falcon-Logscale-Lambda-Integration/main/docs/assets/cs-logo-footer.png"><BR/><img width="250px" src="https://raw.githubusercontent.com/CrowdStrike/AWS-Cloudtrail-Falcon-Logscale-Lambda-Integration/main/docs/assets/adversary-red-eyes.png"></P>
<h3><P align="center">WE STOP BREACHES</P></h3>