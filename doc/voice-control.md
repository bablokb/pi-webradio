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

There is a helper-script with these commands: just edit the model-name
within `tools/install-vosk` and run it.


Configuration
=============

Run

    tools/vosk-map.py /etc/pi-webradio.channels | sudo tee /etc/pi-webradio.vosk

to create the configuration file `/etc/pi-webradio.vosk` from
your channel-list. The file contains a json-structure, please
review it and update as necessary.

You need to configure the path to your model, your microphone device-id
and a dict that maps phrases to api-calls.

You can pass `-L en` to `tools/vosk-map.py` to create an English map.
Pull requests for additional languages are welcome, you mainly have
to provide a word-list (`tools/word_map_xx.py`) and update
`tools/vosk-map.py` to include it.


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

The debug-flag is of course optional, but might help. Vosk will for
example tell you about words it does not have in the given language
model.

You can also pass the options `-H host -P port` if the webradio runs
on a remote system.

To automatically start the voice-controller at startup, run

    sudo systemctl enable pi-webradio-vosk.service

The service just starts the commandline client with the option `-v`
as shown above.
