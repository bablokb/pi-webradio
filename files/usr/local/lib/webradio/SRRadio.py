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

    self._active       = True
    self._channel      = -1                 # current channel index
    self._last_channel = -1                 # last active channel index
    self._name         = ''
    self.stop_event    = app.stop_event
    self._title_toggle = True               # toggle title during recording
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

    #self._api.radio_on            = self.radio_on
    #self._api.radio_off           = self.radio_off
    #self._api.radio_toggle        = self.radio_toggle
    self._api.radio_get_channels   = self.radio_get_channels
    self._api.radio_get_channel    = self.radio_get_channel
    #self._api.radio_play_channel  = self.radio_play_channel
    #self._api.radio_play_next     = self.radio_play_next
    #self._api.radio_play_prev     = self.radio_play_prev

  # --- return persistent state of this class   -------------------------------

  def get_persistent_state(self):
    """ return persistent state (overrides SRBase.get_pesistent_state()) """
    return {
      'channel_index': self._last_channel
      }

  # --- restore persistent state of this class   ------------------------------

  def set_persistent_state(self,state_map):
    """ restore persistent state (overrides SRBase.set_pesistent_state()) """

    self.debug("Radio: restoring persistent state")
    if 'channel_index' in state_map:
      self._last_channel = state_map['channel_index']

  # --- read channels   -------------------------------------------------------

  def read_channels(self):
    """ read channels into a list """

    self._channels = []
    try:
      self.debug("Loading channels from %s" % self._channel_file)
      f = open(self._channel_file,"r")
      self._channels = json.load(f)
      f.close()
    except:
      self.debug("Loading channels failed")
      if self._debug:
        traceback.print_exc()

  # --- get channel info   ----------------------------------------------------

  def radio_get_channel(self,nr):
    """ return info-dict {name,url,logo} for channel nr """

    return self._channels[nr]

  # --- set state   -----------------------------------------------------------

  def set_state(self,active):
    """ set state of object """

    self._active = active

    if active:
      pass
    else:
      self._name    = None
      self._channel = -1

  # --- return active-state of the object   -----------------------------------

  def is_active(self):
    """ return active-state (overrides SRBase.is_active()) """

    return self._active

  # --- get title-line (1st line of display)   -------------------------------

  def get_title(self):
    """ return title-line (1st line of display) """

    now = datetime.datetime.now()
    if self._name and self._app.recorder.is_recording():
      # listening radio and ongoing recording: toggle title-line
      if self._title_toggle:
        self._title_toggle = False
        return self._app.recorder.get_title()      # delegate to recorder
      else:
        self._title_toggle = True
        return (self._name,now.strftime("%H:%M"))  # provide title ourselves
    elif self._name:
      # no recording, just show current channel
      return (self._name,now.strftime("%H:%M"))
    elif self._app.recorder.is_recording():
      # only recording: delegate to recorder
      return self._app.recorder.get_title()
    else:
      # return date + time
      return (now.strftime("%x"),now.strftime("%H:%M"))

  # --- get content for display   -------------------------------------------

  def get_content(self):
    """ read icy-data if available """

    lines = []
    if self._app.mpg123.icy_data:
      while True:
        try:
          line = self._app.mpg123.icy_data.get_nowait()
          self.debug("get_content: line: %s" % line)
          lines.append(line)
        except queue.Empty:
          break
        except:
          if self._debug:
            traceback.print_exc()
          break
    return lines

  # --- return channel-list   ------------------------------------------------

  def radio_get_channels(self):
    """ return complete channel-list """

    return self._channels

  # --- switch channel   ------------------------------------------------------

  def func_switch_channel(self,nr):
    """ switch to given channel """

    nr = int(nr)
    self.debug("switch to channel %d" % nr)
    # check if we have to do anything
    if nr == (self._channel+1):
      self.debug("already on channel %d" % nr)
      return

    # kill current mpg123 process
    self._name = None
    self._channel = -1
    self._app.mpg123.stop()

    self._channel = min(nr-1,len(self._channels)-1)
    self._last_channel = self._channel
    channel_name = self._channels[self._channel][0]
    channel_url  = self._channels[self._channel][1]

    # display name of channel on display
    self._name = channel_name
    self.debug("starting new channel %s" % self._name)
    self._app.mpg123.start(channel_url,True)

  # --- switch to next channel   ----------------------------------------------

  def func_next_channel(self,_):
    """ switch to next channel """

    self.debug("switch to next channel")
    # switch_channel expects a channel-number, while self._channel is
    # a channel index
    if self._channel == -1:
      self.func_switch_channel(1)
    else:
      self.func_switch_channel(1+((self._channel+1) % len(self._channels)))

  # --- switch to previous channel   ------------------------------------------

  def func_prev_channel(self,_):
    """ switch to previous channel """

    self.debug("switch to previous channel")
    # switch_channel expects a channel-number, while self._channel is
    # a channel index
    if self._channel == -1:
      self.func_switch_channel(len(self._channels))
    else:
      self.func_switch_channel(1+((self._channel-1) % len(self._channels)))

  # --- turn radio off   ------------------------------------------------------

  def func_radio_off(self,_):
    """ turn radio off """

    self.debug("turning radio off")
    self._name    = None
    self._channel = -1
    self._app.mpg123.stop()

  # --- turn radio on   -------------------------------------------------------

  def func_radio_on(self,_):
    """ turn radio on """

    if self._channel == -1:
      self.debug("turning radio on")
      # if last_channel is -1, we just switch to the first channel
      self.func_switch_channel(max(self._last_channel,0)+1)
    else:
      self.debug("ignoring command, radio already on")

  # --- toggle recording   ----------------------------------------------------

  def func_toggle_record(self,_):
    """ toggle recording """

    self.debug("toggle recording")

    if self._app.recorder.is_recording():
      self._app.recorder.stop_recording()
    else:
      self._app.recorder.start_recording(self.get_channel(self._channel))
