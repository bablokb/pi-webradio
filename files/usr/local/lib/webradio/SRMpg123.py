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
    self.debug      = app.debug
    self._process   = None
    self._pause     = False
    self._icy_event = None

    self.icy_data   = None
    self.read_config()

  # --- read configuration   --------------------------------------------------

  def read_config(self):
    """ read configuration from config-file """

    # section [MPG123]
    self._mpg123_opts = self.get_value(self._app.parser,"MPG123",
                                       "mpg123_opts","-b 1024")

  # --- active-state (return true if playing)   --------------------------------

  def is_active(self):
    """ return active (playing) state """

    return self._process is not None and self._process.poll() is None

  # --- create player in the background in remote-mode   ----------------------

  def create(self):
    """ spawn new mpg123 process """

    args = ["mpg123","-R"]
    opts = shlex.split(self._mpg123_opts)
    args += opts

    self.msg("Mpg123: starting mpg123 with args %r" % (args,))
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
      self.msg("Mpg123: starting to play %s" % url)
      if url.endswith(".m3u"):
        self._process.stdin.write("LOADLIST 0 %s\n" % url)
      else:
        self._process.stdin.write("LOAD %s\n" % url)

  # --- stop playing current URL/file   ---------------------------------------

  def stop(self):
    """ stop playing """

    if self._process:
      self.msg("Mpg123: stopping current url/file")
      self._process.stdin.write("STOP\n")

  # --- pause playing   -------------------------------------------------------

  def pause(self):
    """ pause playing """

    if self._process:
      self.msg("Mpg123: pausing playback")
      if not self._pause:
        self._process.stdin.write("PAUSE\n")
        self._pause = True

  # --- continue playing   ----------------------------------------------------

  def resume(self):
    """ continue playing """

    if self._process:
      self.msg("Mpg123: continuing playback")
      if self._pause:
        self._process.stdin.write("PAUSE\n")
        self._pause = False

  # --- stop player   ---------------------------------------------------------

  def destroy(self):
    """ destroy current player """

    if self._process:
      self.msg("Mpg123: stopping mpg123 ...")
      self._process.stdin.write("QUIT\n")
      try:
        self._process.wait(5)
        self.msg("Mpg123: ... done")
      except TimeoutExpired:
        # can't do anything about it
        self.msg("Mpg123: ... failed stopping mpg123")
        pass

  # --- process output of mpg123   --------------------------------------------

  def _process_stdout(self):
    """ read mpg123-output and process it """

    self.msg("Mpg123: starting mpg123 reader-thread")
    regex = re.compile(r".*ICY-META.*?'([^']*)';?.*\n")
    for line in iter(self._process.stdout.readline,''):
      if line.startswith("@F"):
        continue
      self.msg("Mpg123: processing line: %s" % line)
      if line.startswith("@I ICY-META"):
        (line,_) = regex.subn(r'\1',line)
        self._api._push_event({'type': 'icy-meta',
                              'value': line})
      elif line.startswith("@I ICY-NAME"):
        self._api._push_event({'type': 'icy-name',
                              'value': line[13:].rstrip("\n")})
    self.msg("Mpg123: stopping mpg123 reader-thread")
