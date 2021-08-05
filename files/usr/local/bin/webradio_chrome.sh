#!/bin/bash
# --------------------------------------------------------------------------
# This starts chrome in app-mode and connects to the local server.
#
# The script monitors the status of the pi-webradio service and if the
# service terminates it will also kill chrome.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-webradio
#
# --------------------------------------------------------------------------

xset -dpms
xset s off
[ -x /usr/bin/unclutter ] && unclutter &

chromium-browser --app=http://localhost:8026/ --kiosk &
pid_cb="$!"

# monitor systemd-service
while systemctl --quiet is-active pi-webradio.service; do
  sleep 5
done

# kill browser
kill -15 "$pid_cb"
