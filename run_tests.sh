#!/bin/zsh

# Script to run all tests, like a local CI pipeline

set -e

echo "##############"
echo "# Code style #"
echo "##############"

black **/*.py

echo ""
echo "##############"
echo "# Type check #"
echo "##############"

mypy --namespace-packages **/*.py

echo ""
echo "##############"
echo "# Unit tests #"
echo "##############"

python3 -m unittest
