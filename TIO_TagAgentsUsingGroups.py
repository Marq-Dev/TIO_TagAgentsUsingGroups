#!/usr/bin/env python3

import re
import os
import sys
import logging
from tenable.io import TenableIO

# Regex pattern for matching tags.
pattern = re.compile('REGEX_PLACEHOLDER')

def get_tenable_instance(access_key, secret_key):
    return TenableIO(access_key, secret_key)

def configure_logging():
    logging.basicConfig(level=logging.DEBUG)

def generate_dict(tio):
    data_dict = {'tags': {}, 'assets': {}}

    try:
        # Queries the "tags" API for any tags that match the regex pattern.
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
        # Queries the "assets" API for any assets with tags that match the provided tag in TAG_PLACEHOLDER.
        for asset in tio.workbenches.assets(('CATEGORY_PLACEHOLDER', 'CONDITION_PLACEHOLDER', 'TAG_PLACEHOLDER')):
            # Loops through queried assets checking if any tags match the regex pattern.
            # If the asset does not have any tags that match the regex pattern, the agent UUID is extracted.
            if not any(pattern.match(tag["tag_value"]) for tag in asset["tags"]):
                uuid = asset["tenable_uuid"][0]
                # UUID is formatted with hyphens as it's required by the "agents" API.
                uuid_formatted = '-'.join((uuid[:8],uuid[8:12],uuid[12:16],uuid[16:20],uuid[20:32]))
                process_agents(tio, tag_dict, asset_dict, asset, uuid_formatted)

    except Exception as e:
        logging.error(f'An error occurred while processing assets: {e}')

def process_agents(tio, tag_dict, asset_dict, asset, uuid_formatted):
    try:
        # Queries the "agents" API for any agents that match the UUID extracted from the asset.
        # Extracts the name of the group and the asset UUID of the agent.
        for agent in tio.agents.list(('uuid', 'eq', uuid_formatted)):
            group_name = agent["groups"][0]["name"]
            asset_uuid = asset["id"]
            agent_name = agent["name"]
            # Checks if any tag names match the group name in the tag dict.
            # Assigns the tag uuid if a match is found.
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
    if asset_dict:
        with open('tagging_results.txt', 'w') as f:
            for name, uuid in asset_dict.items():
                f.write(f"(Tagged) Hostname: {name}\n")

def main():
    # Configures the API endpoint with an access and secret key.
    tio = get_tenable_instance(os.environ['TENABLEIO_ACCESS_KEY'], os.environ['TENABLEIO_SECRET_KEY'])

    # Enable logging for debugging purposes.
    configure_logging()

    # Assigns the output of the dict generation function.
    data_dict = generate_dict(tio)

    tag_dict = data_dict["tags"]

    asset_dict = data_dict["assets"]

    process_assets(tio, tag_dict, asset_dict)

    write_to_file(asset_dict)

if __name__ == "__main__":
    main()
