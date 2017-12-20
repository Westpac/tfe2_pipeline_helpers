import json
import time
import requests


class TE2Client:
    def __init__(self, organisation, atlas_token, base_url="https://atlas.hashicorp.com/api/v2"):

        self.request_header = {
            'Authorization': "Bearer " + atlas_token,
            'Content-Type': 'application/vnd.api+json'
        }

        self.organisation = organisation
        self.base_url = base_url

    def get_workspace_id(self, workspace_name):
        for obj in self.get_all_workspaces():
            if obj["attributes"]["name"] == workspace_name:
                return obj["id"]
        raise KeyError('Workspace ID Cannot be found')

    def get_all_workspaces(self):
        request = self.get(path="/organizations/" + self.organisation + "/workspaces")
        if str(request.status_code).startswith("2"):
            return request.json()['data']
        else:
            raise KeyError('No workspaces can be found under this organisation')

    def get(self, path, params=None):
        return requests.get(url=self.base_url + path, headers=self.request_header, params=params)

    def post(self, path, data, params=None):
        return requests.post(url=self.base_url + path, data=data, headers=self.request_header, params=params)

    def patch(self, path, data, params=None):
        return requests.patch(url=self.base_url + path, data=data, headers=self.request_header, params=params)

    def delete(self, path, params=None):
        return requests.delete(url=self.base_url + path, headers=self.request_header, params=params)


class TE2WorkspaceConfigurations:
    def __init__(self, client, workspace_name):
        self.client = client
        self.workspace_name = workspace_name
        self.workspace_id = self.client.get_workspace_id(workspace_name)

    def _create_configuration_version(self):
        request = self.client.post(
            path="/workspaces/" + self.workspace_id + "/configuration-versions",
            data=json.dumps({
              "data": {
                "type": "configuration-versions"
              }
            })
        )

        if str(request.status_code).startswith("2"):
            print("Successfully created Configuration Version: " + request.json()['data']['id'])
            return request.json()['attributes']['upload-url']
        else:
            raise KeyError("Configuration Creation Failed")

    def upload_configuration(self):
        return("Stub")

class TE2WorkspaceRuns:
    def __init__(self, client, workspace_name):

        self.client = client
        self.workspace_name = workspace_name
        self.workspace_id = self.client.get_workspace_id(workspace_name)

    def _render_run_request(self, destroy=False):
        return {
            "data": {
                "attributes": {
                    "is-destroy": destroy
                },
                "relationships": {
                    "workspace": {
                        "data": {
                            "type": "workspaces",
                            "id": self.workspace_id
                        }
                    }
                },
                "type": "runs"
            }
        }

    def _request_run_request(self, run_id=None, destroy=False):
        if run_id:  # Run an apply
            path = "/runs/" + run_id + "/actions/apply"

        else:  # Else, Run a Plan (and discard all existing plans)
            self.discard_all_pending_runs()
            path = "/runs"

        if destroy:
            vars = TE2WorkspaceVariables(client=self.client, workspace_name=self.workspace_name)
            vars.create_or_update_workspace_variable(key="CONFIRM_DESTROY", value="1", category="env")

        request = self.client.post(path=path, data=json.dumps(self._render_run_request(destroy)))

        if str(request.status_code).startswith("2"):
            return request.json()['data']

        else:
            raise SyntaxError("Invalid call to Terraform Enterprise 2")

    def _get_run_results(self, run_id, request_type="plan", timeout_count=120):
        """
        Wait for plan/apply results, else timeout

        :param run_id: ID for the run
        :return: Returns object of the results.
        """

        if request_type is not "plan" and request_type is not "apply":
            raise KeyError("request_type must be Plan or Apply")

        for x in range(0, timeout_count):

            request = self.client.get(path="/runs/" + run_id).json()
            if request['data']['attributes']['status'] is not "planning" and \
                            request['data']['attributes']['status'] is not "applying":
                return request['data']

            print("Job Status: " + request_type + "ing | " + str(x * 10) + " seconds")
            time.sleep(10)

        raise TimeoutError("Plan took too long to resolve")

    def get_run_status(self, run_id):
        run = self.get_run_by_id(run_id)

        if run:
            return run['attributes']['status']
        else:
            raise KeyError("Run does not exist")

    def get_workspace_runs(self, workspace_id):
        run = self.client.get("/workspaces/" + workspace_id + "/runs")

        if str(run.status_code).startswith("2"):
            return run.json()['data']
        else:
            raise KeyError("Run does not exist")

    def get_run_by_id(self, run_id):
        run = self.client.get("/runs/" + run_id)

        if str(run.status_code).startswith("2"):
            return run.json()['data']
        else:
            raise KeyError("Run does not exist")

    def discard_all_pending_runs(self):

        # Get Status of all pending plans
        print("Discarding pending runs")

        runs_to_discard = True
        while runs_to_discard:
            """
            Since Runs cannot be discarded unless they are in the planned state, this loop iterates through
            each run, until there are none left in the planned, pending or planning state.
            
            The list needs to be pulled on each iteration
            """

            run_list = self.client.get(path="/workspaces/" + self.workspace_id + "/runs").json()['data']

            for run in run_list:

                run_status = run["attributes"]["status"]

                if run_status == "planned" or run_status == "pending" or run_status == "planning":
                    if run_status == "planned":
                        print("Discarding: " + run["id"])
                        self.discard_plan(run["id"])
                else:
                    runs_to_discard = False
        return True

    def discard_plan_by_id(self, run_id):

        request = self.client.post(
            path="/runs/" + run_id + "/actions/discard",
            data=json.dumps({"comment": "Dropped by automated pipeline build"})
        )

        if str(request.status_code).startswith("2"):
            return "Successfully Discarded Plan: " + run_id
        else:
            raise KeyError("Plan has already been discarded")

    def get_run_action(self, run_id, request_type):
        run = self.client.get("/runs/" + run_id + "/" + request_type)

        if str(run.status_code).startswith("2"):
            return run.json()['data']

        raise IndexError("Run or Action does not exist")

    # TODO: Get Run Log STUB
    def get_plan_log(self, run_id, request_type="plan"):
        return self.get_run_action(run_id, request_type=request_type)['attributes']['log-read-url']

    def request_run(self, request_type="plan", destroy=False):

        results = {}

        try:
            request = self._request_run_request(destroy=destroy)
        except SyntaxError:
            results = {}
        else:
            print("New Run: " + request['id'])

            results = self._get_run_results(run_id=request['id'], request_type=request_type)

            if results['attributes']['status'] == "errored":
                print("Job Status: Failed")

            elif results['attributes']['status'] == "planned":
                if results['attributes']['has-changes']:
                    print("Job Status: Changes Detected")
                else:
                    print("Job Status: No Changes Detected")

            elif results['attributes']['status'] == "applied":
                print("Job Status: Apply Successful")

        finally:
            return results


