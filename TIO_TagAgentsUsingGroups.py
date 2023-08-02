#!/usr/bin/env python3

import re
import os
import sys
import logging
from datetime import datetime
from tenable.io import TenableIO

pattern = re.compile(r'REGEX_PLACEHOLDER')

def configure_logging():
    logging.basicConfig(level=logging.DEBUG)

def generate_dict(tio):
    data_dict = {'tags': {}, 'agents': {}}

    try:
        for tag in tio.tags.list():
            tag_name = tag['value']
            tag_uuid = tag['uuid']
            if pattern.match(tag_name):
                data_dict['tags'][tag_name] = tag_uuid

    except Exception as e:
        logging.error(f'An error occurred while fetching tags: {e}')

    return data_dict

def process_assets(tio, data_dict):
    try:
        for asset in tio.workbenches.assets(('CATEGORY_PLACEHOLDER', 'CONDITION_PLACEHOLDER', 'TAG_PLACEHOLDER')):
            if not any(pattern.match(tag['tag_value']) for tag in asset['tags']):
                asset_name = asset['hostname'][0]
                if asset['tenable_uuid']:
                    uuid = asset['tenable_uuid'][0]
                    uuid_formatted = '-'.join((uuid[:8],uuid[8:12],uuid[12:16],uuid[16:20],uuid[20:32]))
                    process_agents(tio, data_dict, asset, uuid_formatted)
                else:
                    data_dict["agents"][asset_name] = "error"

    except Exception as e:
        logging.error(f'An error occurred while processing assets: {e}')

def process_agents(tio, data_dict, asset, uuid_formatted):
    try:
        for agent in tio.agents.list(('uuid', 'eq', uuid_formatted)):
            group_name = agent['groups'][0]['name']
            agent_name = agent['name']
            asset_uuid = asset['id']
            tag_uuid = data_dict['tags'].get(group_name)
            if tag_uuid:
                assign_tag(tio, data_dict, asset_uuid, tag_uuid, agent_name, group_name)
            else:
                data_dict['agents'][agent_name] = "error"

    except Exception as e:
        logging.error(f'An error occurred while processing agents: {e}')

def assign_tag(tio, data_dict, asset_uuid, tag_uuid, agent_name, group_name):
    try:
        if tio.tags.assign(assets=[asset_uuid], tags=[tag_uuid]):
            data_dict['agents'][agent_name] = group_name
        else:
            data_dict['agents'][agent_name] = "error"
    except Exception as e:
        logging.error(f'An error occurred while tagging agents: {e}')

def write_to_file(data_dict):
    try:
        if data_dict['agents']:
            date = current_datetime()
            with open(f'Tagging_Results_{date}.txt', 'w') as f:
                for name, tag in data_dict['agents'].items():
                    if tag == "error":
                        f.write(f'[Failed]\nHostname: {name}\n\n')
                    else:
                        f.write(f'[Successful]\nAgent Name: {name}\nAgent Tag: {tag}\n\n')
    except Exception as e:
        logging.error(f'An error occurred while writing to file: {e}')

def current_datetime():
    date = datetime.now()
    date_formatted = date.strftime('%m-%d-%Y_%H.%M.%S')
    return date_formatted

def main(args):
    
    configure_logging()

    tio = TenableIO(args['TENABLEIO_ACCESS_KEY'], args['TENABLEIO_SECRET_KEY'])

    data_dict = generate_dict(tio)

    process_assets(tio, data_dict)

    write_to_file(data_dict)

if __name__ == "__main__":
    main(os.environ)
