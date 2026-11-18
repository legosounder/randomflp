#!/usr/bin/env zsh
DIR="$( cd "$( dirname "${BASH_SOURCE[0]:-${(%):-%x}}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"
python3 "$DIR/random_flp.py"
