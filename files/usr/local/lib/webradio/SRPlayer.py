#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Pi-Webradio: implementation of class Player
#
# The class Player implements the playback device for existing recordings
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-webradio
#
# -----------------------------------------------------------------------------

import os, datetime, subprocess

from webradio import Base

class Player(Base):
  """ Player-controller """

  _STOP  = 0
  _PLAY  = 1
  _PAUSE = 2

  def __init__(self,app):
    """ initialization """

    self._app     = app
    self.debug    = app.debug
    self._api     = app.api
    self._backend = app.backend

    self._file    = None
    self._state   = Player._STOP

    self.read_config()
    self.register_apis()

  # --- read configuration   --------------------------------------------------

  def read_config(self):
    """ read configuration from config-file """

    # section [PLAYER]
    self._root_dir = self.get_value(self._app.parser,"PLAYER",
                                    "player_root_dir",
                                    os.path.expanduser("~"))
    if not os.path.exists(self._root_dir):
      self.msg("[WARNING] Player: root-directory %s of player does not exist" %
               self._root_dir,True)
      self._root_dir = os.path.expanduser("~")
      self.msg("[WARNING] Player: using %s as fallback" % self._root_dir,True)
    self._root_dir = os.path.abspath(self._root_dir)

    self._def_dir = self.get_value(self._app.parser,"PLAYER",
                                    "player_def_dir",
                                    self._root_dir)
    if not os.path.exists(self._def_dir):
      self.msg("[WARNING] Player: default-directory %s of player does not exist" %
               self._def_dir,True)
      self._def_dir = self._root_dir
      self.msg("[WARNING] Player: using %s as fallback" % self._def_dir,True)
    self._def_dir = os.path.abspath(self._def_dir)

    if not os.path.commonpath([self._root_dir,self._def_dir]) == self._root_dir:
      self.msg("[WARNING] Player: default-directory is not below root-directory",True)
      self._def_dir = self._root_dir
      self.msg("[WARNING] Player: using %s as fallback" % self._def_dir,True)

    self._dir = self._def_dir
    self.msg("Player: root dir:    %s" % self._root_dir)
    self.msg("Player: default dir: %s" % self._def_dir)

  # --- register APIs   ------------------------------------------------------

  def register_apis(self):
    """ register API-functions """

    self._api.player_play_file  = self.player_play_file
    self._api.player_stop       = self.player_stop
    self._api.player_pause      = self.player_pause
    self._api.player_resume     = self.player_resume
    self._api.player_toggle     = self.player_toggle
    self._api.player_select_dir = self.player_select_dir

  # --- return persistent state of this class   -------------------------------

  def get_persistent_state(self):
    """ return persistent state (overrides SRBase.get_pesistent_state()) """
    return {
      'player_dir': self._dir,
      'player_file': self._file
      }

  # --- restore persistent state of this class   ------------------------------

  def set_persistent_state(self,state_map):
    """ restore persistent state (overrides SRBase.set_pesistent_state()) """

    self.msg("Player: restoring persistent state")
    if 'player_dir' in state_map:
      self._dir = state_map['player_dir']
    if 'player_file' in state_map:
      self._file = state_map['player_file']

  # --- pretty print duration/time   ----------------------------------------

  def _pp_time(self,seconds):
    """ pritty-print time as mm:ss or hh:mm """

    m, s = divmod(seconds,60)
    h, m = divmod(m,60)
    if h > 0:
      return "{0:02d}:{1:02d}:{2:02d}".format(h,m,s)
    else:
      return "00:{0:02d}:{1:02d}".format(m,s)

  # --- start playing   -------------------------------------------------------

  def player_play_file(self,fname=None):
    """ start playing """

    if self._state == Player._PLAY:
      self.player_stop()

    if fname:
      if not os.path.isabs(fname):
        fname = os.path.join(self._dir,fname)
      if os.path.exists(fname):
        self._file = fname
      else:
        raise ValueError("filename %s does not exist" % fname)

    self._backend.play(self._file)
    self._state = Player._PLAY
    self._api._push_event({'type': 'play_file', 'value': self._file})
    total_secs = int(subprocess.check_output(["mp3info", "-p","%S",self._file]))
    self._api._push_event({'type': 'file_info',
                           'value': {'name': self._file,
                                     'duration': self._pp_time(total_secs)}})

  # --- stop playing   -------------------------------------------------------

  def player_stop(self):
    """ stop playing (play->stop, pause->stop)"""

    if self._state == Player._STOP:
      return                      # nothing playing
    else:
      self._backend.stop()        # backend will publish eof-event
      self._state = Player._STOP

  # --- pause playing   -----------------------------------------------------

  def player_pause(self):
    """ pause playing (play->pause) """

    if not self._state == Player._PLAY:
      return                      # nothing playing
    else:
      self._backend.pause()
      self._state = Player._PAUSE

  # --- resume playing   ----------------------------------------------------

  def player_resume(self):
    """ resume playing (pause->play) """

    if not self._state == Player._PAUSE:
      return                      # not paused
    else:
      self._backend.resume()
      self._state = Player._PLAY

  # --- toggle playing   ------------------------------------------------------

  def player_toggle(self):
    """ toggle playing (play->pause, pause->play) """

    if self._state == Player._STOP:
      return                      # not paused
    elif self._state == Player._PLAY:
      self.player_pause()
    else:
      self.player_resume()

  # --- select directory, return entries   ------------------------------------

  def player_select_dir(self,dir=None):
    """ select directory """

    result =  {'dirs':  [], 'files': []}
    if not dir:
      dir = self._dir
    else:
      # check path
      dir = os.path.abspath(dir)
      if not os.path.commonpath([self._root_dir,dir]) == self._root_dir:
        self.msg("[WARNING] Player: directory %s is not below root-directory" % dir,True)
        return result
      elif not os.path.isdir(dir):
        self.msg("[WARNING] Player: directory %s does not exist" % dir,True)
        return result
      self._dir = dir

    # iterate over directory ...
    self.msg("Player: collecting dir-info for %s" % dir)
    result['dirs'].append('..')
    for f in os.listdir(dir):
      if os.path.isfile(os.path.join(dir,f)):
        if f.endswith(".mp3"):
          result['files'].append(f)
      else:
        result['dirs'].append(f)

    # ... and sort results
    result['files'].sort()
    result['dirs'].sort()
    return result
