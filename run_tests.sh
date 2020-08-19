#!/bin/zsh

# Script to run all tests, like a local CI pipeline

set -e

echo "##############"
echo "# Code style #"
echo "##############"

black *.py uniplot/**/*.py tests/**/*.py

echo ""
echo "##############"
echo "# Type check #"
echo "##############"

mypy --namespace-packages *.py uniplot/**/*.py tests/**/*.py

echo ""
echo "################"
echo "# Visual check #"
echo "################"

python3 -c "import math; x = [math.sin(i/20)+i/300 for i in range(600)]; from uniplot.uniplot import plot; plot(x, title=\"Sine wave\")"

echo ""
echo "##############"
echo "# Unit tests #"
echo "##############"

python3 -m pytest
