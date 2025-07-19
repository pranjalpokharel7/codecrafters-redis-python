#!/usr/bin/bash

# find app -type f -name '*.py' | entr -rs './your_program.sh'
find app -type f -name '*.py' | entr -rs './your_program.sh --dir ./ --dbfilename dump.rdb' 

