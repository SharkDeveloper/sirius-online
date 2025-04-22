import os
import subprocess

import click
from dotenv import load_dotenv

load_dotenv()  # For DJANGO_SETTINGS_MODULE load env


HTTP_PROXY = os.getenv("HTTP_PROXY")

REGISTRY_URL = os.getenv("REGISTRY_URL")
REGISTRY_ID = os.getenv("REGISTRY_ID")

IMAGE = os.getenv("SERVER_IMAGE")
VERSION = os.getenv("VERSION")


@click.command()
@click.option('--no-proxy', is_flag=True, help='Disable build under proxy')
def main(no_proxy: bool) -> None:
    tag = f'{REGISTRY_URL}/{REGISTRY_ID}/{IMAGE}:{VERSION}'

    build_cmd = ['docker', 'build', '--target', "development", '-t', tag]

    if not no_proxy:
        build_cmd.extend(
            [
                '--build-arg',
                f'HTTP_PROXY={HTTP_PROXY}',
                '--build-arg',
                f'HTTPS_PROXY={HTTP_PROXY}',
            ],
        )

    subprocess.run([*build_cmd, '.'])
    subprocess.run(['docker', 'push', tag])


if __name__ == '__main__':
    main()
