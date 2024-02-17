#!/bin/zsh

# Script to run all tests, like a local CI pipeline

set -e

echo "##############"
echo "# Code style #"
echo "##############"

black uniplot/**/*.py tests/**/*.py scripts/*.py

echo ""
echo "##############"
echo "# Type check #"
echo "##############"

mypy --namespace-packages uniplot/**/*.py tests/**/*.py

echo ""
echo "################"
echo "# Visual check #"
echo "################"

python3 -c "import math; ys = [math.sin(i/20)+i/300 for i in range(600)]; from uniplot import plot; plot(ys, title='Sine wave')"
python3 -c "import math; ys = [[math.sin(i/(10+i/50)) - math.sin(i/100) for i in range(1000)], [math.sin(i/(10+i/50)) - math.sin(i/100) - 1 for i in range(900)]]; from uniplot import plot; plot(ys, lines=True, x_unit='s', title='Double sine wave')"
python3 -c "import math; ys = [[math.sin(i/(10+i/50)) - math.sin(i/100) for i in range(1000)], [math.sin(i/(10+i/50)) - math.sin(i/100) - 1 for i in range(900)]]; from uniplot import histogram; histogram(ys, title='Histograms of the above', legend_labels=['wave', 'wave with offset of 1'])"
python3 -c "import math; import numpy as np; dates =  np.arange('2002-10-27T04:30', 4*60, 60, dtype='M8[m]'); from uniplot import plot; plot(xs=dates, ys=[1,2,3,2], x_min=dates[0], x_max=dates[-1], title='Plotting time series with set bounds')"
python3 -c "import math; import numpy as np; dates =  np.arange('2002-10-27T04:30', 4*60, 60, dtype='M8[m]'); from uniplot import plot; plot(xs=dates, ys=[1,2,3,2], title='Plotting time series with auto bounds')"

echo ""
echo "##############"
echo "# Unit tests #"
echo "##############"

python3 -m pytest tests/
