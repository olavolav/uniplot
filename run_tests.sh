#!/bin/bash

# Script to run all tests, like a local CI pipeline

set -e

echo "##############"
echo "# Code style #"
echo "##############"

ruff format uniplot/**/*.py tests/**/*.py scripts/*.py examples/*.py

echo ""
echo "##########"
echo "# Linter #"
echo "##########"

ruff check

echo ""
echo "##############"
echo "# Type check #"
echo "##############"

mypy --namespace-packages uniplot/**/*.py tests/**/*.py

echo ""
echo "################"
echo "# Visual check #"
echo "################"

python3 examples/1-basic_plot.py
python3 examples/2-color_plot.py
python3 examples/3-histograms.py
python3 examples/4-time_series.py

echo ""
echo "##############"
echo "# Unit tests #"
echo "##############"

python3 -m pytest tests/
