from elasticsearch import Elasticsearch
from elasticsearch import helpers
from pathlib import Path
from dateutil.parser import parse
import re
import glob

es = Elasticsearch()

message_regex = r"^\[(.*?)\]\s(.*?):\s(.*)$"
base_path = "./data/rustle"


def paths_to_messages(paths):
    for path in paths:
        with path.open() as f:
            contents = f.read().splitlines()
        channel = path.stem.split("::")[0]
        for line in contents:
            ts_str, username, text = re.search(message_regex, line).groups()
            ts = parse(ts_str)
            yield {
                "_index": "oversearch",
                "_type": "message",
                "_id": f"{username}-{ts}",
                "_source": {
                    "ts": ts,
                    "channel": channel,
                    "username": username,
                    "text": text,
                },
            }

        with open("cache.txt", "a") as cache:
            cache.write(f"{base_path}/{path.name}\n")


all_paths = glob.glob(f"{base_path}/*.txt")

with open("cache.txt") as cache:
    cache_paths = set(cache.read().splitlines())

paths = [Path(x) for x in all_paths if x not in cache_paths]

print(len(paths))
messages = paths_to_messages(paths)
helpers.bulk(es, messages)
