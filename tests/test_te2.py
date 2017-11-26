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
    def test_get_all_workspaces_success(self, *args, **kwargs):
        self.assertEqual(
            self.client.get_all_workspaces(),
            sample_responses.SAMPLE_GET_WORKSPACES_RESPONSE
        )

    @mock.patch('te2_sdk.te2.requests.get', side_effect=mock_gets)
    def test_request_workspace_id_success(self, *args, **kwargs):
        self.assertEqual(
            self.client.get_workspace_id("Example_Workspace_1"),
            "ws-example1"
        )

    @mock.patch('te2_sdk.te2.requests.get', side_effect=mock_gets)
    def test_request_workspace_id_failure(self, *args, **kwargs):
        self.assertRaises(KeyError, lambda: self.client.get_workspace_id("Fake_Workspace"))

        # TODO: Create Requests Tests


class TestTE2WorkspaceRuns(TestCase):
    @mock.patch('te2_sdk.te2.TE2Client.get_workspace_id', return_value="ws-example1")
    def setUp(self, *args, **kwargs):
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
    def test_get_workspace_runs_success(self, *args, **kwargs):
        self.assertEqual(
            self.runs.get_workspace_runs("Example_Workspace_1"),
            sample_responses.SAMPLE_GET_WORKSPACE_RUNS
        )

    @mock.patch('te2_sdk.te2.requests.get', side_effect=mock_gets)
    def test_get_workspace_runs_fail(self, *args, **kwargs):
        self.assertRaises(KeyError, lambda: self.runs.get_workspace_runs("Invalid_Workspace"))

    @mock.patch('te2_sdk.te2.TE2WorkspaceRuns.get_run_by_id', return_value=sample_responses.SAMPLE_GET_WORKSPACE_RUN)
    def test_get_run_status_success(self, *args, **kwargs):
        self.assertEqual(
            self.runs.get_run_status("run-testID"),
            "applied"
        )

    @mock.patch('te2_sdk.te2.TE2WorkspaceRuns.get_run_by_id', return_value=None)
    def test_get_run_status_fail(self, *args, **kwargs):
        self.assertRaises(KeyError, lambda: self.runs.get_run_status("non_existant_id"))

    @mock.patch('te2_sdk.te2.requests.get', side_effect=mock_gets)
    def test_get_run_by_id_success(self, *args, **kwargs):
        self.assertEqual(
            self.runs.get_run_by_id("run-testID"),
            sample_responses.SAMPLE_GET_WORKSPACE_RUN
        )

    @mock.patch('te2_sdk.te2.requests.get', side_effect=mock_gets)
    def test_get_run_by_id_fail(self, *args, **kwargs):
        self.assertRaises(KeyError, lambda: self.runs.get_run_by_id("invalid_run"))

    @mock.patch('te2_sdk.te2.requests.post', side_effect=mock_posts)
    def test_discard_plan_by_id_success(self, *args, **kwargs):
        self.assertEqual(
            self.runs.discard_plan_by_id("run-testID"),
            "Successfully Discarded Plan: run-testID"
        )

    @mock.patch('te2_sdk.te2.requests.post', side_effect=mock_posts)
    def test_discard_plan_by_id_fail(self, *args, **kwargs):
        self.assertRaises(KeyError, lambda: self.runs.discard_plan_by_id("invalid_run"))

    @mock.patch('te2_sdk.te2.requests.get', side_effect=mock_gets)
    def test_get_run_action_plan_success(self, *args, **kwargs):
        self.assertEqual(
            self.runs.get_run_action(run_id="run-testID", request_type="plan"),
            sample_responses.SAMPLE_GET_WORKSPACE_RUN_PLAN
        )

    @mock.patch('te2_sdk.te2.requests.get', side_effect=mock_gets)
    def test_get_run_action_apply_success(self, *args, **kwargs):
        self.assertEqual(
            self.runs.get_run_action(run_id="run-testID", request_type="apply"),
            sample_responses.SAMPLE_GET_WORKSPACE_RUN_APPLY
        )

    @mock.patch('te2_sdk.te2.requests.get', side_effect=mock_gets)
    def test_get_run_action_fail(self, *args, **kwargs):
        self.assertRaises(IndexError, lambda: self.runs.get_run_action(run_id="run-fakeid", request_type="apply"))

    @mock.patch('te2_sdk.te2.requests.get', side_effect=mock_gets)
    def test_get_plan_log_success(self, *args, **kwargs):
        self.assertEqual(
            self.runs.get_plan_log(run_id="run-testID", request_type="apply"),
            "https://logurl.com"
        )

    @mock.patch('te2_sdk.te2.TE2WorkspaceRuns.discard_all_pending_runs', return_value=True)
    @mock.patch('te2_sdk.te2.requests.post', side_effect=mock_posts)
    def test_request_run_request_apply_success(self, *args, **kwargs):
        self.assertEqual(
            self.runs._request_run_request(
                run_id="run-testID",
            ),
            sample_responses.SAMPLE_GET_WORKSPACE_RUN
        )

    @mock.patch('te2_sdk.te2.TE2WorkspaceRuns.discard_all_pending_runs', return_value=True)
    @mock.patch('te2_sdk.te2.requests.post', side_effect=mock_posts)
    def test_request_run_request_plan_success(self, *args, **kwargs):
        self.assertEqual(
            self.runs._request_run_request(
                run_id=None,
            ),
            sample_responses.SAMPLE_GET_WORKSPACE_RUN
        )

    @mock.patch('te2_sdk.te2.TE2WorkspaceRuns.discard_all_pending_runs', return_value=True)
    @mock.patch('te2_sdk.te2.requests.post', side_effect=mock_posts)
    def test_request_run_request_apply_fail(self, *args, **kwargs):
        self.assertRaises(SyntaxError, lambda: self.runs._request_run_request(run_id="fake_id"))

    @mock.patch('te2_sdk.te2.TE2Client.get_workspace_id', return_value="ws-example1")
    @mock.patch('te2_sdk.te2.TE2WorkspaceVariables.create_or_update_workspace_variable', return_value="true")
    @mock.patch('te2_sdk.te2.TE2WorkspaceRuns.discard_all_pending_runs', return_value=True)
    @mock.patch('te2_sdk.te2.requests.post', side_effect=mock_posts)
    def test_request_run_request_plan_success_destroy(self, *args, **kwargs):
        self.assertEqual(
            self.runs._request_run_request(
                run_id="run-testID",
                destroy=True
            ),
            sample_responses.SAMPLE_GET_WORKSPACE_RUN
        )

    @mock.patch('te2_sdk.te2.requests.get', side_effect=mock_gets)
    def test_get_run_results(self, *args, **kwargs):
        self.assertEqual(
            self.runs._get_run_results(
                run_id="run-testID",
                request_type="plan"
            ),
            sample_responses.SAMPLE_GET_WORKSPACE_RUN

        )

    @mock.patch('te2_sdk.te2.requests.get', side_effect=mock_gets)
    def test_get_apply_results(self, *args, **kwargs):
        self.assertEqual(
            self.runs._get_run_results(
                run_id="run-testID",
                request_type="apply"
            ),
            sample_responses.SAMPLE_GET_WORKSPACE_RUN

        )

    @mock.patch('te2_sdk.te2.requests.get', side_effect=mock_gets)
    def test_get_apply_results_invalid_request(self, *args, **kwargs):
        self.assertRaises(KeyError, lambda: self.runs._get_run_results(
                run_id="run-testID",
                request_type="invalid"
            ))

    @mock.patch('te2_sdk.te2.requests.get', side_effect=mock_gets)
    def test_get_apply_results_timeout(self, *args, **kwargs):
        self.assertRaises(TimeoutError, lambda: self.runs._get_run_results(
                run_id="run-testID",
                request_type="plan",
                timeout_count=0
            ))

    """
    @mock.patch('te2_sdk.te2.requests.get', side_effect=mock_gets)
    def test_request_run_success(self, *args, **kwargs):
        self.assertEqual(
            self.runs.request_run(
                request_type="plan",
                destroy=False
            ),
            sample_responses.SAMPLE_GET_WORKSPACE_RUN

        )
    """

