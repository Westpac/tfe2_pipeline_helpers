from unittest import TestCase, mock
from tests.requests import requests as sample_requests
from tests.responses import responses as sample_responses
from tests.mocks import mocked_terraform_responses_gets as mock_gets
from tests.mocks import mocked_terraform_responses_posts as mock_posts
from tests.mocks import mocked_terraform_responses_patches as mock_patches
from tests.mocks import mocked_terraform_responses_deletes as mock_deletes



from te2_sdk.te2 import TE2Client, TE2WorkspaceRuns, TE2WorkspaceVariables

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

    @mock.patch('te2_sdk.te2.requests.get', side_effect=mock_gets)
    def test_get_all_workspaces_success(self, mock_get):
        self.assertEqual(
            self.client.get_all_workspaces(),
            sample_responses.SAMPLE_GET_WORKSPACES_RESPONSE
        )

    @mock.patch('te2_sdk.te2.requests.get', side_effect=mock_gets)
    def test_request_workspace_id_success(self, mock_get):
        self.assertEqual(
            self.client.get_workspace_id("Example_Workspace_1"),
            "ws-example1"
        )

    @mock.patch('te2_sdk.te2.requests.get', side_effect=mock_gets)
    def test_request_workspace_id_failure(self, mock_get):
        self.assertRaises(KeyError, lambda: self.client.get_workspace_id("Fake_Workspace"))

    # TODO: Create Requests Tests

class TestTE2WorkspaceRuns(TestCase):

    @mock.patch('te2_sdk.te2.TE2Client.get_workspace_id', return_value="ws-example1")
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

    @mock.patch('te2_sdk.te2.requests.get', side_effect=mock_gets)
    def test_get_workspace_runs_success(self, mock_get):
        self.assertEqual(
            self.runs.get_workspace_runs("Example_Workspace_1"),
            sample_responses.SAMPLE_GET_WORKSPACE_RUNS
        )

    @mock.patch('te2_sdk.te2.requests.get', side_effect=mock_gets)
    def test_get_workspace_runs_fail(self, mock_get):
        self.assertRaises(KeyError, lambda: self.runs.get_workspace_runs("Invalid_Workspace"))


    @mock.patch('te2_sdk.te2.TE2WorkspaceRuns.get_run_by_id', return_value=sample_responses.SAMPLE_GET_WORKSPACE_RUN)
    def test_get_run_status_success(self, mock_get):
        self.assertEqual(
            self.runs.get_run_status("run-testID"),
            "applied"
        )

    @mock.patch('te2_sdk.te2.TE2WorkspaceRuns.get_run_by_id', return_value=None)
    def test_get_run_status_fail(self, mock_get):
        self.assertRaises(KeyError, lambda: self.runs.get_run_status("non_existant_id"))


    @mock.patch('te2_sdk.te2.requests.get', side_effect=mock_gets)
    def test_get_run_by_id_success(self, mock_get):
        self.assertEqual(
            self.runs.get_run_by_id("run-testID"),
            sample_responses.SAMPLE_GET_WORKSPACE_RUN
        )

    @mock.patch('te2_sdk.te2.requests.get', side_effect=mock_gets)
    def test_get_run_by_id_fail(self, mock_get):
        self.assertRaises(KeyError, lambda: self.runs.get_run_by_id("invalid_run"))


    @mock.patch('te2_sdk.te2.requests.post', side_effect=mock_posts)
    def test_discard_plan_by_id_success(self, mock_get):
        self.assertEqual(
            self.runs.discard_plan_by_id("run-testID"),
            "Successfully Discarded Plan: run-testID"
        )

    @mock.patch('te2_sdk.te2.requests.post', side_effect=mock_posts)
    def test_discard_plan_by_id_fail(self, mock_get):
        self.assertRaises(KeyError, lambda: self.runs.discard_plan_by_id("invalid_run"))


