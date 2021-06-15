#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Simple radio: implementation of class Recorder
#
# The class Recorder encapsulates the recording functions
#
# Part of this code is inspired by https://github.com/radiorec
# Copyright (C) 2013  Martin Brodbeck <martin@brodbeck-online.de>
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-webradio
#
# -----------------------------------------------------------------------------

import threading, os, datetime, urllib.request
from threading import Thread

from SRBase import Base

class Recorder(Thread,Base):
  """ Recorder-controller """

  RECORD_CHUNK = 65536                 # with 128kbs, this should be around 4s

  def __init__(self,app):
    """ initialization """
    super(Recorder,self).__init__(name="Recorder")

    self._app          = app
    self.rec_stop      = None
    self._rec_channel  = None
    self._rec_start_dt = None

    self.read_config()
    app.register_funcs(self.get_funcs())

  # --- read configuration   --------------------------------------------------

  def read_config(self):
    """ read configuration from config-file """

    # section [GLOBAL]
    self._debug = self.get_value(self._app.parser,"GLOBAL", "debug","0") == "1"

    # section [RECORD]
    if not self._app.options.target_dir is None:
      self._target_dir = self._app.options.target_dir[0]
    else:
      self._target_dir = self.get_value(self._app.parser,"RECORD","dir",
                                        os.path.expanduser("~"))
    if not os.path.exists(self._target_dir):
      os.mkdir(self._target_dir)
    elif not os.path.isdir(self._target_dir):
      print("[ERROR] target-directory for recordings %s is not a directory" %
            self._target_dir)

    if self._app.options.duration:
      self._duration = int(self._app.options.duration)
    else:
      self._duration = int(self.get_value(self._app.parser,"RECORD","duration",60))

  # --- return status of recorder   -------------------------------------------

  def is_recording(self):
    """ return status of recorder """

    return self._rec_start_dt is not None

  # --- record stream   -------------------------------------------------------

  def record_stream(self,channel):
    """ record the given stream """

    self._rec_channel,url = channel
    request = urllib.request.Request(url)
    cur_dt_string = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = "%s%s%s_%s" % (self._target_dir,os.sep,cur_dt_string,
                                                             self._rec_channel)

    content_type = request.get_header('Content-Type')
    if(content_type == 'audio/mpeg'):
      filename += '.mp3'
    elif(content_type == 'application/ogg' or content_type == 'audio/ogg'):
      filename += '.ogg'
    elif(content_type == 'audio/x-mpegurl'):
      url = None
      conn = urllib.request.urlopen(request)
      with conn as stream:
        if not line.startswith('#') and len(line) > 1:
          url = line
          stream.close()
      if url:
        request = urllib.request.Request(url)
        filename += '.mp3'
      else:
        self._debug("could not parse m3u-playlist")
        return
    else:
      self.debug('unknown content type %r. Assuming mp3' % content_type)
      filename += '.mp3'

    with open(filename, "wb") as stream:
      self.debug('recording %s for %d minutes' %
                                              (self._rec_channel,self._duration))
      conn = urllib.request.urlopen(request)
      self._rec_start_dt = datetime.datetime.now()
      while(not self.rec_stop.is_set()):
        stream.write(conn.read(Recorder.RECORD_CHUNK))

    self.debug('recording finished')
    self.rec_stop.set()

  # --- get title for recordings   -------------------------------------------

  def get_title(self):
    """ get title during recordings """

    duration = datetime.datetime.now() - self._rec_start_dt
    duration = int(duration.total_seconds())

    m, s = divmod(duration,60)
    # check if we have to stop recording
    # actually, wie should do this elsewhere, but here we have all
    # the necessary information
    if m >= self._duration and self.rec_stop:
      self.rec_stop.set()
    h, m = divmod(m,60)

    # return either mm:ss or hh:mm
    if h > 0:
      return (self._rec_channel,u"{0:02d}*{1:02d}".format(h,m))
    else:
      return (self._rec_channel,u"{0:02d}*{1:02d}".format(m,s))

  # --- start recording   -----------------------------------------------------

  def start_recording(self,channel):
    """ start recording (argument is [name,url]-list) """

    self.debug("start recording")
    if self.rec_stop is None:
      # no recording ongoing, start it
      self._rec_thread = Thread(target=self.record_stream,args=(channel,))
      self.rec_stop = threading.Event()
      self._rec_thread.start()

  # --- stop recording   ------------------------------------------------------

  def stop_recording(self):
    """ stop recording """

    self.debug("stop recording")
    if self.rec_stop:
      # recording is ongoing, so stop it
      self.rec_stop.set()
      self._rec_thread.join()
      self.rec_stop      = None
      self._rec_start_dt = None

  # --- record for the given duration   ---------------------------------------

  def record(self,channel):
    """ record the given channel (blocks) """

    self.start_recording(channel)
    if not self.rec_stop.wait(60*self._duration):
      self.stop_recording()
