# Codecrafters Redis

Solving the [codecrafters redis challenge](https://app.codecrafters.io/courses/redis/overview) in Python.

## Instructions

Simply use make to run server.
```bash
# starts the your_program.sh script.
make
```

We use pipenv to initialize our development environment.

```bash
# install necessary requirements
pipenv install
```

If you don't want to use pipenv, simply read the list of requirements present in the Pipfile and make sure those packages are available on your path.

## Root Structure

```bash
.
├── app # main app directory
├── CODECRAFTERS_README.md
├── codecrafters.yml
├── Makefile
├── Pipfile
├── Pipfile.lock
├── pyproject.toml
├── README.md
├── spawn_replica.sh # run multiple instances of app as 'replicas'
├── tests # tests folder
├── watch.sh # run app as a hot-reload server (requires executable 'entr' in path)
└── your_program.sh # actual script to run app
```

Of note are the folders,
- `app`: Actual logic of the app module which is run as our redis server.
- `tests`: Tests directory that contains unit and integration tests used during development.

## App Directory

```bash
.
├── args.py # parsing of command line arguments
├── commands # handlers for specific redis commands (eg, handlers/get.py handles command GET)
├── config.py # redis server config
├── context.py # context required for execution of commands
├── info # redis server info and stats
├── __init__.py
├── logger.py # logging config
├── main.py # entrypoint
├── pool.py # connection pool
├── __pycache__
├── queue.py # wrapper around python queue (used for redis transactions)
├── replication # logic specific to the server running as a replica
├── resp # Redis Serialization Protocol (RESP)
├── storage # in-memory storage and rdb config
└── utils # utils used by the main app
```

Each sub module within app usually contains some notable files as,
- `base.py`: Contains definitions of abstract base classes, decorators and generics that are used by other files within the submodule.
- `errors.py`: Defines errors that are specific to the submodule.
- `constants.py`: Constants that are declared at a single place to make them reusable.
- `parser.py`: Parsing logic required by the submodule.

## Running Tests

You can use the Makefile to run tests.

```bash
# run unit tests
make unit-test

# run integration tests
make integration-test
```

We use `pytest` for unit tests, make sure it is installed in your environment.

## Contributing

This repo is mostly for self-learning and so I'm not currently accepting any contributions. If you do make a PR, make sure to install pre-commit before making any changes.

```bash
# install pre-commit so linting errors are caught before commit
pre-commit install

# you can also run the hooks manually
pre-commit run --all-files
```
