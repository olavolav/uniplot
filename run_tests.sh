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

python3 -c "import math; ys = [math.sin(i/20)+i/300 for i in range(600)]; from uniplot import plot; plot(ys, title='Sine wave')"
python3 -c "import math; ys = [[math.sin(i/(10+i/50)) - math.sin(i/100) for i in range(1000)], [math.sin(i/(10+i/50)) - math.sin(i/100) - 1 for i in range(900)]]; from uniplot import plot; plot(ys, title='Double sine wave', legend_labels=['wave', 'wave with offset of 1'])"

echo ""
echo "##############"
echo "# Unit tests #"
echo "##############"

python3 -m pytest
