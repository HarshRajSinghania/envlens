.PHONY: help install test lint fmt check demo clean

help:
	@echo "install  editable install"
	@echo "test     unittest suite"
	@echo "lint     ruff + mypy + compileall"
	@echo "check    everything CI runs"
	@echo "demo     run against examples/"

install:
	python3 -m pip install -e ".[dev]"

test:
	python3 -m unittest discover -s tests -v

lint:
	python3 -m compileall -q envlens.py tests
	ruff check .
	ruff format --check .
	mypy envlens.py || true

fmt:
	ruff check --fix .
	ruff format .

check: lint test

demo:
	python3 envlens.py check --example examples/.env.example --actual examples/.env || true
	python3 envlens.py diff examples/.env.example examples/.env || true

clean:
	rm -rf build dist *.egg-info __pycache__ tests/__pycache__ .mypy_cache .ruff_cache
