#!/bin/bash

rm /tmp/.X99-lock
Xvfb :99 -screen 0 1920x1080x16 &
sleep 2
/squashfs-root/lm-studio --no-sandbox &
sleep 30
/root/.lmstudio/bin/lms server start --cors &
sleep 5
/root/.lmstudio/bin/lms load --gpu max --context-length ${CONTEXT_LENGTH:-4096} ${MODEL_PATH} &
sleep 60
cp -f /http-server-config.json /root/.cache/lm-studio/.internal/http-server-config.json
x11vnc -display :99 -forever -rfbauth /root/.vnc/passwd -quiet -listen 0.0.0.0 -xkb
/bin/bash
