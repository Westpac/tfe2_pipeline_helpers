import json
import tests.requests.requests as sample_requests
import tests.responses.responses as sample_responses


BASE_URL = "https://tf-api.com"

class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


def mocked_terraform_responses_gets(*args, **kwargs):

    # Workspaces - Success
    if kwargs.get('url') == BASE_URL + '/organizations/TestOrg/workspaces':
        with open('tests/responses/get_workspaces.json') as data_file:
            data = json.load(data_file)
        return MockResponse(data, 200)

    # Runs List - Success
    elif kwargs.get('url') == BASE_URL + '/workspaces/Example_Workspace_1/runs':
        with open('tests/responses/get_runs.json') as data_file:
            data = json.load(data_file)
        return MockResponse(data, 200)

    # Run - Success
    elif kwargs.get('url') == BASE_URL + "/runs/run-testID":
        with open('tests/responses/get_run.json') as data_file:
            data = json.load(data_file)
        return MockResponse(data, 200)

    # Variables - Success
    elif kwargs.get('url') == BASE_URL + "/vars" and kwargs.get('params') == sample_responses.SAMPLE_GET_WORKSPACE_VARIABLES_PARAMS:
        with open('tests/responses/get_variables.json') as data_file:
            data = json.load(data_file)
        return MockResponse(data, 200)

    return MockResponse(None, 404)

def mocked_terraform_responses_posts(*args, **kwargs):
    # Run - Success
    if kwargs.get('url') == BASE_URL + "/runs/run-testID/actions/discard":
        return MockResponse(None, 200)

    # Variable - Create Var
    elif kwargs.get('url') == BASE_URL + "/vars":
        with open('tests/requests/post_variable_new.json') as req:
            if json.load(req) ==  json.loads(kwargs.get('data')): ###
                with open('tests/responses/post_variable.json') as res:
                    return MockResponse(json.load(res), 200)


    return MockResponse(None, 404)

def mocked_terraform_responses_patches(*args, **kwargs):

    # Run - Success
    if kwargs.get('url') == BASE_URL + "/runs/run-testID/actions/discard":
        return MockResponse(None, 200)


    # Variable - Update existing variable
    elif kwargs.get('url') == BASE_URL + "/vars/id-existing":
        with open('tests/requests/post_variable_existing.json') as req:
            if json.load(req) ==  json.loads(kwargs.get('data')): ###
                with open('tests/responses/post_variable.json') as res:
                    return MockResponse(json.load(res), 200)


    return MockResponse(None, 404)

def mocked_terraform_responses_deletes(*args, **kwargs):

    # Run - Success
    if kwargs.get('url') == BASE_URL + "/vars/id-existing":
        return MockResponse(None, 200)

    return MockResponse(None, 404)