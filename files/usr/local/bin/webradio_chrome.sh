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

# prevent screenblanking
xset -dpms
xset s off
[ -x /usr/bin/unclutter ] && unclutter &

# extract port from configuration
if [ -f /etc/pi-webradio.conf ]; then
  PORT=$(sed -ne '/port/s/port[^0-9]*\([0-9]*\).*$/\1/p' /etc/pi-webradio.conf)
else
  PORT=8026
fi

chromium-browser --app=http://localhost:$PORT/ --kiosk &
pid_cb="$!"

# monitor systemd-service
while systemctl --quiet is-active pi-webradio.service; do
  sleep 5
done

# kill browser
kill -15 "$pid_cb"
