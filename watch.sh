#!/usr/bin/bash

# run server continuously
find app -type f -name '*.py' | entr -rs './your_program.sh --dir ./ --dbfilename dump.rdb'
