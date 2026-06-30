#!/usr/bin/env python3
import os

cmd = 'egrep --with-filename --line-number "def test|class Test" test*.py /dev/null'
print(f"+ {cmd}")
os.system(cmd)
# Note 'pytest --collectonly -q' is slow relatively
