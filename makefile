PYTHON = python

TEST_RUNNER = unittest
TEST_RUNNER_ARGS = discover -v

MANAGE_SCRIPT = manage.py


run:
	$(PYTHON) $(MANAGE_SCRIPT) server

test:
	$(PYTHON) -m $(TEST_RUNNER) $(TEST_RUNNER_ARGS)

populate:
	$(PYTHON) $(MANAGE_SCRIPT) populate

clean-db:
	$(PYTHON) $(MANAGE_SCRIPT) clean_database
