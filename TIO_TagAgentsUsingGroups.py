#!/usr/bin/env python3

import re
import sys
import logging
from tenable.io import TenableIO

def generate_dict(tio):
    
    tag_dict = {}
    
    try:
    
        for tag in tio.tags.list():
            if pattern.match(tag["value"]):
                tag_dict[tag["value"]] = tag["uuid"]
    
    except Exception as e:
        logging.error(f'An error occurred while fetching tags: {str(e)}')
        sys.exit()
    
    return tag_dict

if __name__ == "__main__":

    tio = TenableIO(sys.argv[1], sys.argv[2])

    logging.basicConfig(level=logging.DEBUG)

    pattern = re.compile('REGEX_PLACEHOLDER')

    tag_dict = generate_dict(tio)

    try:
    
        for asset in tio.workbenches.assets(('CATEGORY_PLACEHOLDER', 'CONDITION_PLACEHOLDER', 'TAG_PLACEHOLDER')):
            if not any(pattern.match(tag["tag_value"]) for tag in asset["tags"]):
                uuid = asset["tenable_uuid"][0]
                uuid_formatted = '-'.join((uuid[:8],uuid[8:12],uuid[12:16],uuid[16:20],uuid[20:32]))

                try:
                
                    for agent in tio.agents.list(('uuid', 'eq', uuid_formatted)):
                        group_name = agent["groups"][0]["name"]
                        asset_uuid = asset["id"]
                        tag_uuid = tag_dict.get(group_name)
                        if tag_uuid:

                            try:

                                tio.tags.assign(assets=[asset_uuid], tags=[tag_uuid])
                            
                            except Exception as e:
                                logging.error(f'An error occurred while tagging agents: {str(e)}')
                                sys.exit()

                except Exception as e:
                    logging.error(f'An error occurred while processing agents: {str(e)}')
                    sys.exit()

    except Exception as e:
        logging.error(f'An error occurred while processing assets: {str(e)}')
        sys.exit()
