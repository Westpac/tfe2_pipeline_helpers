import json
import time
import inspect

import hcl
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

        # Find the ID for the Repository that matches the repository name.
        for obj in self.get_all_workspaces():
            if obj["attributes"]["name"] == workspace_name:
                return obj["id"]
        return None

    def get_all_workspaces(self):
        request = self.get(path="/organizations/" + self.organisation + "/workspaces")
        if str(request.status_code).startswith("2"):
            return request.json()['data']
        else:
            return None

    def get(self, path, params=None):
        return requests.get(url=self.base_url + path, headers=self.request_header, params=params)

    def post(self, path, data, params=None):
        return requests.post(url=self.base_url + path, data=data, headers=self.request_header, params=params)

    def patch(self, path, data, params=None):
        return requests.patch(url=self.base_url + path, data=data, headers=self.request_header, params=params)

    def delete(self, path, params=None):
        return requests.delete(url=self.base_url + path, headers=self.request_header, params=params)

class TE2WorkspaceRuns:

    def __init__(self, client, app_id, workspace_name, repository, base_api_url=None):

        self.client = client
        self.workspace_name = workspace_name
        self.workspace_id = self.client.get_workspace_id(workspace_name)
        self.app_id = app_id
        self.repository = repository

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

    def get_run_status(self, run_id):
        run = self.get_run_by_id(run_id)

        if run:
            return run['attributes']['status']
        else:
            return None

    def get_workspace_runs(self, workspace_id):
        run = self.client.get("/workspaces/" + workspace_id + "/runs")

        if str(run.status_code).startswith("2"):
            return run.json()['data']
        else:
            return None

    def get_run_by_id(self, run_id):
        run = self.client.get("/runs/" + run_id )

        if str(run.status_code).startswith("2"):
            return run.json()['data']
        else:
            return None

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

    # TODO: Error Handling
    def discard_plan_by_id(self, run_id):

        request = self.client.post(
            path="/runs/" + run_id + "/actions/discard",
            data=json.dumps({"comment": "Dropped by automated pipeline build"})
        )

        if str(request.status_code).startswith("2"):
            return "Successfully Discarded Plan: " + run_id
        else:
            return None

    def create_run(self, destroy=False):

        # Untriggered plans must be discarded before creating a new one is queued.
        self.discard_untriggered_plans()
        self._delete_all_variables()
        self.load_secrets(destroy)
        self.load_app_variables("")

        return_data = self.te2_calls.post(path="/runs", data=self._render_request_run(destroy))

        print("Creating new Terraform run against: " + self.get_workspace_id)

        self._delete_all_variables()

        # Check if run can be created Successfully
        if str(return_data.status_code).startswith("2"):
            print("New Run: " + json.loads(return_data.text)['data']['id'])

            # Keep Checking until planning phase has finished
            planning = True
            status = "planning"
            changes_detected = None
            while planning:
                planning = False
                print("Job Status: Planning")
                time.sleep(5)

                request = self.te2_calls.get(path="/runs/" + return_data.text['data']['id']).json()

                status = request['data']['attributes']['status']
                changes_detected = request['data']['attributes']['has-changes']
                if status == "planning":
                    planning = True

            print("changes detected: " + str(changes_detected))

            # If Plan Failed
            if status == "errored":
                print("Job Status: Failed")
                print("Job Output")
                exit(1)

            # If Plan Succeeded, Check for Changes
            elif status == "planned":
                if changes_detected:
                    print("Changes Detected")
                    with open('data.json', 'w') as f:
                        json.dump({'status': "changed", 'run_id': json.loads(return_data.text)['data']['id']}, f,
                                  ensure_ascii=False)

                else:
                    print("No Changes Detected")
                    with open('data.json', 'w') as f:
                        json.dump({"status": "unchanged", "run_id": json.loads(return_data.text)['data']['id']}, f,
                                  ensure_ascii=False)

            exit(0)

        else:  # Else Fail Run
            print("Plan Failed: " + json.loads(return_data.text)["data"]["attributes"]["message"])

            with open('data.json', 'w') as f:
                json.dump({"status": "failed", "run_id": json.loads(return_data.text)['data']['id']}, f,
                          ensure_ascii=False)

    def apply_run(self, run_id, destroy=False):

        # Reload secrets into Terraform.
        self.delete_all_variables()
        self.load_secrets(destroy)
        self.load_app_variables("")

        request_uri = self.base_url + "/runs/" + run_id + "/actions/apply"

        data = self._render_request_run(destroy)

        print("Applying Job: " + run_id)

        return_data = self.te2_calls.post(path="/runs/" + run_id + "/actions/apply", data=json.dumps(data))
        print(return_data.status_code)

        # TODO: Add link to logs
        # log_read_url = json.loads(return_data.text)['data']['attributes']['log-read-url']

        if str(return_data.status_code).startswith("2"):

            # Keep Checking until planning phase has finished
            status = "applying"
            while status == "applying" or status == "queued":
                print("Job Status: Applying changes")
                time.sleep(5)

                request = self.te2_calls.get(path="/runs/" + run_id).json()

                status = request['data']['attributes']['status']

            # Get Log File
            # print("Log File Directory:" + log_read_url)
            # print(requests.get(log_read_url, headers=self.header).text)

            self._delete_all_variables()

            # If Plan Failed
            if status == "errored":
                with open('data.json', 'w') as f:
                    json.dump({"status": "failed"}, f,
                              ensure_ascii=False)

            # If Plan Succeeded, Check for Changes
            elif status == "applied":
                with open('data.json', 'w') as f:
                    json.dump({"status": "applied"}, f,
                              ensure_ascii=False)

        else:  # Else Fail Run
            print("Apply Failed")
            with open('data.json', 'w') as f:
                json.dump({"status": "errored"}, f,
                          ensure_ascii=False)

