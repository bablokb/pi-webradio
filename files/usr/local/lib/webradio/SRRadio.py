#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Pi-Webradio: implementation of class Radio
#
# The class Radio implements the core functionality of the web-radio.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-webradio
#
# -----------------------------------------------------------------------------

import os, time, datetime, shlex, json
import queue, collections
import threading, signal, subprocess, traceback

from webradio import *

class Radio(Base):
  """ Radio-controller """

  def __init__(self,app):
    """ initialization """

    self._app          = app
    self._api          = app.api
    self._backend      = app.backend

    self._channel_nr   = 0                  # current channel number
    self._last_channel = 0                  # last active channel number
    self.stop_event    = app.stop_event
    self.read_config()
    self.register_apis()
    self.read_channels()

  # --- read configuration   --------------------------------------------------

  def read_config(self):
    """ read configuration from config-file """

    # section [GLOBAL]
    self._debug       = self.get_value(self._app.parser,"GLOBAL", "debug","0") == "1"
    default_path        = "/etc/pi-webradio.channels"
    self._channel_file  = self.get_value(self._app.parser,"GLOBAL","channel_file",
                                         default_path)

  # --- register APIs   ------------------------------------------------------

  def register_apis(self):
    """ register API-functions """

    self._api.radio_on             = self.radio_on
    self._api.radio_off            = self.radio_off
    self._api.radio_toggle         = self.radio_toggle
    self._api.radio_get_channels   = self.radio_get_channels
    self._api.radio_get_channel    = self.radio_get_channel
    self._api.radio_play_channel   = self.radio_play_channel
    self._api.radio_play_next      = self.radio_play_next
    self._api.radio_play_prev      = self.radio_play_prev

  # --- return persistent state of this class   -------------------------------

  def get_persistent_state(self):
    """ return persistent state (overrides SRBase.get_pesistent_state()) """
    return {
      'channel_nr': self._last_channel
      }

  # --- restore persistent state of this class   ------------------------------

  def set_persistent_state(self,state_map):
    """ restore persistent state (overrides SRBase.set_pesistent_state()) """

    self.msg("Radio: restoring persistent state")
    if 'channel_nr' in state_map:
      self._last_channel = state_map['channel_nr']

  # --- read channels   -------------------------------------------------------

  def read_channels(self):
    """ read channels into a list """

    self._channels = []
    try:
      self.msg("Loading channels from %s" % self._channel_file)
      f = open(self._channel_file,"r")
      self._channels = json.load(f)
      f.close()
    except:
      self.msg("Loading channels failed")
      if self._debug:
        traceback.print_exc()

  # --- get channel info   ----------------------------------------------------

  def radio_get_channel(self,nr):
    """ return info-dict {name,url,logo} for channel nr """

    return self._channels[int(nr-1)]

  # --- return channel-list   ------------------------------------------------

  def radio_get_channels(self):
    """ return complete channel-list """

    return self._channels

  # --- play given channel   --------------------------------------------------

  def radio_play_channel(self,nr=0):
    """ switch to given channel """

    if nr == 0:
      if self._last_channel == 0:
        nr = 1
      else:
        nr = self._last_channel

    channel = self._api.radio_get_channel(nr)
    self.msg("start playing channel %d (%s)" % (nr,channel['name']))

    # check if we have to do anything
    if nr == self._channel_nr:
      self.msg("already on channel %d" % nr)
      return
    else:
      self._api.push_event({'type': 'radio_play_channel', 'value': channel})
      self._channel_nr   = nr
      self._last_channel = self._channel_nr
      channel = self.radio_get_channel(nr)
      self._backend.play(channel['url'])

  # --- switch to next channel   ----------------------------------------------

  def radio_play_next(self):
    """ switch to next channel """

    self.msg("switch to next channel")
    if self._channel_nr == 0:
      self.radio_play_channel(1)
    elif self._channel_nr == len(self._channels):
      self.radio_play_channel(1)
    else:
      self.radio_play_channel(1+self._channel_nr)

  # --- switch to previous channel   ------------------------------------------


  def radio_play_prev(self):
    """ switch to previous channel """

    self.msg("switch to previous channel")
    if self._channel_nr <= 1:
      self.radio_play_channel(len(self._channels))
    else:
      self.radio_play_channel(self._channel_nr-1)

  # --- turn radio off   ------------------------------------------------------

  def radio_off(self):
    """ turn radio off """

    self.msg("turning radio off")
    self._channel_nr = 0
    self._backend.stop()

  # --- turn radio on   -------------------------------------------------------

  def radio_on(self):
    """ turn radio on """

    if self._channel_nr == 0:
      self.msg("turning radio on")
      self.radio_play_channel()
    else:
      self.msg("ignoring command, radio already on")

  # --- toggle radio state   --------------------------------------------------

  def radio_toggle(self):
    """ toggle radio state """

    if self._channel_nr == 0:
      self.radio_on()
    else:
      self.radio_off()
