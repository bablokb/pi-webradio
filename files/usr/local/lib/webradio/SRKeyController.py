#!/usr/bin/python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Pi-Webradio: implementation of class KeyController
#
# The class KeyController maps key-events to api-calls
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-webradio
#
# ----------------------------------------------------------------------------

import evdev, select
from webradio import Base

class KeyController(Base):
  """ map key-events to api-calls """

  # --- builtin-keymaps   ----------------------------------------------------

  KEYMAP_RADIO = {
    "KEY_LEFT":  "radio_play_prev",
    "KEY_RIGHT": "radio_play_next",
    "KEY_UP":    "vol_up",
    "KEY_DOWN":  "vol_down"
    }

  # --- constructor   --------------------------------------------------------

  def __init__(self,stop,debug=False):
    """ constructor """

    self._stop    = stop
    self._kmap    = KeyController.KEYMAP_RADIO
    self.debug    = debug
    self.msg("KeyController: map: %r" % self._kmap)

  # --- yield api from key-event   -------------------------------------------

  def api_from_key(self):
    """ monitor key-events and yield mapped API-name """

    devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
    devices = {dev.fd: dev for dev in devices}

    self.msg("KeyController: type of kmap: %s" % type(self._kmap))
    while not self._stop.is_set():
      fds, _1, _2 = select.select(devices, [], [])
      for fd in fds:
        for event in devices[fd].read():
          event = evdev.util.categorize(event)
          if (isinstance(event, evdev.events.KeyEvent) and
              event.keystate == event.key_down):
            self.msg("KeyController: processing %s" % event.keycode)
            if event.keycode in self._kmap:
              # key is mapped, yield api-name
              self.msg("KeyController: mapping %s to %s" %
                       (event.keycode,self._kmap[event.keycode]))
              yield self._kmap[event.keycode]
            else:
              # key is not mapped, ignore
              self.msg("KeyController: ignoring %s" % event.keycode)
