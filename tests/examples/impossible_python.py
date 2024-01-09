#!/usr/bin/env idae
# /// script
# requires-python = ">=69420"
# dependencies = [
#   "requests<3",
#   "rich",
# ]
# ///

import requests
from rich.pretty import pprint

resp = requests.get("https://peps.python.org/api/peps.json")  # noqa:
data = resp.json()
pprint([(k, v["title"]) for k, v in data.items()][:10])
