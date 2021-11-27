Configuring Voice-Control for Pi-Webradio
=========================================

Voice-Control is based on [Vosk](https://alphacephei.com/vosk/).
This is currently a highly experimental and unstable feature. 

These notes are for early adopters ready to spent some time to
figure out what to do.


Installation
============

Install Vosk and download a suitable model:

    sudo pip3 install vosk soundfile
    wget https://alphacephei.com/kaldi/models/vosk-model-small-de-0.15.zip
    sudo mkdir /usr/local/lib/vosk
    sudo unzip -d /usr/local/lib/vosk vosk-model-small-de-0.15.zip
    sudo ln -s vosk-model-small-de-0.15 /usr/local/lib/vosk/model


Configuration
=============

Currently inline in `/usr/local/lib/webradio/SRVoskController.py`.
Please keep your copy, every update will overwrite your changes.
Configuration will eventually move to `/etc/pi-webradio.vosk.json`.

You need to configure your microphone device-id and map phrases
to api-calls.


LED-Support
===========

The voice-controller optionally supports LEDs, mainly because
the ReSpeaker-HAT (a microphone-array with four microphones)
from Seeed-Studio has a nice APA102 LED-ring.

There is a sample implementation of the LEDController in the `misc`
directory. If you have a ReSpeaker, copy the relevant files:

    sudo cp  misc/LEDController.py /usr/local/lib/webradio
    sudo cp  misc/apa102.py /usr/local/lib/webradio
    sudo chown root:root /usr/local/lib/webradio/LEDController.py
    sudo chown root:root /usr/local/lib/webradio/apa102.py

Otherwise, you have to provide your own implementation. Note that
the LEDController-class can actually do anything, you are not limited
to LEDs.

The methods of the class `LEDController` are callbacks for certain
events, e.g. when the wakeup-word is detected and the mic waits for
a command, the LED-ring will signal "active".

If you don't have a ReSpeaker and don't provide your own implementation,
then don't copy anything or else you will run into trouble.


Usage
=====

Start the [commandline client](webradio_cli.md) with the option `-v`:

  webradio_cli.py -v -d

The debug-flag is of course optional, but might help.