class TestTE2WorkspaceVariables(TestCase):

    @mock.patch('te2_sdk.te2.TE2Client.get_workspace_id', return_value="ws-example1")
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

    @mock.patch('te2_sdk.te2.requests.get', side_effect=mock_gets)
    def test_get_workspace_variables_success(self, mock_get):
        self.assertEqual(
            self.variables.get_workspace_variables(),
            sample_responses.SAMPLE_GET_WORKSPACE_VARIABLES
        )


    @mock.patch('te2_sdk.te2.requests.get', side_effect=mock_gets)
    @mock.patch('te2_sdk.te2.TE2Client.get_workspace_id', return_value="ws-example1")
    def test_get_workspace_variables_fail(self, patch1, patch2):

        self.non_existant_vars = TE2WorkspaceVariables(
            client=self.client,
            workspace_name="NonExistantWorkspace",
        )

        self.assertRaises(KeyError, lambda: self.non_existant_vars.get_workspace_variables())

    @mock.patch('te2_sdk.te2.TE2WorkspaceVariables.get_workspace_variables', return_value=sample_responses.SAMPLE_GET_WORKSPACE_VARIABLES)
    def test_get_variable_by_name_success(self, mock_get):
        self.assertEqual(
            self.variables.get_variable_by_name("key1"),
            sample_responses.SAMPLE_GET_WORKSPACE_VARIABLE
        )

    @mock.patch('te2_sdk.te2.TE2WorkspaceVariables.get_workspace_variables', return_value=None)
    def test_get_variable_by_name_fail(self, mock_get):
        self.assertRaises(KeyError, lambda: self.variables.get_variable_by_name("badkey"))



    """
    @mock.patch('te2_sdk.te2.requests.post', side_effect=mock_posts)
    def test_create_or_update_workspace_variable_new_success(self, mock_get):
        self.assertEqual(
            self.variables.create_or_update_workspace_variable(
                key="key1",
                value="value",
                category="terraform",
                sensitive=False,
                hcl=False
            ),
            "Success"
        )
    """

    @mock.patch('te2_sdk.te2.requests.post', side_effect=mock_posts)
    def test_create_or_update_workspace_variable_invalid_category(self, mock_get):
        self.assertRaises(
            SyntaxError,
            lambda: self.variables.create_or_update_workspace_variable(
                key="key1",
                value="value",
                category="invalid",
                sensitive=False,
                hcl=False
            )
        )



    @mock.patch('te2_sdk.te2.requests.post', side_effect=mock_posts)
    def test_create_or_update_workspace_variable_invalid_sensitive(self, mock_get):
        self.assertRaises(
            SyntaxError,
            lambda: self.variables.create_or_update_workspace_variable(
                key="key1",
                value="value",
                category="env",
                sensitive="invalid",
                hcl=False
            )
        )

    @mock.patch('te2_sdk.te2.requests.post', side_effect=mock_posts)
    def test_create_or_update_workspace_variable_invalid_hcl(self, mock_get):
        self.assertRaises(
            SyntaxError,
            lambda: self.variables.create_or_update_workspace_variable(
                key="key1",
                value="value",
                category="env",
                sensitive=False,
                hcl="invalid"
            )
        )


    @mock.patch('te2_sdk.te2.requests.delete', side_effect=mock_deletes)
    def delete_variable_by_id_success(self, mock_get):
        self.assertEqual(
            self.variables.delete_variable_by_id(
                id="id-existing"
            ),
            "Success"
        )

    @mock.patch('te2_sdk.te2.requests.delete', side_effect=mock_deletes)
    def delete_variable_by_id_fail(self, mock_get):
        self.assertRaises(
            KeyError,
            lambda: self.variables.delete_variable_by_id(
                id="id-fake"
            ),
        )

    @mock.patch('te2_sdk.te2.TE2WorkspaceVariables.get_variable_by_name', return_value=None)
    @mock.patch('te2_sdk.te2.requests.post', side_effect=mock_posts)
    def test_create_or_update_workspace_variable_new_success(self, patch_1, patch_2):
        self.assertTrue(
            self.variables.create_or_update_workspace_variable(
                key="key1",
                value="value",
                category="env",
                sensitive=False,
                hcl=False
            )
        )

    @mock.patch('te2_sdk.te2.TE2WorkspaceVariables.get_variable_by_name', return_value=None)
    @mock.patch('te2_sdk.te2.requests.post', side_effect=mock_posts)
    def test_create_or_update_workspace_variable_new_fail(self, patch_1, patch_2):
        self.assertRaises(
            SyntaxError,
            lambda: self.variables.create_or_update_workspace_variable(
                key="INVALID_KEY)(!&$@)(&#$@",
                value="value",
                category="env",
                sensitive=False,
                hcl=False
            )
        )


    @mock.patch('te2_sdk.te2.TE2WorkspaceVariables.get_variable_by_name', return_value="id-existing")
    @mock.patch('te2_sdk.te2.requests.patch', side_effect=mock_patches)
    def test_create_or_update_workspace_variable_existing_success(self, patch_1, patch_2):
        self.assertEqual(
            self.variables.create_or_update_workspace_variable(
                key="key1",
                value="value",
                category="env",
                sensitive=False,
                hcl=False
            ),
            True
        )