class TE2WorkspaceVariables():
    def __init__(self, client, workspace_name):
        self.client = client   # Connectivity class to provide function calls.
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
        return None

    def delete_variable_by_name(self, name):
        var = self.get_variable_by_name(self, name)
        return self.client.delete(path="/vars/" + var['data']['id'])

    def delete_variable_by_id(self, id):
        return self.client.delete(path="/vars/" + id)

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
            return None

    # TODO: Error Handling
    def create_or_update_workspace_variable(self, key, value, category="terraform", sensitive=False,
                                         hcl=False):

        request = None
        request_data = self._render_request_data_workplace_variable_attributes(
            key, value, category, sensitive, hcl
        )

        existing_variable = self.get_variable_by_name(key)

        if existing_variable:
            request_data["data"]["id"] = existing_variable['id']

            request = self.client.patch(
                path= "/vars/" + existing_variable['id'],
                data=json.dumps(request_data)
            )

        else:
            request_data["filter"] = self._render_request_data_workplace_filter()
            request = self.client.post(path="/vars", data=json.dumps(request_data))

        if request.status_code().startswith("2"):
            return "Success"
        else:
            return "Failure"

    def load_secrets(self, destroy=False):
        if "environment_variables" in self.secrets:
            for obj in self.secrets["environment_variables"]:
                self._add_or_update_workspace_variable(obj, self.secrets["environment_variables"][obj], category="env", hcl=False,
                                            sensitive=True)

        if "workspace_variables" in self.secrets:
            for obj in self.secrets["workspace_variables"]:
                self._add_or_update_workspace_variable(obj, self.secrets["workspace_variables"][obj], category="env", hcl=False,
                                            sensitive=True)

        if destroy:
            self._add_or_update_workspace_variable("CONFIRM_DESTROY", "1", category="env", hcl=False,
                                        sensitive=True)


    # Environment Variables from file
    def load_environment_variables(self, directory):
        with open(directory + "environment_variables.json", 'r') as fp:
            variable_list = json.load(fp)
            for obj in variable_list:
                self._add_or_update_workspace_variable(obj, variable_list[obj], category="env",
                                            sensitive=True)

    # TODO: Rewrite the app variables.
    def load_app_variables(self, directory):
        url = "https://raw.githubusercontent.com/" + self.repository + "/env/" + self.environment + "/env/" + self.environment + ".tfvars"

        print("Getting Environment Variables from: " + url)
        variable_list = hcl.loads(requests.get(url)).json()
        for obj in variable_list:
            self._add_or_update_workspace_variable(obj, hcl.dumps(variable_list[obj]), hcl=True)

        self._add_or_update_workspace_variable("app_id", self.app_id, hcl=False)