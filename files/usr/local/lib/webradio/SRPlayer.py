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

  def __init__(self,app):
    """ initialization """

    self._app     = app
    self.debug    = app.debug
    self._api     = app.api
    self._backend = app.backend

    self._file    = None

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
    self._def_dir = os.path.abspath(self._def_dir)
    if not self._check_dir(self._def_dir):
      self._def_dir = self._root_dir
      self.msg("[WARNING] Player: using %s as fallback" % self._root_dir,True)

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
      if not self._check_dir(self._dir):
        self._dir = self._def_dir
    if 'player_file' in state_map:
      self._file = state_map['player_file']
      if self._file and not self._check_file(self._file):
        self._file = None
    self.msg("Player: currrent dir:  %s" % self._dir)
    self.msg("Player: currrent file: %s" % self._file)

  # --- check directory   ---------------------------------------------------

  def _check_dir(self,path):
    """ check if directory is valid """

    path = os.path.abspath(path)
    if not os.path.exists(path):
      self.msg("[WARNING] Player: %s does not exist" % path)
      return False

    if not os.path.commonpath([self._root_dir,path]) == self._root_dir:
      self.msg("[WARNING] Player: %s is not child of root-directory" % path,
               True)
      return False

    return True

  # --- check file   ---------------------------------------------------------

  def _check_file(self,path):
    """ check if file is valid """

    path = os.path.abspath(path)
    if not os.path.exists(path):
      self.msg("[WARNING] Player: %s does not exist" % path)
      return False
    else:
      return self._check_dir(os.path.dirname(path))

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

  def player_play_file(self,file=None):
    """ start playing """

    if file:
      if not os.path.isabs(file):
        file = os.path.join(self._dir,file)
      if not self._check_file(file):
        raise ValueError("invalid filename %s" % file)
      self._file = file

    if not self._file:
      raise ValueError("default file not set")

    self._backend.play(self._file)
    self._api._push_event({'type': 'play_file', 'value': self._file})
    total_secs = int(subprocess.check_output(["mp3info", "-p","%S",self._file]))
    file_info = {'name': self._file,
                 'duration': self._pp_time(total_secs)}
    self._api._push_event({'type': 'file_info', 'value': file_info })
    return file_info

  # --- stop playing   -------------------------------------------------------

  def player_stop(self):
    """ stop playing (play->stop, pause->stop)"""

    self._backend.stop()        # backend will publish eof-event

  # --- pause playing   -----------------------------------------------------

  def player_pause(self):
    """ pause playing (play->pause) """

    self._backend.pause()

  # --- resume playing   ----------------------------------------------------

  def player_resume(self):
    """ resume playing (pause->play) """

    self._backend.resume()

  # --- toggle playing   ------------------------------------------------------

  def player_toggle(self):
    """ toggle playing (play->pause, pause->play) """

    self._backend.toggle()

  # --- select directory, return entries   ------------------------------------

  def player_select_dir(self,dir=None):
    """ select directory """

    result =  {'dirs':  [], 'files': []}
    if not dir:
      # use current directory, keep current file
      dir = self._dir
    else:
      if not os.path.isabs(dir):
        dir = os.path.abspath(os.path.join(self._dir,dir))
      if not self._check_dir(dir):
        raise ValueError("invalid directory %s" % dir)
      # set new current directory, reset current file
      self._dir = dir
      self._file = None

    # publish event (return dir relative to root_dir)
    if self._dir == self._root_dir:
      cur_dir = None
    else:
      cur_dir = self._dir[len(self._root_dir)+1:]
    self._api._push_event({'type':  'dir_select', 'value': cur_dir})

    # iterate over directory ...
    self.msg("Player: collecting dir-info for %s" % dir)
    if self._dir != self._root_dir:
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
