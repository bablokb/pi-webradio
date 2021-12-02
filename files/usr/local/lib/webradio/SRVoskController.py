#!/usr/bin/python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Pi-Webradio: implementation of class VoskController
#
# The class VoskController maps words/phrases to api-calls
# using speech-recognition with Vosk (https://alphacephei.com/vosk/).
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-webradio
#
# ----------------------------------------------------------------------------

import os, sys, queue, json, traceback, vosk, sounddevice as sd

from webradio import Base

have_LEDs = False
try:
  import webradio.LEDController as LEDController
  have_LEDs = True
except:
  pass

class VoskController(Base):
  """ map words phrases to api-calls """

  CONFIG_FILE = "/etc/pi-webradio.vosk"

  # --- constructor   --------------------------------------------------------

  def __init__(self,stop,debug=False):
    """ constructor """

    self._stop        = stop
    self.debug        = debug
    self._audio_queue = queue.Queue()
    self._cmd_mode    = False

    if self.debug:
      vosk.SetLogLevel(0)   # AssertFailed:-3,Error:-2,Warning:-1,Info:0
    else:
      vosk.SetLogLevel(-2)  # AssertFailed:-3,Error:-2,Warning:-1,Info:0

    if have_LEDs:
      self._leds = LEDController.LEDController()

    self._read_config()

  # --- read vosk-configuration   --------------------------------------------

  def _read_config(self):
    """ read vosk-configuration """

    self._model       = '/usr/local/lib/vosk/model'
    self._device_id   = 1
    self._wmap        = {
      "an":             ["radio_on"],
      "aus":            ["radio_off"],
      "lauter":         ["vol_up"],
      "leiser":         ["vol_down"],
      "kanal eins":     ["radio_play_channel", "nr=1"],
      "stop":           ["sys_stop"],
      "ende":           ["_quit"],
      "radio":          ["_set_cmd_mode"]
      }

    try:
      self.msg("VoskController: reading vosk-config from %s" %
                                                   VoskController.CONFIG_FILE)
      f = open(VoskController.CONFIG_FILE,"r")
      vosk_config = json.load(f)
      f.close()

      if "model" in vosk_config:
        self._model = vosk_config["model"]
      if "device_id" in vosk_config:
        self._device_id = vosk_config["device_id"]
      if "api_map" in vosk_config:
        self._wmap = vosk_config["api_map"]

    except:
      self.msg("VoskController: loading configuration failed, using defaults")
      if self.debug:
        traceback.print_exc()

  # --- set command-mode   ---------------------------------------------------

  def _set_cmd_mode(self,mode):
    """ toggle command-mode """

    self._cmd_mode = mode
    self.msg("VoskController: command-mode set to: '%r'" % self._cmd_mode)

  # --- process audio-block   ------------------------------------------------

  def _process_audio_block(self,indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""

    if status:
      self.msg("VoskController: status %s" % status)
    if self._stop.is_set():
      self._audio_queue.put(None)
    else:
      self._audio_queue.put(bytes(indata))

  # --- hook for active command-mode   ---------------------------------------

  def _on_active(self):
    """ active mode is set to on """

    self._set_cmd_mode(True)
    if have_LEDs:
      self._leds.active()

  # --- hook for inactive command-mode   -------------------------------------

  def _on_inactive(self):
    """ active mode is set to off """

    self._set_cmd_mode(False)
    if have_LEDs:
      self._leds.inactive()

  # --- hook for successful command   ----------------------------------------

  def _on_success(self):
    """ command executed successfully """

    if have_LEDs:
      self._leds.success()

  # --- hook for unknown command   -------------------------------------------

  def _on_unknown(self):
    """ command unknown """

    self._set_cmd_mode(False)
    if have_LEDs:
      self._leds.unknown()

  # --- yield api from detected words/phrases   ------------------------------

  def api_from_key(self):
    """ monitor voice-events and yield mapped API-name """

    dev_info = sd.query_devices(self._device_id, 'input')
    rate     = int(dev_info['default_samplerate'])
    model    = vosk.Model(self._model)

    try:
      with sd.RawInputStream(samplerate=rate,
                             blocksize = 8000,
                             device=self._device_id,
                             dtype='int16',
                             channels=1,
                             callback=self._process_audio_block):

        rec = vosk.KaldiRecognizer(model,rate,
                   json.dumps(list(self._wmap.keys()),ensure_ascii=False))

        # signal ready ...
        self._on_active()
        self._on_inactive()

        # ... and listen
        while True:
          data = self._audio_queue.get()
          if not data:
            break
          if rec.AcceptWaveform(data):
            phrase = json.loads(rec.FinalResult())['text']
            self.msg("VoskController: phrase: '%s'" % phrase)
            if phrase in self._wmap:
              # only process valid commands ...
              if self._wmap[phrase][0] == "_set_cmd_mode":
                self._on_active()
              elif self._cmd_mode:
                # ... and only if in command-mode
                self._on_success()
                yield self._wmap[phrase]
                self._on_inactive()
              else:
                self.msg("VoskController: not in command-mode, ignoring %s" %
                         phrase)
            elif len(phrase):
              # non-empty, but unknown phrase
              self.msg("VoskController: unknown phrase")
              if self._cmd_mode:
                self._on_unknown()
                self._on_inactive()
    except GeneratorExit:
      pass
    except:
      traceback.print_exc()