class TE2WorkspaceVariables():
    def __init__(self, client, workspace_name):
        self.client = client  # Connectivity class to provide function calls.
        self.workspace_name = workspace_name
        self.workspace_id = client.get_workspace_id(workspace_name)

    @staticmethod
    def _render_request_data_workplace_variable_attributes(key, value, category, sensitive, hcl=False):
        request_data = {
            "data": {
                "type": "vars",
                "attributes": {
                    "key": key,
                    "value": value,
                    "category": category,
                    "sensitive": sensitive
                }
            }
        }

        if hcl:
            request_data['data']['attributes']['hcl'] = True

        return request_data

    def _render_request_data_workplace_filter(self):
        return {
            "organization": {
                "username": self.client.organisation
            },
            "workspace": {
                "name": self.workspace_name
            }
        }

    def get_variable_by_name(self, name):
        vars = self.get_workspace_variables()

        if vars:
            for var in self.get_workspace_variables():
                if var['attributes']['key'] == name:
                    return var
        raise KeyError('Name: \'' + name + "\' does not exist")

    def delete_variable_by_name(self, name):
        var = self.get_variable_by_name(self, name)

        if var:
            if self.delete_variable_by_id(var):
                return True

        # Exceptions will be raised by underlying function calls on failure

    def delete_variable_by_id(self, id):
        request = self.client.delete(path="/vars/" + id)

        if str(request.status_code).startswith('2'):
            return True
        raise KeyError('ID does not exist or cannot be deleted')

    def delete_all_variables(self):
        variables = self.get_workspace_variables()

        # Delete Variables
        for variable in variables:
            self.delete_variable_by_id(variable["id"])

    def get_workspace_variables(self):
        params = {
            "filter[organization][username]": self.client.organisation,
            "filter[workspace][name]": self.workspace_name
        }

        request = self.client.get(path="/vars", params=params)

        if str(request.status_code).startswith("2"):
            return request.json()['data']
        else:
            raise KeyError('Keys or Workspace do not exist')  # TODO: Split later

    # TODO: Error Handling
    def create_or_update_workspace_variable(self, key, value, category="terraform", sensitive=False,
                                            hcl=False):
        # Data Validation
        if category is not "env" and category is not "terraform":
            raise SyntaxError("Category should be 'env' or 'terraform")
        if sensitive is not True and sensitive is not False:
            raise SyntaxError('Sensitive should be True or False')
        if hcl is not True and hcl is not False:
            raise SyntaxError('hcl should be True or False')

        request_data = self._render_request_data_workplace_variable_attributes(
            key.replace(' ', '_'), value.replace(' ', '_'), category, sensitive, hcl
        )

        try:
            existing_variable = self.get_variable_by_name(key)
        except KeyError:
            request_data["filter"] = self._render_request_data_workplace_filter()
            request = self.client.post(path="/vars", data=json.dumps(request_data))
        else:
            request_data["data"]["id"] = existing_variable
            request = self.client.patch(path="/vars/" + existing_variable, data=json.dumps(request_data))

        if str(request.status_code).startswith("2"):
            return True
        else:
            raise SyntaxError('Invalid Syntax')
