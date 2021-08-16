pi-webradio.py
==============

The python-script `pi-webradio.py` is the main script providing all
the services of the webradio. After installation, you will find it
in `/usr/local/bin`.

Normally, the script is started by the systemd-service `pi-webradio.service`,
see `/etc/systemd/system/pi-webradio.service`. In this mode, the
script starts a webserver (based on Flask) and waits for incoming
requests.

Besides this normal mode of operation, the script supports a number of
other use-cases.


Debugging
---------

To debug problems, stop the regular systemd-service and start
the script in the foreground:

    pi-webradio.py -d

This will log various messages to standard-error.


Listing Channels
----------------

To get a list of all configured channels, run

    > pi-webradio.py -l
    pi-webradio version 0.91
     1: Bayern 1
     2: Bayern 2
     3: Bayern 3
     4: BR-Klassik
     5: BR24
     6: BR24live
     7: France Musique Baroque
     8: MDR KLASSIK
     9: NDR Kultur
    10: hr2-kultur
    11: SR 2 Kultur
    12: DLF Kultur
    13: Klassik im Konzert
    14: Kulturradio
    15: SWR 2
    16: WDR 3
    17: NDR Info
    18: Bremen Zwei
    19: Ö1

Listing channels is a way to check your channel-file is correct.


Direct Play
-----------

To test an url (e.g. from channel 5), you can run the command

    pi-webradio.py -p 5

Hit CTRL-C to quit. This mode does not start the
webserver and you don't have any additional controls, so it is mainly
useful for testing purposes (correct channel-configuration, correct url).


Recording
---------

The web-gui allows for spontaneous recordings using the record-button
(rightmost button in the first row beneath the logo).

Recordings can also be started from the commandline. The command

    pi-webradio.py -r 4 120

records channel 4 for 120 minutes. You can override the default
target-directory configured in `/etc/pi-webradio.conf` with the
option `-t dir`.

For planned recordings, you should install the package *at* and use
the following command:

    echo "/usr/local/bin/pi-webradio.py -r 4 120" | at 20:00 31.10.21

The at-command accepts various date/time formats, see the manpage
for details. You can plan regular recordings from the crontab or
by defining a systemd-timer.

