# StoreCrawler
Web crawler gathering store information.

Script reads domains of online stores from input CSV files and list following data to output CSV file:
- email addresses
- facebook links
- twitter links
- store products' titles and images 

**Note that this crawler extracts possibly sensitive data. Use them rationally, legally and ethically (a.k.a. not for SPAM ;))**

## Usage
Script can be run from commandline, e.g.:
```
./main.py example_data/stores_small.csv output_file.csv
```
For more details and/or listing configurable attributes use:
```
./main.py --help
```

# Development instructions
## Environment setup
### In virtual env without Docker
* create a virtual environment
* activate virtual env

* install requirements
```
pip install -r dev_requirements.txt
```

## Tooling
Install precommit hooks that run various checks before commit
```
pre-commit install
```
Run linter checks
```
flake8
```
Run tests
```
pytest
```

Note that `pytest-testmon` plugin is used by default. To run tests with coverage report use
```
./pytest-with-cov
```
script from the project root.

Run myPy (type checks)
```
mypy .
```
Run code formatting
```
black .
```

## Updating dependencies
Pip-tools are used for dependency management. To update dependencies run
```
pip-compile --upgrade dev_requirements.in
pip-compile --upgrade requirements.in
```
And to install updated packages run
```
pip-sync dev_requirements.txt
```