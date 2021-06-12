#!/usr/bin/env bash

./jungno.py /tmp/sdl/jungno{1..2}/* -c text > "/tmp/jungno.txt" &
./jungno.py /tmp/sdl/jungno{1..2}/* -c html > "/tmp/jungno.htm"; dragon "/tmp/jungno.htm" &
