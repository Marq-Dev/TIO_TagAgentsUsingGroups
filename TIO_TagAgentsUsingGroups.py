#!/usr/bin/env python3

import re
import os
import logging
from tenable.io import TenableIO

pattern = re.compile('REGEX_PLACEHOLDER')

def configure_logging():
    logging.basicConfig(level=logging.DEBUG)

def generate_dict(tio):
    data_dict = {'tags': {}, 'assets': {}}

    try:
        for tag in tio.tags.list():
            tag_name = tag["value"]
            tag_uuid = tag["uuid"]
            if pattern.match(tag_name):
                data_dict["tags"][tag_name] = tag_uuid

    except Exception as e:
        logging.error(f'An error occurred while fetching tags: {e}')

    return data_dict

def process_assets(tio, tag_dict, asset_dict):
    try:
        for asset in tio.workbenches.assets(('CATEGORY_PLACEHOLDER', 'CONDITION_PLACEHOLDER', 'TAG_PLACEHOLDER')):
            if not any(pattern.match(tag["tag_value"]) for tag in asset["tags"]):
                uuid = asset["tenable_uuid"][0]
                uuid_formatted = '-'.join((uuid[:8],uuid[8:12],uuid[12:16],uuid[16:20],uuid[20:32]))
                process_agents(tio, tag_dict, asset_dict, asset, uuid_formatted)

    except Exception as e:
        logging.error(f'An error occurred while processing assets: {e}')

def process_agents(tio, tag_dict, asset_dict, asset, uuid_formatted):
    try:
        for agent in tio.agents.list(('uuid', 'eq', uuid_formatted)):
            group_name = agent["groups"][0]["name"]
            asset_uuid = asset["id"]
            agent_name = agent["name"]
            tag_uuid = tag_dict.get(group_name)
            if tag_uuid:
                assign_tag(tio, asset_dict, asset_uuid, tag_uuid, agent_name)

    except Exception as e:
        logging.error(f'An error occurred while processing agents: {e}')

def assign_tag(tio, asset_dict, asset_uuid, tag_uuid, agent_name):
    try:
        if tio.tags.assign(assets=[asset_uuid], tags=[tag_uuid]):
            asset_dict[agent_name] = asset_uuid

    except Exception as e:
        logging.error(f'An error occurred while tagging agents: {e}')

def write_to_file(asset_dict):
    try:
        if asset_dict:
            with open('tagging_results.txt', 'w') as f:
                for name, uuid in asset_dict.items():
                    f.write(f"(Tagged) Hostname: {name}\n")
    except Exception as e:
        logging.error(f'An error occurred while writing to file: {e}')

def main():
    
    configure_logging()

    tio = TenableIO(os.environ['TENABLEIO_ACCESS_KEY'], os.environ['TENABLEIO_SECRET_KEY'])

    data_dict = generate_dict(tio)

    tag_dict = data_dict["tags"]

    asset_dict = data_dict["assets"]

    process_assets(tio, tag_dict, asset_dict)

    write_to_file(asset_dict)

if __name__ == "__main__":
    main()
