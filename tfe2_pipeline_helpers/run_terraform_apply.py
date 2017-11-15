import terraform_class as tf
import build_info as bf
import argparse

p = argparse.ArgumentParser()
p.add_argument('app_id')
p.add_argument('component_name')
p.add_argument('environment')
p.add_argument('run_id')
p.add_argument('destroy')

def main(app_id, component_name, environment, run_id, destroy=False):
    # Get Build Information
    info = bf.BuildInformation(
        app_id=app_id,
        component_name=component_name,
        environment=environment,
        consul_address="consul.australiaeast.cloudapp.azure.com"
    )

    build_information = info.get_build_information()
    secrets = info.get_secret_information("")

    api = tf.TerraformAPICalls(
        app_id=app_id,
        component_name=component_name,
        workspace_name=build_information["tf_workspace"],
        organisation=build_information["organisation"],
        repository=build_information["git_repository"],
        environment=environment,
        secrets=secrets
    )

    return api.apply_run(destroy=destroy, run_id=run_id)


if __name__ == "__main__":
    args = p.parse_args()
    main(args.app_id, args.component_name, args.environment, args.run_id, args.destroy)