import argparse

import build_info as bf
from te2_sdk import te2 as tf

p = argparse.ArgumentParser()
p.add_argument('app_id')
p.add_argument('component_name')
p.add_argument('environment')
p.add_argument('destroy')


def main(app_id, component_name, environment, destroy=False):
    # Get Build Information
    info = bf

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

    return api.create_run(destroy=destroy)


if __name__ == "__main__":
    args = p.parse_args()
    main(args.app_id, args.component_name, args.environment, args.destroy)
