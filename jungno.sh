#!/usr/bin/env bash

./jungno.py /tmp/sdl/jungno-{a,b}/* -c text > "/tmp/jungno.txt" &
./jungno.py /tmp/sdl/jungno-{a,b}/* -c html > "/tmp/jungno.htm"; dragon "/tmp/jungno.htm" &
