# make sure you have required permissions to execute the script ./your_program.sh
.PHONY: run
run:
	./your_program.sh

# make sure you activate your virtual environment that contains the package pytest
.PHONY: unit-test
unit-test:
	pipenv run pytest

.PHONY: integration-test
integration-test:
	pipenv run python3 tests/integration_tests/entrypoint.py

