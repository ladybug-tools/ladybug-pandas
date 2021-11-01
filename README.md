[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)

# ladybug-pandas

A ladybug extension powered by pandas

## Installation
```console
pip install ladybug-pandas
```

## QuickStart
```python
import ladybug_pandas as lbp
from ladybug.epw import EPW

epw_path = 'tests/assets/epw/tokyo.epw'

epw = EPW(epw_path)

df = lbp.DataFrame.from_epw(epw)

df_ip = df.ladybug.to_ip()

```

## [API Documentation](http://ladybug-tools.github.io/ladybug-pandas)

You can also find some usage examples in the [examples](https://github.com/ladybug-tools/ladybug-pandas/blob/master/examples) folder of the code repository.


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
