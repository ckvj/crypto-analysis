import os
import argparse
from cryptotax.const import DEFAULT_CONFIG_PATH


def process_config_location():

    parser = argparse.ArgumentParser()
    parser.add_argument('config_path', default=DEFAULT_CONFIG_PATH, nargs='?',
                        help='Optional. Config file path if not named config.ini in cwd')
    args = parser.parse_args()

    print(f'Config location = {args.config_path}')
    return args.config_path