class TestTE2WorkspaceVariables(TestCase):
    @mock.patch('te2_sdk.te2.TE2Client.get_workspace_id', return_value="ws-example1")
    def setUp(self, *args, **kwargs):
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
    def test_get_workspace_variables_success(self, *args, **kwargs):
        self.assertEqual(
            self.variables.get_workspace_variables(),
            sample_responses.SAMPLE_GET_WORKSPACE_VARIABLES
        )

    @mock.patch('te2_sdk.te2.requests.get', side_effect=mock_gets)
    @mock.patch('te2_sdk.te2.TE2Client.get_workspace_id', return_value="ws-example1")
    def test_get_workspace_variables_fail(self, *args, **kwargs):
        self.non_existant_vars = TE2WorkspaceVariables(
            client=self.client,
            workspace_name="NonExistantWorkspace",
        )

        self.assertRaises(KeyError, lambda: self.non_existant_vars.get_workspace_variables())

    @mock.patch('te2_sdk.te2.TE2WorkspaceVariables.get_workspace_variables',
                return_value=sample_responses.SAMPLE_GET_WORKSPACE_VARIABLES)
    def test_get_variable_by_name_success(self, *args, **kwargs):
        self.assertEqual(
            self.variables.get_variable_by_name("key1"),
            sample_responses.SAMPLE_GET_WORKSPACE_VARIABLE
        )

    @mock.patch('te2_sdk.te2.TE2WorkspaceVariables.get_workspace_variables', return_value=None)
    def test_get_variable_by_name_fail(self, *args, **kwargs):
        self.assertRaises(KeyError, lambda: self.variables.get_variable_by_name("badkey"))

    @mock.patch('te2_sdk.te2.requests.post', side_effect=mock_posts)
    def test_create_or_update_workspace_variable_invalid_category(self, *args, **kwargs):
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
    def test_create_or_update_workspace_variable_invalid_sensitive(self, *args, **kwargs):
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
    def test_create_or_update_workspace_variable_invalid_hcl(self, *args, **kwargs):
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
    def delete_variable_by_id_success(self, *args, **kwargs):
        self.assertEqual(
            self.variables.delete_variable_by_id(
                id="id-existing"
            ),
            "Success"
        )

    @mock.patch('te2_sdk.te2.requests.delete', side_effect=mock_deletes)
    def delete_variable_by_id_fail(self, *args, **kwargs):
        self.assertRaises(
            KeyError,
            lambda: self.variables.delete_variable_by_id(
                id="id-fake"
            ),
        )

    @mock.patch('te2_sdk.te2.TE2WorkspaceVariables.get_variable_by_name', return_value=None)
    @mock.patch('te2_sdk.te2.requests.post', side_effect=mock_posts)
    def test_create_or_update_workspace_variable_new_success(self, *args, **kwargs):
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
    def test_create_or_update_workspace_variable_new_fail(self, *args, **kwargs):
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
    def test_create_or_update_workspace_variable_existing_success(self, *args, **kwargs):
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

    @mock.patch('te2_sdk.te2.TE2WorkspaceVariables.get_variable_by_name', return_value="id-existing")
    @mock.patch('te2_sdk.te2.requests.delete', side_effect=mock_deletes)
    def test_delete_variable_by_name_success(self,*args, **kwargs):
        self.assertEqual(
            self.variables.delete_variable_by_name("Some_Real_ID"),
            True
        )

    @mock.patch('te2_sdk.te2.TE2WorkspaceVariables.get_variable_by_name', side_effect=KeyError)
    @mock.patch('te2_sdk.te2.requests.delete', side_effect=mock_deletes)
    def test_delete_variable_by_name_failure(self,*args, **kwargs):
        self.assertRaises(KeyError, lambda: self.variables.delete_variable_by_name("FakeID"))

    @mock.patch('te2_sdk.te2.requests.delete', side_effect=mock_deletes)
    def test_delete_variable_by_id_success(self, *args, **kwargs):
        self.assertEqual(
            self.variables.delete_variable_by_id("id-existing"),
            True
        )

    @mock.patch('te2_sdk.te2.requests.delete', side_effect=mock_deletes)
    def test_delete_variable_by_id_failure(self, *args, **kwargs):
        self.assertRaises(KeyError, lambda: self.variables.delete_variable_by_id("fake-id"))

    @mock.patch('te2_sdk.te2.TE2WorkspaceVariables.get_workspace_variables', return_value=sample_responses.SAMPLE_GET_WORKSPACE_VARIABLES)
    @mock.patch('te2_sdk.te2.TE2WorkspaceVariables.delete_variable_by_id', return_value=True)
    def test_delete_all_variables(self, *args, **kwargs):
        self.assertEqual(
            self.variables.delete_all_variables(),
            None
        )
