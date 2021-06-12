#!/usr/bin/env bash

./sss-yeokhae.py /tmp/sdl/yy1/{3..140} /tmp/sdl/yy2/{3..106} -c text > "/tmp/yeokhae.txt"; dragon "/tmp/yeokhae.txt" &
./sss-yeokhae.py /tmp/sdl/yy1/{3..140} /tmp/sdl/yy2/{3..106} -c html > "/tmp/yeokhae.htm"; dragon "/tmp/yeokhae.htm" &
./sss-yeokhae.py /tmp/sdl/yy1/{3..140} /tmp/sdl/yy2/{3..106} -c html -p > "/tmp/yeokhae-p.htm"; dragon "/tmp/yeokhae-p.htm" &
