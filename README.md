# StoreCrawler
Web crawler gathering store information


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