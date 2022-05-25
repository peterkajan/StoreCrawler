# StoreCrawler
Web crawler gathering information from given online shops. Script reads domains of online stores from input CSV files and list following data to output CSV file:
- email addresses
- facebook links
- twitter links
- store products' titles and images 

**Note that this crawler extracts possibly sensitive data. Use them rationally, legally and ethically (a.k.a. not for SPAM ;))**

## Usage
Script has to be run in proper environment. Therefore, environment must be setup prior to the usage.

### Using Docker
Run script using the following command:
```
docker-compose run -it --rm crawler example_data/stores_small.csv data/output.csv
```

Note that output directory has to be mounted as a volume. Otherwise, the result would not be accessible (-v mounts the volume), e.g.:

```
docker-compose run -it --rm -v $(pwd)/data2:/app/data2 crawler example_data/stores_small.csv data2/output.csv 
```

`data` folder is mounted as volume by default. Input and output files should be kept in this folder.
For more configuration options and further details check script's help:

```
docker-compose run -it --rm crawler -h
```

### In virtual env without Docker
* create a virtual environment
* activate virtual env
* install requirements:
```
pip install -r dev_requirements.txt
```

Run script from commandline, e.g.:
```
./main.py example_data/stores_small.csv output_file.csv
```
For more configuration options and further details check script's help:
```
./main.py --help
```

# Development instructions
Crawler's architecture is described in [docs/Architecture](docs/Architecture.md).

## Tooling
Install pre-commit hooks that run various checks before commit (see pre-commit-config.yaml for details)
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
Check for security issues:
```
bandit .
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