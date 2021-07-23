#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Pi-Webradio: implementation of class Recorder
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

from webradio import Base

class Recorder(Thread,Base):
  """ Recorder-controller """

  RECORD_CHUNK = 65536                 # with 128kbs, this should be around 4s

  def __init__(self,app):
    """ initialization """
    super(Recorder,self).__init__(name="Recorder")

    self._app            = app
    self.debug           = app.debug
    self._api            = app.api
    self._rec_thread     = None
    self._rec_stop_event = None
    self._rec_start_dt   = None

    self.read_config()
    self.register_apis()

  # --- read configuration   --------------------------------------------------

  def read_config(self):
    """ read configuration from config-file """

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

  # --- register APIs   ------------------------------------------------------

  def register_apis(self):
    """ register API-functions """

    self._api.rec_start  = self.rec_start
    self._api.rec_stop   = self.rec_stop
    self._api.rec_toggle = self.rec_toggle

  # --- return status of recorder   -------------------------------------------

  def is_recording(self):
    """ return status of recorder """

    return self._rec_start_dt is not None

  # --- record stream   -------------------------------------------------------

  def record_stream(self,channel):
    """ record the given stream """

    name = channel['name']
    url  = channel['url']
    request = urllib.request.Request(url)
    cur_dt_string = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = "%s%s%s_%s" % (self._target_dir,os.sep,cur_dt_string,
                                                             name)

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
        self.msg("Recorder: could not parse m3u-playlist")
        return
    else:
      self.msg('Recorder: unknown content type %r. Assuming mp3' % content_type)
      filename += '.mp3'

    with open(filename, "wb") as stream:
      self.msg('Recorder: recording %s for %d minutes' % (name,self._duration))
      self._api._push_event({'type': 'rec_start',
                             'value': {'name': name,
                                       'duration': self._duration}})
      conn = urllib.request.urlopen(request)
      self._rec_start_dt = datetime.datetime.now()
      while(not self._rec_stop_event.is_set() and
            (datetime.datetime.now()-self._rec_start_dt).total_seconds() <
                                                           60*self._duration):
        stream.write(conn.read(Recorder.RECORD_CHUNK))

    duration = int((datetime.datetime.now()-self._rec_start_dt).total_seconds()/60)
    self.msg('Recorder: recording finished')
    self._api._push_event({'type': 'rec_stop',
                             'value': {'file': filename,
                                       'duration': duration}})
    self._rec_stop_event.set()

  # --- start recording   -----------------------------------------------------

  def rec_start(self,nr=0,sync=False):
    """ start recording (argument is channel number) """

    channel = self._api.radio_get_channel(nr)
    self.msg("Recorder: start recording of channel %d (%s)" %
                                                (channel['nr'],channel['name']))
    if self._rec_stop_event is None:
      # no recording ongoing, start it
      self._rec_stop_event = threading.Event()
      if not sync:
        self._rec_thread = Thread(target=self.record_stream,args=(channel,))
        self._rec_thread.start()
      else:
        self.record_stream(channel)

  # --- stop recording   ------------------------------------------------------

  def rec_stop(self):
    """ stop recording """

    if self._rec_stop_event:
      # recording is ongoing, so stop it
      self.msg("Recorder: stop recording")
      self._rec_stop_event.set()
      if self._rec_thread:
        self._rec_thread.join()
      self._rec_thread     = None
      self._rec_stop_event = None
      self._rec_start_dt   = None

  # --- toggle recording   ----------------------------------------------------

  def rec_toggle(self,nr=0):
    """ toggle recording """

    if self._rec_stop_event:
      # recording is ongoing, so stop it
      self.rec_stop()
    else:
      self.rec_start(nr)
