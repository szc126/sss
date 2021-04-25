#!/usr/bin/env bash
python3 nogeoldae.py /tmp/sdl/no{1,2}/* -c text > /tmp/N.txt
python3 nogeoldae.py /tmp/sdl/no{1,2}/* -c html > /tmp/N.htm; firefox /tmp/N.htm
