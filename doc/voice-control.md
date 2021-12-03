Configuring Voice-Control for Pi-Webradio
=========================================

Voice-Control is based on [Vosk](https://alphacephei.com/vosk/).

Voice recognition and speech-to-text is local, i.e. no cloud-services
are needed. Hardware prerequisites are a microphone and a Raspberry Pi
with armv7-architecture (Vosk does not run on a Pi-Zero).

Vosk has been successfully installed and tested on a Pi3 and a Pi-Zero-2
using [Seeed's ReSpeeker 4-Mic Array for Raspberry Pi](https://wiki.seeedstudio.com/ReSpeaker_4_Mic_Array_for_Raspberry_Pi/)
and
[Waveshare's WM9860-Audio-Hat](http://www.waveshare.com/wiki/WM8960_Audio_HAT) with two microphones. Note that the
latter is very similar to
[Seeed's ReSpeaker 2-Mics Pi-Hat](https://wiki.seeedstudio.com/ReSpeaker_2_Mics_Pi_HAT/).


Installation
============

Install Vosk and download a suitable model:

    sudo pip3 install vosk sounddevice
    wget https://alphacephei.com/kaldi/models/vosk-model-small-de-0.15.zip
    sudo mkdir /usr/local/lib/vosk
    sudo unzip -d /usr/local/lib/vosk vosk-model-small-de-0.15.zip
    sudo ln -s vosk-model-small-de-0.15 /usr/local/lib/vosk/model

There is a helper-script with these commands: just edit the model-name
within `tools/install-vosk` and run it.

Note that the installation of Vosk is necessary where the controller
runs, not where the webradio is installed (but it could of course be
the same physical system).


Configuration
=============

Run

    tools/vosk-map.py /etc/pi-webradio.channels | sudo tee /etc/pi-webradio.vosk

to create the configuration file `/etc/pi-webradio.vosk` from
your channel-list. The file contains a json-structure, please
review it and update as necessary.

You need to configure the path to your model, your microphone device-id
and a dict that maps phrases to api-calls.

    {
      "model": "/usr/local/lib/vosk/model",
      "device_id": 1,
      "api_map": {
        "radio": [
          "_set_cmd_mode"
        ],
        ...
      }
    }

Take special care regarding the "wake-word", which puts the voice-controller
into command-mode. The default is "radio":

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


Activating Voice-Control
========================

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


Usage
=====

To start a voice-command, first use the wake-word (default: "radio").
This puts the controller into command-mode and will mute the radio.
Then say the command, e.g. "channel two".

If the detected phrase is within the api-map, the controller will
pass the api to the api-processor. Otherwise, it will ignore the command.

If you use a ReSpeaker and have configured the LEDController as
described above, the hat will use the following colors:

  - off:   waiting for (next) wake-word
  - blue:  wake-word detected, waiting for command
  - green: valid phrase, executing API
  - red:   invalid phrase
