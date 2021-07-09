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

Although the webradio can be controlled from any browser, it is also
possible to implement other clients by just using the web-API directly.

The second part of this project is about building a webradio using a
Waveshare 7.9" touch-display. Here the server-part of the software runs on
the same machine (Raspberry Pi4) as the web-gui.


Installation
------------

To install the software, run

    git clone https://github.com/bablokb/pi-webradio.git
    cd pi-webradio
    sudo tools/install

For non-Debian based systems you need to adapt the installation script.


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


SW-Versions
-----------

The install script installs the current version from the available
repositories (Raspberry Pi or pip).

  - jquery 3.6.0 (<https://jquery.com/download>)
  - Fontawesome-free 5.13.3 (<https://fontawesome.com>)
