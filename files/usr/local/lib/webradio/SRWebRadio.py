#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Pi-Webradio: implementation of class WebRadio
#
# The class WebRadio implements the main application class and serves as model
# and controller (for generic functions)
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-webradio
#
# -----------------------------------------------------------------------------

import os, sys, json, traceback, threading
import configparser

from webradio import *

# --- main application class   ----------------------------------------------

class WebRadio(Base):
  """ main application class """

  def __init__(self,options):
    """ initialization """

    self.options    = options
    self.parser     = configparser.RawConfigParser(inline_comment_prefixes=(';',))
    self.parser.optionxform = str
    self.parser.read('/etc/pi-webradio.conf')

    self.read_config()
    self._store = os.path.join(os.path.expanduser("~"),".pi-webradio.json")

    self._threads    = []                   # thread-store
    self.stop_event  = threading.Event()

    # create API-object and register our own functions
    self.api = Api()
    self.register_apis()

    # create all objects
    if options.do_record:
      self.backend  = None
      self.radio    = Radio(self)
      self.recorder = Recorder(self)
      self._objects = [self,self.radio,self.recorder]
    elif options.do_play:
      self._events  = RadioEvents(self)
      self.backend  = Mpg123(self)
      self.backend.start()
      self.radio    = Radio(self)
      self._objects = [self,self.radio,self.backend]
    elif options.do_list:
      self.backend  = None
      self.radio    = Radio(self)
      self._objects = [self,self.radio]
    else:
      self._events  = RadioEvents(self)
      self.backend  = Mpg123(self)
      self.radio    = Radio(self)
      self.player   = Player(self)
      self.recorder = Recorder(self)
      self._objects = [self,self.radio,self.player,
                       self.recorder,self.backend]
    self._load_state()

  # --- read configuration   -------------------------------------------------

  def read_config(self):
    """ read configuration from config-file """

    # section [GLOBAL]
    self._debug  = self.get_value(self.parser,"GLOBAL", "debug","0") == "1"

  # --- register APIs   ------------------------------------------------------

  def register_apis(self):
    """ register API-functions """

    self.api.sys_restart      = self.sys_restart
    self.api.sys_stop         = self.sys_stop
    self.api.sys_reboot       = self.sys_reboot
    self.api.sys_halt         = self.sys_halt
    self.api.play_mode_start  = self.play_mode_start
    self.api.play_mode_exit   = self.play_mode_exit
    self.api.play_mode_toggle = self.play_mode_toggle

  # --- switch to player mode   -----------------------------------------------

  def play_mode_start(self):
    """ start player mode """

    self.msg("starting player mode")
    self._play_mode = True
    self.api.radio_off()

  # --- exit player mode   ----------------------------------------------------

  def play_mode_exit(self):
    """ stop player mode, start radio mode """

    self.msg("stopping player mode")
    self._play_mode = False
    self.api.play_stop()

  # --- exit player mode   ----------------------------------------------------

  def play_mode_toggle(self):
    """ toggle player mode """

    self.msg("processing play_mode_toggle")
    if self._play_mode:
      self.play_mode_exit()
    else:
      self.play_mode_start()

  # --- shutdown system   -----------------------------------------------------

  def sys_halt(self):
    """ shutdown system """

    self.msg("processing sys_halt")
    self.backend.stop()
    if not self._debug:
      try:
        os.system("sudo /sbin/halt &")
      except:
        pass
    else:
      self.msg("no shutdown in debug-mode")

  # --- reboot system   -----------------------------------------------------

  def sys_reboot(self):
    """ reboot system """

    self.msg("processing sys_reboot")
    self.backend.stop()
    if not self._debug:
      try:
        os.system("sudo /sbin/reboot &")
      except:
        pass
    else:
      self.msg("no reboot in debug-mode")

  # --- restart service   -----------------------------------------------------

  def sys_restart(self):
    """ restart service """

    self.msg("processing sys_restart")
    self.backend.stop()
    if not self._debug:
      try:
        os.system("sudo /bin/systemctl restart pi-webradio.service &")
      except:
        pass
    else:
      self.msg("no restart in debug-mode")

  # --- stop service   --------------------------------------------------------

  def sys_stop(self):
    """ stop service """

    self.msg("processing sys_stop")
    self.backend.stop()
    if not self._debug:
      try:
        os.system("sudo /bin/systemctl stop pi-webradio.service &")
      except:
        pass
    else:
      self.msg("no restart in debug-mode")

  # --- query state of objects and save   -------------------------------------

  def _save_state(self):
    """ query and save state of objects """

    state = {}
    for obj in self._objects:
      state[obj.__module__] = obj.get_persistent_state()

    f = open(self._store,"w")
    self.msg("Saving settings to %s" % self._store)
    json.dump(state,f,indent=2,sort_keys=True)
    f.close()

  # --- load state of objects   -----------------------------------------------

  def _load_state(self):
    """ load state of objects """

    try:
      if not os.path.exists(self._store):
        self._play_mode = False
        return
      self.msg("Loading settings from %s" % self._store)
      f = open(self._store,"r")
      state = json.load(f)
      for obj in self._objects:
        if obj.__module__ in state:
          obj.set_persistent_state(state[obj.__module__])
      f.close()
    except:
      self.msg("Loading settings failed")
      if self._debug:
        traceback.print_exc()

  # --- setup signal handler   ------------------------------------------------

  def signal_handler(self,_signo, _stack_frame):
    """ signal-handler for clean shutdown """

    self.msg("received signal, stopping program ...")
    if hasattr(self,'backend') and self.backend:
      self.backend.stop()
    self.stop_event.set()
    if hasattr(self.api,'rec_stop'):
      self.api.rec_stop()
    map(threading.Thread.join,self._threads)
    self._save_state()
    self.msg("... done stopping program")

  # --- run method   ----------------------------------------------------------

  def run(self):
    """ start all threads and return """
    pass
