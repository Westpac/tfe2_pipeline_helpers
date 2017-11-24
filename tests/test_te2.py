import json
from unittest import TestCase, mock

from tests.requests import requests as sample_requests
from tests.responses import responses as sample_responses

from te2_sdk.te2 import TE2Client, TE2WorkspaceRuns, TE2WorkspaceVariables

def mocked_terraform_responses(*args, **kwargs):

    base_url = "https://tf-api.com"

    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    # Workspaces - Success
    if kwargs.get('url') == base_url + '/organizations/TestOrg/workspaces':
        with open('tests/responses/get_workspaces.json') as data_file:
            data = json.load(data_file)
        return MockResponse(data, 200)

    # Runs List - Success
    elif kwargs.get('url') == base_url + '/workspaces/Example_Workspace_1/runs':
        with open('tests/responses/get_runs.json') as data_file:
            data = json.load(data_file)
        return MockResponse(data, 200)

    # Run - Success
    elif kwargs.get('url') == base_url + "/runs/run-testID":
        with open('tests/responses/get_run.json') as data_file:
            data = json.load(data_file)
        return MockResponse(data, 200)

    # Variables - Success
    elif kwargs.get('url') == base_url + "/vars" and kwargs.get('params') == sample_responses.SAMPLE_GET_WORKSPACE_VARIABLES_PARAMS:
        with open('tests/responses/get_variables.json') as data_file:
            data = json.load(data_file)
        return MockResponse(data, 200)


    # Run - Success
    elif kwargs.get('url') == base_url + "/runs/run-testID/actions/discard":
        return MockResponse(None, 200)

    return MockResponse(None, 404)

def mocked_get_workspace_id(*args, **kwargs):
    return "ws-example1"

class TestTE2Client(TestCase):
    def setUp(self):
        self.client = TE2Client(
            organisation="TestOrg",
            atlas_token="Test_Token",
            base_url="https://tf-api.com"
        )

    def test_client_get(self):
        self.assertEqual(
            self.client.request_header,
            {
                'Authorization': "Bearer " + "Test_Token",
                'Content-Type': 'application/vnd.api+json'
            }
        )

    @mock.patch('te2_sdk.te2.requests.get', side_effect=mocked_terraform_responses)
    def test_get_all_workspaces_success(self, mock_get):
        self.assertEqual(
            self.client.get_all_workspaces(),
            sample_responses.SAMPLE_GET_WORKSPACES_RESPONSE
        )

    @mock.patch('te2_sdk.te2.requests.get', side_effect=mocked_terraform_responses)
    def test_request_workspace_id_success(self, mock_get):
        self.assertEqual(
            self.client.get_workspace_id("Example_Workspace_1"),
            "ws-example1"
        )


    @mock.patch('te2_sdk.te2.requests.get', side_effect=mocked_terraform_responses)
    def test_request_workspace_id_failure(self, mock_get):

        self.assertEqual(
            self.client.get_workspace_id("Fake_Workspace"),
            None
        )

    # TODO: Create Requests Tests

