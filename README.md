Pi-Webradio
===========

This project provides the software for a Linux-based internet-radio. While
it will run on any Linux-system (given that it has a valid sound-output),
the target-hardware is the Raspberry-Pi range.

The software has the following components:

  - mpg123 as the low-level player
  - a set of Python3-classes for control and management
  - a web-API for (remote) control
  - a web GUI
  - a commandline client

Although the webradio can be controlled from any browser, it is also
possible to implement other clients by just using the web-API directly (the
commandline client can be used as an example).

[The second part of this project](case/README.md) is about building a webradio
using a Waveshare 7.9" touch-display. Here the server-part of the software
runs on the same machine (Raspberry Pi4) as the web-gui.


Installation
------------

To install the (server-) software, run

    git clone https://github.com/bablokb/pi-webradio.git
    cd pi-webradio
    sudo tools/install [username]

If you don't supply a username, the service is installed for the
standard user "pi".

For non-Debian based systems you need to adapt the installation script.

To test the installation, you can run the following commands:

    pi-webradio.py -l    # list channels
    pi-webradio.py -p 5  # use CTRL-C to finish
    pi-webradio.py -h    # help

The first should list the currently configured radio-stations, the
second one should play channel 5.

If testing is ok, you should activate the service. Either restart your
system or just start the service with

    sudo systemctl start pi-webradio.service

Once the service is running, you can access the web-interface with the
url `http://<ip-or-hostname>:8026/`. If you installed the service on a
Pi-desktop system, you would use `http://localhost:8026/` from your
browser.

You can install the commandline client (including all necessary prereqs)
with the commands:

    git clone https://github.com/bablokb/pi-webradio.git
    cd pi-webradio
    sudo tools/install-client

See below for usage-hints.


Configuration
-------------

The central configuration-file is `/etc/pi-webradio.conf`. The file
reproduces the defaults. Channels have to be added to the file
`/etc/pi-webradio.channels`. The latter is a json-file, with name,
url, and filename (without path) of the channel-logo. The sample
channel-file distributed with the project contains a number of
radio-stations mainly from Germany.

This project does not distribute any logos for the sample channel list
to prevent any copyright-trouble. Please download the files yourself
and copy them to the `files/usr/local/lib/webradio/web/images` directory
(before installation, afterwards use the same path without the
`file`-prefix). The image-size should be 256x256 pixel.

Finding the correct urls for your favorite radio-stations is not always
simple, there are various portals which can serve as a starting point.
If they don't disclose the url directly, you can always use the
developer-tools of your browser and check all requested urls in the
network-tab.


SW-Versions
-----------

The install script installs the current version from the available
repositories (Raspberry Pi or pip).

  - jquery 3.6.0 (<https://jquery.com/download>)
  - Fontawesome-free 5.13.3 (<https://fontawesome.com>)
