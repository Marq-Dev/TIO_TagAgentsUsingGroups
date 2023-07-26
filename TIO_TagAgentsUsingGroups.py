#!/usr/bin/env python3

import re
import os
import sys
import logging
from tenable.io import TenableIO

# Function for generating a dict of current tags in Tenable.
# Dict uses the tag name as the key, and the tag UUID as the value.
def generate_dict(tio):
    
    tag_dict = {}
    
    try:
        # Queries the "tags" API for any tags that match the regex pattern.
        for tag in tio.tags.list():
            if pattern.match(tag["value"]):
                tag_dict[tag["value"]] = tag["uuid"]
    
    # Error handling. Exits if an error is encountered.
    except Exception as e:
        logging.error(f'An error occurred while fetching tags: {str(e)}')
        sys.exit()
    
    return tag_dict

if __name__ == "__main__":

    # Configures the API endpoint with an access and secret key.
    tio = TenableIO(os.environ['TENABLEIO_ACCESS_KEY'], os.environ['TENABLEIO_SECRET_KEY'])

    # Enable logging for debugging purposes.
    logging.basicConfig(level=logging.DEBUG)

    # Regex pattern for matching tags.
    pattern = re.compile('REGEX_PLACEHOLDER')

    # Assigns the output of the dict generation function.
    tag_dict = generate_dict(tio)

    try:
        
        # Queries the "assets" API for any assets with tags that match the provided tag in TAG_PLACEHOLDER.
        for asset in tio.workbenches.assets(('CATEGORY_PLACEHOLDER', 'CONDITION_PLACEHOLDER', 'TAG_PLACEHOLDER')):
            # Loops through queried assets checking if any tags match the regex pattern.
            # If the asset does not have any tags that match the regex pattern, the agent UUID is extracted.
            if not any(pattern.match(tag["tag_value"]) for tag in asset["tags"]):
                uuid = asset["tenable_uuid"][0]
                # UUID is formatted with hyphens as it's required by the "agents" API.
                uuid_formatted = '-'.join((uuid[:8],uuid[8:12],uuid[12:16],uuid[16:20],uuid[20:32]))

                try:
                    # Queries the "agents" API for any agents that match the UUID extracted from the asset.
                    # Extracts the name of the group and the asset UUID of the agent.
                    for agent in tio.agents.list(('uuid', 'eq', uuid_formatted)):
                        group_name = agent["groups"][0]["name"]
                        asset_uuid = asset["id"]
                        # Checks if any tag names match the group name in the tag dict.
                        # Assigns the tag uuid if a match is found.
                        tag_uuid = tag_dict.get(group_name)
                        if tag_uuid:

                            try:
                                # Assigns a tag to the asset that matches the group name.
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
