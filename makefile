PYTHON = python

TEST_RUNNER = unittest
TEST_RUNNER_ARGS = discover -v


run:
	$(PYTHON) run.py server

test:
	$(PYTHON) -m $(TEST_RUNNER) $(TEST_RUNNER_ARGS)

populate:
	$(PYTHON) run.py populate
