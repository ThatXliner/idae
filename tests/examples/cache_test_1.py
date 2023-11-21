#!/usr/bin/env idae
# /// pyproject
# [run]
# dependencies = [
#   "beautifulsoup4==4.12.2",
# ]
# ///
from bs4 import BeautifulSoup

print(BeautifulSoup("<h1>Hello world</h1>"))
