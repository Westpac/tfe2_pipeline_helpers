# Terraform 2 SDK [![Build Status](https://travis-ci.org/westpac-cloud-engineering/Terraform-Enterprise-2-Python-SDK.svg?branch=master)](https://travis-ci.org/westpac-cloud-engineering/Terraform-Enterprise-2-Python-SDK) [![codecov](https://codecov.io/gh/westpac-cloud-engineering/Terraform-Enterprise-2-Python-SDK/branch/master/graph/badge.svg)](https://codecov.io/gh/westpac-cloud-engineering/Terraform-Enterprise-2-Python-SDK) 

SDK to call Terraform Enterprise 2 using Python.

This SDK was developed to wrap Restful API calls to Terraform Enterprise 2, in order to trigger Plans, Applys and Variable updates using Jenkins. 

## How to install

```
pip install te2_sdk
```

## Triggering a Run
Below is an example of how you trigger a plan

```python
from te2_sdk import te2

client = te2.TE2Client(
    organisation="MY_TERRAFORM_ENTERPRISE_ORG",
    atlas_token="SECRET_TOKEN_HERE",
    base_url="https://atlas.hashicorp.com/api/v2" # Change this if you are using a private install
)

ws_runs = te2.TE2WorkspaceRuns(client=client, workspace_name="My Workspace Name" )
run = ws_runs.request_run(request_type="plan", destroy=False)

```

And to do a run:
```python
run = ws_runs.request_run(request_type="apply", destroy=False)
```

###Completed Functionality

- [x] Runs
    - Plan
    - Run
    - Discard
    - Get Log
- [x] Variables
    - Create
    - Read
    - Update
    - Delete
    
### Incomplete Functionality
The following items are not in development, as these Day 0 operations will eventually be wrapped up in an official Terraform Provider. 
- [ ] Workspaces
- [ ] Sentinel
- [ ] Teams