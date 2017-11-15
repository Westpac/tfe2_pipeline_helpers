import consul
import json


def get_secret_information(directory):

    secrets = {}
    with open(directory + "environment_variables.json", 'r') as fp:
        variable_list = json.load(fp)

        if "environment_variables" in variable_list:
            secrets["environment_variables"] = variable_list["environment_variables"]
        if "workspace_variables" in variable_list:
            secrets["workspace_variables"] = variable_list["workspace_variables"]

    secrets['atlas_token'] = variable_list["atlas_token"]

    return secrets


class BuildInformation:
    def __init__(self, app_id, component_name, environment, consul_address, consul_token="", consul_dc=""):

        # Consul Information
        self.consul_address = consul_address
        self.consul_token = consul_token
        self.consul_dc = consul_dc

        self.component_name = component_name
        self.environment = environment
        self.app_id = app_id

        self.base_app_key = "apps/" + app_id + "/"
        self.base_component_key = self.base_app_key + "/pipelines/" + component_name + "/"
        self.base_environment_key = self.base_component_key + environment + "/"

    def get_consul_key(self, key):
        c = consul.Consul(host=self.consul_address)
        return c.kv.get(str(key), token=self.consul_token, dc=self.consul_dc)[1]['Value'].decode('utf-8')

    def get_build_information(self):
        build_information = {"git_repository": self.get_consul_key(self.base_component_key + "git_repository"),
                             "tf_workspace": self.get_consul_key(self.base_environment_key + "tf_workspace"),
                             "organisation": self.get_consul_key(
                                 "shared_services/terraform/" +
                                 self.get_consul_key(self.base_environment_key + "tf_tenant") +
                                 "/organisation"
                             )}

        # Get info from consul

        return build_information


info = BuildInformation(
    app_id="F12345",
    component_name="Infrastructure",
    environment="dev",
    consul_address="consul.australiaeast.cloudapp.azure.com"
)
