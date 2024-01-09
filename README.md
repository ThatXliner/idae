# Idae

[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![codecov](https://codecov.io/gh/ThatXliner/idae/branch/main/graph/badge.svg)](https://codecov.io/gh/ThatXliner/idae)

[![CI](https://github.com/ThatXliner/idae/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/ThatXliner/idae/actions/workflows/ci.yml)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/idae)](https://pypi.org/project/idae)
[![PyPI](https://img.shields.io/pypi/v/idae)](https://pypi.org/project/idae)
[![PyPI - License](https://img.shields.io/pypi/l/idae)](#license)

> A [PEP 723][] implementation

[PEP 723]: https://peps.python.org/pep-0723/

## Usage

Run like normal Python except that the first argument must be a path to the script.

```
idae example.py
```

The dependency specification within the Python script must be like the following (example from [PEP 723][]):

```python
#!/usr/bin/env idae
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "requests<3",
#   "rich",
# ]
# ///

import requests
from rich.pretty import pprint

resp = requests.get("https://peps.python.org/api/peps.json")
data = resp.json()
pprint([(k, v["title"]) for k, v in data.items()][:10])
```

If you need to pass arguments that look like options for `idae` to the script you want to run, use the standard UNIX convention of `--`. For example, let's say you have a script

```python
# script.py
import sys
print(" ".join(sys.argv[1:]))
```

and you want that script to output `I am --help`. To run it with Idae, use

```
idae script.py -- I am --help
```

## Caveats

- [No logging, or very minimal output reporting](https://github.com/ThatXliner/idae/issues/10)

## How it works

1. Detect script file
2. Detect appropriate Python executable
3. Use [venv][] to create a temporary virtual environment in the [user cache directory][] using the executable detected
4. Find [PEP 723][] `pip` requirements
5. Install them into the virtual environment
6. Run the script within the virtual environment

Run `idae clean` to remove all cached environments to free up space. Environments are cached per set of requirements.

[venv]: https://docs.python.org/3/library/venv.html
[user cache directory]: https://platformdirs.readthedocs.io/en/latest/api.html#cache-directory

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

This project is licensed under the [GNU GPL v3+](https://github.com/ThatXliner/idae/blob/main/LICENSE.txt).

In short, this means you can do anything with it (distribute, modify, sell) but if you were to publish your changes, you must make the source code and build instructions readily available.

If you are a company using this project and want an exception, email me at [thatxliner@gmail.com](mailto:thatxliner@gmail.com) and we can discuss.
