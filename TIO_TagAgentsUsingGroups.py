#!/usr/bin/env python3

from tenable.io import TenableIO
import logging
import os
import re

def generate_dict(tio):
    tag_dict = {}
    for tag in tio.tags.list():
        if pattern.match(tag["value"]):
            tag_dict[tag["value"]] = tag["uuid"]
    return tag_dict

if __name__ == "__main__":

    tio = TenableIO(os.getenv('TENABLEIO_ACCESS_KEY'), os.getenv('TENABLEIO_SECRET_KEY'))

    logging.basicConfig(level=logging.DEBUG)

    pattern = re.compile('REGEX_PLACEHOLDER')

    tag_dict = generate_dict(tio)

    for asset in tio.workbenches.assets(('CATEGORY_PLACEHOLDER', 'CONDITION_PLACEHOLDER', 'TAG_PLACEHOLDER')):
        if not any(pattern.match(tag["tag_value"]) for tag in asset["tags"]):
            uuid = asset["tenable_uuid"][0]
            uuid_formatted = '-'.join((uuid[:8],uuid[8:12],uuid[12:16],uuid[16:20],uuid[20:32]))

            for agent in tio.agents.list(('uuid', 'eq', uuid_formatted)):
                group_name = agent["groups"][0]["name"]
                asset_uuid = asset["id"]
                tag_uuid = tag_dict.get(group_name)
                if tag_uuid:
                    print(asset_uuid)
                    print(tag_uuid)
                    #tio.tags.assign(assets=[asset_uuid], tags=[tag_uuid])