class TestTE2WorkspaceRuns(TestCase):

    @mock.patch('te2_sdk.te2.TE2Client.get_workspace_id', side_effect=mocked_get_workspace_id)
    def setUp(self, mock_get):
        self.client = TE2Client(
            organisation="TestOrg",
            atlas_token="Test_Token",
            base_url="https://tf-api.com"
        )

        self.runs = TE2WorkspaceRuns(
            client=self.client,
            app_id="123456",
            workspace_name="Example_Workspace_1",
            repository="TestRepository",
        )

    def test_render_run_request(self):
        self.assertEqual(
            self.runs._render_run_request(destroy=True),
            sample_requests.SAMPLE_REQUEST_RUN
        )

    @mock.patch('te2_sdk.te2.requests.get', side_effect=mocked_terraform_responses)
    def test_get_workspace_runs_success(self, mock_get):
        self.assertEqual(
            self.runs.get_workspace_runs("Example_Workspace_1"),
            sample_responses.SAMPLE_GET_WORKSPACE_RUNS
        )

    @mock.patch('te2_sdk.te2.requests.get', side_effect=mocked_terraform_responses)
    def test_get_workspace_runs_fail(self, mock_get):
        self.assertEqual(
            self.runs.get_workspace_runs("Invalid_Workspace"),
            None
        )

    @mock.patch('te2_sdk.te2.requests.get', side_effect=mocked_terraform_responses)
    def test_get_run_by_id_success(self, mock_get):
        self.assertEqual(
            self.runs.get_run_by_id("run-testID"),
            sample_responses.SAMPLE_GET_WORKSPACE_RUN
        )

    @mock.patch('te2_sdk.te2.requests.get', side_effect=mocked_terraform_responses)
    def test_get_run_by_id_fail(self, mock_get):
        self.assertEqual(
            self.runs.get_run_by_id("invalid_run"),
            None
        )

    @mock.patch('te2_sdk.te2.requests.post', side_effect=mocked_terraform_responses)
    def test_discard_plan_by_id_success(self, mock_get):
        self.assertEqual(
            self.runs.discard_plan_by_id("run-testID"),
            "Successfully Discarded Plan: run-testID"
        )

    @mock.patch('te2_sdk.te2.requests.post', side_effect=mocked_terraform_responses)
    def test_discard_plan_by_id_fail(self, mock_get):
        self.assertEqual(
            self.runs.discard_plan_by_id("invalid_run"),
            None
        )

class TestTE2WorkspaceVariables(TestCase):

    @mock.patch('te2_sdk.te2.TE2Client.get_workspace_id', side_effect=mocked_get_workspace_id)
    def setUp(self, mock_patch):

        self.client = TE2Client(
            organisation="TestOrg",
            atlas_token="Test_Token",
            base_url="https://tf-api.com"
        )

        self.variables = TE2WorkspaceVariables(
            client=self.client,
            workspace_name="Example_Workspace_1",
        )

    def test_request_data_workplace_variable_attributes(self):

        self.assertEqual(
            self.variables._render_request_data_workplace_variable_attributes(
                key="test_key",
                value="test_value",
                category="env",
                sensitive=True,
                hcl=True
            ),
            sample_requests.SAMPLE_REQUEST_WORKSPACE_BODY_HCL
        )

    def test_request_data_workplace_variable_filter(self):
        self.assertEqual(
            self.variables._render_request_data_workplace_filter(),
            sample_requests.SAMPLE_REQUEST_WORKSPACE_FILTER
        )

    @mock.patch('te2_sdk.te2.requests.get', side_effect=mocked_terraform_responses)
    def test_get_workspace_variables_success(self, mock_get):
        self.assertEqual(
            self.variables.get_workspace_variables(),
            sample_responses.SAMPLE_GET_WORKSPACE_VARIABLES
        )

    @mock.patch('te2_sdk.te2.requests.get', side_effect=mocked_terraform_responses)
    def test_get_workspace_variables_fail(self, mock_get):
        self.non_existant_vars = TE2WorkspaceVariables(
            client=self.client,
            workspace_name="NonExistantWorkspace",
        )

        self.assertEqual(
            self.non_existant_vars.get_workspace_variables(),
            None
        )

    @mock.patch('te2_sdk.te2.TE2WorkspaceVariables.get_workspace_variables', return_value=sample_responses.SAMPLE_GET_WORKSPACE_VARIABLES)
    def test_get_variable_by_name_success(self, mock_get):
        self.assertEqual(
            self.variables.get_variable_by_name("key1"),
            sample_responses.SAMPLE_GET_WORKSPACE_VARIABLE
        )

    @mock.patch('te2_sdk.te2.TE2WorkspaceVariables.get_workspace_variables', return_value=None)
    def test_get_variable_by_name_fail(self, mock_get):
        self.assertEqual(
            self.variables.get_variable_by_name("badkey"),
            None
        )
