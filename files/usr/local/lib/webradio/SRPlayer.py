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
      self.msg("WARNING: root-directory %s of player does not exist" %
               self._root_dir,True)
      self._root_dir = os.path.expanduser("~")
      self.msg("WARNING: using %s as fallback" % self._root_dir,True)
    self._root_dir = os.path.abspath(self._root_dir)

    self._def_dir = self.get_value(self._app.parser,"PLAYER",
                                    "player_def_dir",
                                    self._root_dir)
    if not os.path.exists(self._def_dir):
      self.msg("WARNING: default-directory %s of player does not exist" %
               self._def_dir,True)
      self._def_dir = self._root_dir
      self.msg("WARNING: using %s as fallback" % self._def_dir,True)
    self._def_dir = os.path.abspath(self._def_dir)

    if not os.path.commonpath([self._root_dir,self._def_dir]) == self._root_dir:
      self.msg("WARNING: default-directory is not below root-directory",True)
      self._def_dir = self._root_dir
      self.msg("WARNING: using %s as fallback" % self._def_dir,True)
    self._dir = self._def_dir

  # --- register APIs   ------------------------------------------------------

  def register_apis(self):
    """ register API-functions """

    self._api.player_play = self.player_play

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

  # --- start playing   -------------------------------------------------------

  def player_play(self,fname=None):
    """ start playing """

    if fname:
      self._file = fname
    total_secs = int(subprocess.check_output(["mp3info", "-p","%S",self._file]))
    self._api._push_event({'type': 'player_play', 'value': self._file})
    self._api._push_event({'type': 'file_info',
                           'value': {'name': self._file,
                                     'duration': total_secs}})
    self._backend.play(self._file)
