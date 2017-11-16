import json
import time

import hcl
import requests

class TE22Connectivity:
    def __init__(self, organisation, atlas_token, base_url="https://atlas.hashicorp.com/api/v2"):

        self.request_header = {
            'Authorization': "Bearer " + atlas_token,
            'Content-Type': 'application/vnd.api+json'
        }

        self.organisation = organisation()
        self.base_url = base_url

    def get(self, path, params=None):
        return requests.get(url=self.base_url + path, headers=self.request_header, params=params)

    def post(self, path, data, params=None):
        return requests.post(url=self.base_url + path, data=data, headers=self.request_header, params=params)

    def patch(self, path, data, params=None):
        return requests.patch(url=self.base_url + path, data=data, headers=self.request_header, params=params)

    def delete(self, path, params=None):
        return requests.delete(url=self.base_url + path, headers=self.request_header, params=params)


class TE2Runs:

    def __init__(self, organisation, app_id, component_name, workspace_name, environment, repository, secrets,
                 base_api_url=None):

        self.te2_calls = TE22Connectivity(
            organisation=organisation,
            atlas_token=secrets['atlas_token']
        )

        self.app_id = app_id
        self.organisation = organisation
        self.environment = environment
        self.component_name = component_name
        self.workspace_name = workspace_name
        self.repository = repository

    def _render_request_run(self, destroy=False):
        return {
            "data": {
                "attributes": {
                    "is-destroy": destroy
                },
                "relationships": {
                    "workspace": {
                        "data": {
                            "type": "workspaces",
                            "id": self._get_workspace_id()
                        }
                    }
                },
                "type": "runs"
            }
        }

    def _get_workspace_id(self):
        response = self.te2_calls.get(path= "/organizations/" + self.organisation + "/workspaces")

        # Find the ID for the Repository that matches the repository name.
        for obj in response.json()['data']:
            if obj["attributes"]["name"] == self.workspace_name:
                return obj["id"]

        # Else return an empty object
        else:
            return None

    # TODO: Rewrite the app variables.
    def load_app_variables(self, directory):
        url = "https://raw.githubusercontent.com/" + self.repository + "/env/" + self.environment + "/env/" + self.environment + ".tfvars"

        print("Getting Environment Variables from: " + url)
        variable_list = hcl.loads(requests.get(url)).json()
        for obj in variable_list:
            self._add_or_update_workspace_variable(obj, hcl.dumps(variable_list[obj]), hcl=True)

        self._add_or_update_workspace_variable("app_id", self.app_id, hcl=False)

    # TODO: Error Handling
    def get_run_status(self, run_id):
        data = self.te2_calls.get("/runs/" + run_id).json()
        return data['data']['attributes']['status']

    def discard_untriggered_plans(self):

        # Get Status of all pending plans
        print("Discarding Untriggered Jobs")

        nothing_to_discard = False
        while not nothing_to_discard:
            data = self.te2_calls.get(
                path="/workspaces/" + self._get_workspace_id() + "/runs"
            ).json()

            nothing_to_discard = True
            for obj in data['data']:

                # Delete Item
                if obj["attributes"]["status"] == "planned":
                    print("Discarding: " + obj["id"])
                    self.discard_plan(obj["id"])

                # More items left to Delete
                elif obj["attributes"]["status"] == "pending" or obj["attributes"]["status"] == "planning":
                    nothing_to_discard = False

    # TODO: Error Handling
    def discard_plan(self, run_id):
        request_uri = "/runs/" + run_id + "/actions/discard"
        data = {"comment": "Dropped by Jenkins Build"} # TODO: Add Job Number

        return self.te2_calls.post(
            path="/runs/" + run_id + "/actions/discard",
            data=json.dumps(data)
        ).text

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


class TE2Variables():
    def __init__(self, tfe2_calls, workspace_name, organisation, secrets):
        self.te2_calls = tfe2_calls   # Connectivity class to provide function calls.
        self.organisation = organisation
        self.workspace_name = workspace_name
        self.secrets = secrets

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
                "username": self.organisation
            },
            "workspace": {
                "name": self.workspace_name
            }
        }

    def _delete_variable(self, variable_id):
        return self.te2_calls.delete(path="/vars/" + variable_id)

    def _delete_all_variables(self):
        params = {"filter[organization][username]": self.organisation,
                  "filter[workspace][name]": self.workspace_name
                  }

        variable_list = self.te2_calls.get(path= "/vars", params=params).json()

        # Delete Variables
        for variable in variable_list["data"]:
            self._delete_variable(variable["id"])

    def get_workspace_variables(self):
        params = {
            "filter[organization][username]": self.organisation,
            "filter[workspace][name]": self.workspace_name
        }

        return self.te2_calls.get(path="/vars", params=params).json()

    # TODO: Error Handling
    def _add_or_update_workspace_variable(self, key, value, category="terraform", sensitive=False,
                                         hcl=False, variable_id=None):

        request_data = self._render_request_data_workplace_variable_attributes(key, value, category, sensitive, hcl).json()

        if variable_id:
            request_data["data"]["id"] = variable_id
            return self.te2_calls.patch(
                path= "/vars/" + variable_id,
                data=json.dumps(request_data)
            )

        else:
            request_data["filter"] = self._render_request_data_workplace_filter()
            return self.te2_calls.post(path="/vars", data=json.dumps(request_data)).status_code

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
