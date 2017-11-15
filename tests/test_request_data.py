from unittest import TestCase
from tfe2_pipeline_helpers import terraform_class as tf

SAMPLE_REQUEST_WORKSPACE_BODY_HCL = {
    "data": {
        "type": "vars",
        "attributes": {
            "key": "test_key",
            "value": "test_value",
            "category": "env",
            "sensitive": True,
            "hcl": True
        }
    }
}


SAMPLE_REQUEST_WORKSPACE_FILTER = {
    "organization": {
        "username": "TestOrg"
    },
    "workspace": {
        "name": "TestWorkspace"
    }
}


class TestTerraform2ApiBodies(TestCase):
    api_calls = tf.TerraformAPICalls(
        organisation="TestOrg",
        app_id="123456",
        component_name="TestComponent",
        workspace_name="TestWorkspace",
        environment="TestEnvironment",
        repository="TestRepository",
        secrets={"atlas_token": "123456"}
    )

    def test_request_data_workplace_variable_attributes(self):
        self.assertEqual(
            self.api_calls._request_data_workplace_variable_attributes(
                key="test_key",
                value="test_value",
                category="env",
                sensitive=True,
                hcl=True
            ),
            SAMPLE_REQUEST_WORKSPACE_BODY_HCL
        )

    def test_request_data_workplace_variable_filter(self):
        self.assertEqual(
            self.api_calls._request_data_workplace_filter(),
            SAMPLE_REQUEST_WORKSPACE_FILTER
        )