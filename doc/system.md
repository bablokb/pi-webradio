System configuration
====================

This project has only one real prerequisite: a system which can output audio.
So before installation you should make sure your audio is working
(there are many tutorials available on the net for setting up various
audio configurations).


HDMI-Audio
----------

If you use HDMI only for audio-signals, you should set it up in
`/boot/config.txt` with the following statements:

    dtparam=audio=on

    [HDMI]
    hdmi_group=1
    hdmi_drive=2
    hdmi_force_hotplug=1
    hdmi_ignore_edid=0xa5000080
    hdmi_force_edid_audio=1
    hdmi_ignore_cec_init=1
    config_hdmi_boost=4

Otherwise, if the Pi does not detect a monitor, it will switch to analogue
output. If you are using a Pi4 and want to route audio to a specific
HDMI-socket, you can add a suffix to `[HDMI]`: `[HDMI:0]` or `[HDMI:1]`.

The `hdmi_ignore_cec_init`-statement is only relevant if you connect your
system to a receiver or television and don't want it to turn other
components on or off.


Autostart of the browser
------------------------

In an integrated setup the client (usually a browser) runs
on the same system as the server. To automatically start the client
create a "desktop"-file (e.g. `webradio_chrome.desktop`)
with the following content

    [Desktop Entry]
    Name=Pi-Webradio
    Comment=Webclient (chrome) for Pi-Webradio
    Exec=/usr/local/bin/webradio_chrome.sh
    Terminal=false
    Type=Application
    StartupNotify=false
    X-GNOME-Autostart-enabled=true

and put it into the directory `$HOME/.config/autostart`. This file
is part of the distribution in the `misc`-directory.

The script `/usr/local/bin/webradio_chrome.sh` will start chromium
in application and kiosk mode:

chromium-browser --app=http://localhost:8026/ --kiosk &

After the start it then monitors the systemd-process of pi-webradio.
If that process terminates, the browser is killed as well.


Prevent Screen-Blanking
-----------------------

The script `/usr/local/bin/webradio_chrome.sh` also takes care of
setting options to prevent screen-blanking. Depending on your
display-manager and/or window-manager, you might need to take
additional actions, e.g. to prevent a lock-screen.


Remove Mousepointer
-------------------

To remove the mouse-pointer while being idle, install the package
`unclutter`. If the start-script detects unclutter, it automatically
calls the binary. No additional action is necessary.
