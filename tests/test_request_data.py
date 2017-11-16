from unittest import TestCase, mock
from tfe2_pipeline_helpers import terraform_class as tf
from tests.requests import requests
import json



def mocked_terraform_responses(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if kwargs.get('url') == 'https://atlas.hashicorp.com/api/v2/organizations/TestOrg/workspaces':
        with open('tests/responses/get_workspaces.json') as data_file:
            data = json.load(data_file)
        return MockResponse(data, 200)

    return MockResponse(None, 404)

class TestTerraform2ApiBodies(TestCase):

    api_calls = tf.TerraformAPICalls(
        organisation="TestOrg",
        app_id="123456",
        component_name="TestComponent",
        workspace_name="Example_Workspace_1",
        environment="TestEnvironment",
        repository="TestRepository",
        secrets={"atlas_token": "123456"}
    )


    def test_request_data_workplace_variable_attributes(self):
        self.assertEqual(
            self.api_calls._render_request_data_workplace_variable_attributes(
                key="test_key",
                value="test_value",
                category="env",
                sensitive=True,
                hcl=True
            ),
            requests.SAMPLE_REQUEST_WORKSPACE_BODY_HCL
        )

    def test_request_data_workplace_variable_filter(self):
        self.assertEqual(
            self.api_calls._render_request_data_workplace_filter(),
            requests.SAMPLE_REQUEST_WORKSPACE_FILTER
        )

    def test_request_data_workplace_variable_filter(self):
        self.assertEqual(
            self.api_calls._render_request_run(destroy=True),
            requests.SAMPLE_REQUEST_RUN
        )

    @mock.patch('tfe2_pipeline_helpers.terraform_class.requests.get', side_effect=mocked_terraform_responses)
    def test_request_workspace_id_success(self, mock_get):
        self.assertEqual(
            self.api_calls._get_workspace_id(),
            "ws-example1"
        )

    @mock.patch('tfe2_pipeline_helpers.terraform_class.requests.get', side_effect=mocked_terraform_responses)
    def test_request_workspace_id_failure(self, mock_get):
        non_existant_workspace = tf.TerraformAPICalls(
            organisation="TestOrg",
            app_id="123456",
            component_name="TestComponent",
            workspace_name="FakeWorkspace",
            environment="TestEnvironment",
            repository="TestRepository",
            secrets={"atlas_token": "123456"}
        )

        self.assertEqual(
            non_existant_workspace._get_workspace_id(),
            None
        )

