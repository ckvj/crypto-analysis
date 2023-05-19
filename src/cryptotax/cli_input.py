import argparse
from .const import DEFAULT_CONFIG_PATH


def collect_config_filepath():

    parser = argparse.ArgumentParser()
    parser.add_argument('config_path', default=DEFAULT_CONFIG_PATH, nargs='?',
                        help='Optional. Config file path if not named config.ini in cwd')
    args = parser.parse_args()

    print(f'Config location = {args.config_path}')
    return args.config_path
