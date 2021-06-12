#!/usr/bin/env bash

./yeokhae.py /tmp/sdl/yeokhae1/{3..140} /tmp/sdl/yeokhae2/{3..106} -c text > "/tmp/yeokhae.txt"; dragon "/tmp/yeokhae.txt" &
./yeokhae.py /tmp/sdl/yeokhae1/{3..140} /tmp/sdl/yeokhae2/{3..106} -c html > "/tmp/yeokhae.htm"; dragon "/tmp/yeokhae.htm" &
./yeokhae.py /tmp/sdl/yeokhae1/{3..140} /tmp/sdl/yeokhae2/{3..106} -c html -p > "/tmp/yeokhae-p.htm"; dragon "/tmp/yeokhae-p.htm" &
