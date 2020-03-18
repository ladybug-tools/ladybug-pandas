[![Build Status](https://travis-ci.org/ladybug-tools/ladybug-pandas.svg?branch=master)](https://travis-ci.org/ladybug-tools/ladybug-pandas)
[![Coverage Status](https://coveralls.io/repos/github/ladybug-tools/ladybug-pandas/badge.svg?branch=master)](https://coveralls.io/github/ladybug-tools/ladybug-pandas)

[![Python 2.7](https://img.shields.io/badge/python-2.7-green.svg)](https://www.python.org/downloads/release/python-270/) [![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)

# ladybug-pandas

A ladybug extension powered by pandas

## Installation
```console
pip install ladybug-pandas
```

## QuickStart
```python
import ladybug_pandas

```

## [API Documentation](http://ladybug-tools.github.io/ladybug-pandas/docs)

## Local Development
1. Clone this repo locally
```console
git clone git@github.com:ladybug-tools/ladybug-pandas

# or

git clone https://github.com/ladybug-tools/ladybug-pandas
```
2. Install dependencies:
```console
cd ladybug-pandas
pip install -r dev-requirements.txt
pip install -r requirements.txt
```

3. Run Tests:
```console
python -m pytest tests/
```

4. Generate Documentation:
```console
sphinx-apidoc -f -e -d 4 -o ./docs ./ladybug_pandas
sphinx-build -b html ./docs ./docs/_build/docs
```
