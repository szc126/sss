#!/usr/bin/env bash
python3 nogeoldae.py /tmp/sdl/no{1,2}/* -c | gedit - &
python3 nogeoldae.py /tmp/sdl/no{1,2}/* -c -p | gedit - &
