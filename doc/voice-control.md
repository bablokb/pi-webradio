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


Usage
=====

Start the [commandline client](webradio_cli.md) with the option `-v`:

  webradio_cli.py -v -d

The debug-flag is of course optional, but might help.
