.PHONY: *

test: format linter type_check visual_check unit_test

help:
	@echo "Available commands:"
	@echo "\ttest format linter type_check visual_check unit_test run_all_examples"

format:
	@echo "##############"
	@echo "# Code style #"
	@echo "##############"
	uv run ruff format
	@echo

linter:
	@echo "##########"
	@echo "# Linter #"
	@echo "##########"
	uv run ruff check
	@echo

type_check:
	@echo "##############"
	@echo "# Type check #"
	@echo "##############"
	uv run mypy --namespace-packages uniplot/**/*.py tests/**/*.py
	@echo

visual_check:
	@echo "################"
	@echo "# Visual check #"
	@echo "################"
	uv run python3 examples/1-basic_plot.py
	uv run python3 examples/2-color_plot.py
	uv run python3 examples/3-histograms.py
	uv run python3 examples/4-time_series.py
	@echo

unit_test:
	@echo "##############"
	@echo "# Unit tests #"
	@echo "##############"
	uv run python3 -m pytest tests/
	@echo

run_all_examples:
	@echo "Running all examples..."
	@for example in examples/*.py; do \
		uv run python3 $$example; \
	done

clean:
	rm -rf dist/