# make sure you have required permissions to execute the script ./your_program.sh
.PHONY: run
run:
	./your_program.sh

# make sure you activate your virtual environment that contains the package pytest
.PHONY: test
test:
	pytest
