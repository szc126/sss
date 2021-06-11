#!/usr/bin/env bash
python3 jungno.py /tmp/sdl/no{1,2}/* -c text > /tmp/jungno.txt &
python3 jungno.py /tmp/sdl/no{1,2}/* -c html > /tmp/jungno.htm; dragon /tmp/jungno.htm &
