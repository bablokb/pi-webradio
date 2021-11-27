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

class VoskController(Base):
  """ map words phrases to api-calls """

  TIMEOUT = 5             # check stop-event every x seconds

  # --- builtin-word-map   ---------------------------------------------------

  # TODO: move to /etc/.pi-webradio.vosk.json
  WORDMAP = {
    "an":             ["radio_on"],
    "aus":            ["radio_off"],
    "lauter":         ["vol_up"],
    "leiser":         ["vol_down"],
    "kanal eins":     ["radio_play_channel", "nr=1"],
    "kanal zwei":     ["radio_play_channel", "nr=2"],
    "kanal drei":     ["radio_play_channel", "nr=3"],
    "kanal vier":     ["radio_play_channel", "nr=4"],
    "br klassik":     ["radio_play_channel", "nr=4"],
    "kanal fünf":     ["radio_play_channel", "nr=5"],
    "kanal sechs":    ["radio_play_channel", "nr=6"],
    "kanal sieben":   ["radio_play_channel", "nr=7"],
    "kanal acht":     ["radio_play_channel", "nr=8"],
    "kanal neun":     ["radio_play_channel", "nr=9"],
    "kanal siebzehn": ["radio_play_channel", "nr=17"],
    "ndr info":       ["radio_play_channel", "nr=17"],
    "stop":           ["sys_stop"],
    "ende":           ["_quit"],
    "radio":          ["_set_cmd_mode"]
    }

  # --- constructor   --------------------------------------------------------

  def __init__(self,stop,pgm_dir,debug=False):
    """ constructor """

    self._stop        = stop
    self.debug        = debug
    self._audio_queue = queue.Queue()
    self._wmap        = VoskController.WORDMAP
    self._model       = os.path.join(pgm_dir,"..","lib","vosk","model")
    self._device_id   = 1
    self._cmd_mode    = False

    if self.debug:
      vosk.SetLogLevel(0)   # AssertFailed:-3,Error:-2,Warning:-1,Info:0
    else:
      vosk.SetLogLevel(-2)  # AssertFailed:-3,Error:-2,Warning:-1,Info:0

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
                                   json.dumps(list(self._wmap.keys())))
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
                self._set_cmd_mode(True)
              elif self._cmd_mode:
                # ... and only if in command-mode
                yield self._wmap[phrase]
                self._set_cmd_mode(False)
              else:
                self.msg("VoskController: not in command-mode, ignoring %s" % phrase)
            elif len(phrase):
              # non-empty, but unknown command, so clear command-mode
              self.msg("VoskController: unknown phrase")
              self._set_cmd_mode(False)
    except GeneratorExit:
      pass
    except:
      traceback.print_exc()
