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

  VERSION = "0.95"

  def __init__(self,options):
    """ initialization """

    self.options    = options
    self.parser     = configparser.RawConfigParser(inline_comment_prefixes=(';',))
    self.parser.optionxform = str
    self.parser.read('/etc/pi-webradio.conf')

    self.read_config(options)
    self._store = os.path.join(os.path.expanduser("~"),".pi-webradio.json")

    self._threads    = []                   # thread-store
    self.stop_event  = threading.Event()

    # create API-object and register our own functions
    self.api = Api(self)
    self.register_apis()

    # create all objects
    if options.do_record:
      self._events  = RadioEvents(self)
      self.backend  = None
      self.radio    = Radio(self)
      self.recorder = Recorder(self)
      self._objects = [self,self.radio,self.recorder]
    elif options.do_play:
      self._events  = RadioEvents(self)
      self.backend  = Mpg123(self)
      self.radio    = Radio(self)
      self.player   = Player(self)
      self._objects = [self,self.radio,self.player,self.backend]
    elif options.do_list:
      self.backend  = None
      self.radio    = Radio(self)
      self._objects = [self,self.radio]
    else:
      self._events  = RadioEvents(self)
      self._server  = WebServer(self)
      self.backend  = Mpg123(self)
      self.radio    = Radio(self)
      self.player   = Player(self)
      self.recorder = Recorder(self)
      self._objects = [self,self.radio,self.player,
                       self.recorder,self.backend]
    self._load_state()
    if self.backend:
      self.backend.create()

  # --- read configuration   -------------------------------------------------

  def read_config(self,options):
    """ read configuration from config-file """

    # section [GLOBAL]
    if options.debug:
      self.debug = True
    else:
      self.debug  = self.get_value(self.parser,"GLOBAL", "debug","0") == "1"

  # --- register APIs   ------------------------------------------------------

  def register_apis(self):
    """ register API-functions """

    self.api.get_version      = self._get_version
    self.api.sys_restart      = self.sys_restart
    self.api.sys_stop         = self.sys_stop
    self.api.sys_reboot       = self.sys_reboot
    self.api.sys_halt         = self.sys_halt

  # --- return version   ---------------------------------------------------

  def _get_version(self):
    """ return version """

    self.msg("WebRadio: version: %s" % WebRadio.VERSION)
    return WebRadio.VERSION

  # --- shutdown system   -----------------------------------------------------

  def sys_halt(self):
    """ shutdown system """

    self.msg("Webradio: processing sys_halt")
    if not self.debug:
      try:
        os.system("sudo /sbin/halt &")
      except:
        pass
    else:
      self.msg("Webradio: no shutdown in debug-mode")
    self.api._push_event({'type': 'sys', 'value': 'halt'})

  # --- reboot system   -----------------------------------------------------

  def sys_reboot(self):
    """ reboot system """

    self.msg("Webradio: processing sys_reboot")
    if not self.debug:
      try:
        os.system("sudo /sbin/reboot &")
      except:
        pass
    else:
      self.msg("Webradio: no reboot in debug-mode")
    self.api._push_event({'type': 'sys', 'value': 'reboot'})

  # --- restart service   -----------------------------------------------------

  def sys_restart(self):
    """ restart service """

    self.msg("Webradio: processing sys_restart")
    if not self.debug:
      try:
        os.system("sudo /bin/systemctl restart pi-webradio.service &")
      except:
        pass
    else:
      self.msg("Webradio: no application restart in debug-mode")
    self.api._push_event({'type': 'sys', 'value': 'restart'})

  # --- stop service   --------------------------------------------------------

  def sys_stop(self):
    """ stop service """

    self.msg("Webradio: processing sys_stop")
    if not self.debug:
      try:
        os.system("sudo /bin/systemctl stop pi-webradio.service &")
      except:
        pass
    else:
      self.msg("Webradio: no application stop in debug-mode")
    self.api._push_event({'type': 'sys', 'value': 'stop'})

  # --- query state of objects and save   -------------------------------------

  def _save_state(self):
    """ query and save state of objects """

    state = {}
    for obj in self._objects:
      state[obj.__module__] = obj.get_persistent_state()

    f = open(self._store,"w")
    self.msg("WebRadio: Saving settings to %s" % self._store)
    json.dump(state,f,indent=2,sort_keys=True)
    f.close()

  # --- load state of objects   -----------------------------------------------

  def _load_state(self):
    """ load state of objects """

    try:
      if not os.path.exists(self._store):
        self._play_mode = False
        return
      self.msg("Webradio: Loading settings from %s" % self._store)
      f = open(self._store,"r")
      state = json.load(f)
      for obj in self._objects:
        if obj.__module__ in state:
          obj.set_persistent_state(state[obj.__module__])
      f.close()
    except:
      self.msg("Webradio: Loading settings failed")
      if self.debug:
        traceback.print_exc()

  # --- setup signal handler   ------------------------------------------------

  def signal_handler(self,_signo, _stack_frame):
    """ signal-handler for clean shutdown """

    self.msg("Webradio: received signal, stopping program ...")
    self.cleanup()

  # --- cleanup of ressources   -----------------------------------------------

  def cleanup(self):
    """ cleanup of ressources """

    if hasattr(self,'backend') and self.backend:
      self.backend.destroy()
    if hasattr(self,'_server') and self._server:
      self._server.stop()
    self.stop_event.set()
    if hasattr(self.api,'rec_stop'):
      self.api.rec_stop()
    map(threading.Thread.join,self._threads)
    self._save_state()
    self.msg("Webradio: ... done stopping program")

  # --- run method   ----------------------------------------------------------

  def run(self):
    """ start all threads and return """

    threading.Thread(target=self._server.run).start()
    self.msg("WebRadio: started web-server")
