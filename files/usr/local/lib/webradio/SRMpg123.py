#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Pi-Webradio: implementation of class Mpg123
#
# The class Mpg123 encapsulates the mpg123-process for playing MP3s.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-webradio
#
# -----------------------------------------------------------------------------

import threading, subprocess, signal, os, shlex, re, traceback
from threading import Thread
import queue, collections

from webradio import Base

class Mpg123(Base):
  """ mpg123 control-object """

  def __init__(self,app):
    """ initialization """

    self._app       = app
    self._api       = app.api
    self._process   = None
    self._pause     = False
    self._icy_event = None

    self.icy_data   = None
    self.read_config()

  # --- read configuration   --------------------------------------------------

  def read_config(self):
    """ read configuration from config-file """

    # section [GLOBAL]
    self._debug       = self.get_value(self._app.parser,
                                       "GLOBAL", "debug","0") == "1"

    # section [MPG123]
    self._mpg123_opts = self.get_value(self._app.parser,"MPG123",
                                       "mpg123_opts","-b 1024")

  # --- active-state (return true if playing)   --------------------------------

  def is_active(self):
    """ return active (playing) state """

    return self._process is not None and self._process.poll() is None

  # --- start player in the background in remote-mode   ----------------------

  def start(self):
    """ spawn new mpg123 process """

    args = ["mpg123","-R"]
    opts = shlex.split(self._mpg123_opts)
    args += opts

    self.debug("starting mpg123 with args %r" % (args,))
    # start process with line-buffered stdin/stdout
    self._process = subprocess.Popen(args,bufsize=1,
                                     universal_newlines=True,
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT)
    self._reader_thread = Thread(target=self._process_stdout)
    self._reader_thread.start()

  # --- play URL/file   -------------------------------------------------------

  def play(self,url):
    """ start playing """

    if self._process:
      self.debug("starting to play %s" % url)
      if url.endswith(".m3u"):
        self._process.stdin.write("LOADLIST 0 %s\n" % url)
      else:
        self._process.stdin.write("LOAD %s\n" % url)

  # --- pause playing   -------------------------------------------------------

  def pause(self):
    """ pause playing """

    if self._process:
      self.debug("pausing playback")
      if not self._pause:
        self._process.stdin.write("PAUSE\n")
        self._pause = True

  # --- continue playing   ----------------------------------------------------

  def resume(self):
    """ continue playing """

    if self._process:
      self.debug("continuing playback")
      if self._pause:
        self._process.stdin.write("PAUSE\n")
        self._pause = False

  # --- stop player   ---------------------------------------------------------

  def stop(self):
    """ stop current player """

    if self._process:
      self.debug("stopping mpg123 ...")
      self._process.stdin.write("QUIT\n")

  # --- process output of mpg123   --------------------------------------------

  def _process_stdout(self):
    """ read mpg123-output and process it """

    self.debug("starting mpg123 reader-thread")
    for line in iter(self._process.stdout.readline,''):
      if line.startswith("@F"):
        continue
      else:
        self.debug("mpg123: %s" % line)
    self.debug("stopping mpg123 reader-thread")
