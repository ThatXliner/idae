# Idae

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![codecov](https://codecov.io/gh/ThatXliner/idae/branch/main/graph/badge.svg)](https://codecov.io/gh/ThatXliner/idae)

[![CI](https://github.com/ThatXliner/idae/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/ThatXliner/idae/actions/workflows/ci.yml)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/idae)](https://pypi.org/project/idae)
[![PyPI](https://img.shields.io/pypi/v/idae)](https://pypi.org/project/idae)
[![PyPI - License](https://img.shields.io/pypi/l/idae)](#license)

> A [PEP 772](https://peps.python.org/pep-0722/) implementation

## Usage

Run like normal Python except that the first argument must be a path to the script.

The dependency specification within the Python script must be like the following (example from PEP 772):

```python
# In order to run, this script needs the following 3rd party libraries
#
## Script Dependencies:
##    requests
##    rich

import requests
from rich.pretty import pprint

resp = requests.get("https://peps.python.org/api/peps.json")
data = resp.json()
pprint([(k, v["title"]) for k, v in data.items()][:10])
```

Basically, you specify your dependencies using the following comment format:

```python
## Script Dependencies:
##    dep-1
##    dep-2
##    etc
```

## How it works

1. Detect script file
2. Use [venv](https://docs.python.org/3/library/venv.html) to create a temporary virtual environment named `idae-venv` using the Python executable used to run `idae`
3. Find PEP 772 requirements
4. Install them into the venv
5. Run the script within the venv
6. Delete the venv

## Installation

You can get this project via `pip`

```bash
$ pip install idae
```

But we **highly recommend** you install this project using [pipx](https://pypa.github.io/pipx/)

```bash
$ pipx install idae
```

## Why the name

The scientific name for Pythons is "Pythonidae". I just removed the "Python" and we get "idae".

## License

Copyright © 2021, Bryan Hu

This project is licensed under the [GNU GPL v3+](https://github.com/ThatXliner/idae/blob/main/LICENSE.txt).

In short, this means you can do anything with it (distribute, modify, sell) but if you were to publish your changes, you must make the source code and build instructions readily available.

If you are a company using this project and want an exception, email me at [thatxliner@gmail.com](mailto:thatxliner@gmail.com) and we can discuss.
