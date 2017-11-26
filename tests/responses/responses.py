SAMPLE_GET_WORKSPACES_RESPONSE = [
    {
        "id": "ws-example1",
        "type": "workspaces",
        "attributes": {
            "name": "Example_Workspace_1",
            "environment": "default",
            "auto-apply": False,
            "locked": False,
            "created-at": "2017-11-15T03:15:29.509Z",
            "working-directory": "",
            "terraform-version": "0.10.8",
            "can-queue-destroy-plan": False,
            "ingress-trigger-attributes": {
                "branch": "dev",
                "default-branch": True,
                "vcs-root-path": "",
                "ingress-submodules": False
            },
            "permissions": {
                "can-update": True,
                "can-destroy": True,
                "can-queue-destroy": True,
                "can-queue-run": True,
                "can-update-variable": True,
                "can-lock": True,
                "can-read-settings": True
            }
        },
        "relationships": {
            "organization": {
                "data": {
                    "id": "TestOrg",
                    "type": "organizations"
                }
            },
            "ssh-key": {
                "data": None
            },
            "latest-run": {
                "data": None
            }
        }
    },
    {
        "id": "ws-example2",
        "type": "workspaces",
        "attributes": {
            "name": "Example_Workspace_2",
            "environment": "default",
            "auto-apply": False,
            "locked": False,
            "created-at": "2017-11-13T08:36:00.667Z",
            "working-directory": "",
            "terraform-version": "0.10.8",
            "can-queue-destroy-plan": False,
            "ingress-trigger-attributes": {
                "branch": "env/branch",
                "default-branch": True,
                "vcs-root-path": "",
                "ingress-submodules": False
            },
            "permissions": {
                "can-update": True,
                "can-destroy": True,
                "can-queue-destroy": True,
                "can-queue-run": True,
                "can-update-variable": True,
                "can-lock": True,
                "can-read-settings": True
            }
        },
        "relationships": {
            "organization": {
                "data": {
                    "id": "TestOrg",
                    "type": "organizations"
                }
            },
            "ssh-key": {
                "data": None
            },
            "latest-run": {
                "data": {
                    "id": "run-S9sxpqUy5GGsW86S",
                    "type": "runs"
                },
                "links": {
                    "related": "/api/v2/runs/run-S9sxpqUy5GGsW86S"
                }
            }
        }
    }
]

SAMPLE_GET_WORKSPACE_RUNS = [
    {
        "id": "run-test1",
        "type": "runs",
        "attributes": {
            "auto-apply": False,
            "error-text": None,
            "is-destroy": False,
            "message": "New image",
            "metadata": {},
            "source": "tfe-configuration-version",
            "status": "applied",
            "status-timestamps": {
                "applied-at": "2017-10-11T11:40:05+00:00",
                "planned-at": "2017-10-11T11:38:28+00:00",
                "confirmed-at": "2017-10-11T11:38:53+00:00"
            },
            "terraform-version": "0.10.7",
            "created-at": "2017-10-11T11:38:13.576Z",
            "may-canceled": False,
            "may-confirm": False,
            "may-discarded": False,
            "has-changes": True,
            "permissions": {
                "can-apply": True,
                "can-cancel": True,
                "can-discard": True,
                "can-force-execute": True
            }
        },
        "links": {
            "self": "/api/v2/runs/run-test1"
        }
    },
    {
        "id": "run-test2",
        "type": "runs",
        "attributes": {
            "auto-apply": False,
            "error-text": None,
            "is-destroy": False,
            "message": "updated managed disk id",
            "metadata": {},
            "source": "tfe-configuration-version",
            "status": "applied",
            "status-timestamps": {
                "applied-at": "2017-10-11T03:45:45+00:00",
                "planned-at": "2017-10-11T03:42:26+00:00",
                "confirmed-at": "2017-10-11T03:42:32+00:00"
            },
            "terraform-version": "0.10.7",
            "created-at": "2017-10-11T03:42:12.168Z",
            "may-canceled": False,
            "may-confirm": False,
            "may-discarded": False,
            "has-changes": True,
            "permissions": {
                "can-apply": True,
                "can-cancel": True,
                "can-discard": True,
                "can-force-execute": True
            }
        },
        "links": {
            "self": "/api/v2/runs/run-test2"
        }
    }
]

SAMPLE_GET_WORKSPACE_RUN = {
    "id": "run-testID",
    "type": "runs",
    "attributes": {
        "auto-apply": False,
        "error-text": None,
        "is-destroy": False,
        "message": "New image",
        "metadata": {},
        "source": "tfe-configuration-version",
        "status": "applied",
        "status-timestamps": {
            "applied-at": "2017-10-11T11:40:05+00:00",
            "planned-at": "2017-10-11T11:38:28+00:00",
            "confirmed-at": "2017-10-11T11:38:53+00:00"
        },
        "terraform-version": "0.10.7",
        "created-at": "2017-10-11T11:38:13.576Z",
        "may-canceled": False,
        "may-confirm": False,
        "may-discarded": False,
        "has-changes": True,
        "permissions": {
            "can-apply": True,
            "can-cancel": True,
            "can-discard": True,
            "can-force-execute": True
        }
    }
}

SAMPLE_GET_WORKSPACE_VARIABLES_PARAMS = {
    'filter[organization][username]': 'TestOrg',
    'filter[workspace][name]': 'Example_Workspace_1'
}

SAMPLE_GET_WORKSPACE_VARIABLE = {
    "id": "var-1",
    "type": "vars",
    "attributes": {
        "key": "key1",
        "sensitive": False,
        "category": "terraform",
        "hcl": False,
        "value": "val-1"
    }
}

SAMPLE_GET_WORKSPACE_VARIABLES = [
    {
        "id": "var-1",
        "type": "vars",
        "attributes": {
            "key": "key1",
            "sensitive": False,
            "category": "terraform",
            "hcl": False,
            "value": "val-1"
        }
    },
    {
        "id": "var-2",
        "type": "vars",
        "attributes": {
            "key": "key2",
            "sensitive": False,
            "category": "env",
            "hcl": False,
            "value": "val"
        }
    },
    {
        "id": "var-3",
        "type": "vars",
        "attributes": {
            "key": "key3",
            "sensitive": False,
            "category": "terraform",
            "hcl": False,
            "value": "val"
        }
    },
    {
        "id": "var-4",
        "type": "vars",
        "attributes": {
            "key": "key4",
            "sensitive": False,
            "category": "terraform",
            "hcl": True,
            "value": "val"
        }
    }
]

