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

from SRBase import Base
from SRKeypad import Keypad

class Player(Base):
  """ Player-controller """

  def __init__(self,app):
    """ initialization """

    self._app    = app
    self.debug   = app.debug
    app.register_funcs(self.get_funcs())

    self.set_state(False)
    self.read_config()

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

  # --- set state   -----------------------------------------------------------

  def set_state(self,active):
    """ set state of object """

    self._active = active

    if active:
      self._play_start_dt = None
      self._read_recordings()
    else:
      self._play_start_dt = None
      self._rec_index     = None
      self._recordings    = None

  # --- get title-line (1st line of display)   -------------------------------

  def get_title(self):
    """ return title-line (1st line of display) """

    if self._rec_index is None and self._recordings:
      return ("reading","")

    if not self._app.mpg123.is_active():
      self.func_stop_play("_")
      # nothing is playing, show name of current recording
      if self._rec_index is None:
        return ("no recordings","")
      else:
        return (self._channel_name,"")
    else:
      # show progress
      if self._play_pause:
        curtime = self._play_pause_dt - self._play_start_dt
      else:
        curtime = datetime.datetime.now() - self._play_start_dt
      curtime = self._pp_time(int(curtime.total_seconds()))
      time_info = "{0:5.5s}/{1:5.5s}".format(curtime,self._tottime)

      if self._play_pause:
        return ("pause",time_info)
      else:
        return (">>>>",time_info)

  # --- get content for display   -------------------------------------------

  def get_content(self):
    """ return content for display """

    lines=[]

    # check if currently are reading the recordings
    if self._rec_index is None and self._recordings:
      lines.append("recordings ...")
      return lines

    if not self._app.mpg123.is_active():
      # nothing is playing, show current recording
      if self._rec_index is not None:
        lines.append("%s %s" % (self._date,self._time))
    else:
      lines.append(self._channel_name)
      lines.append("%s %s" % (self._date,self._time))
    return lines

  # --- pretty print duration/time   ----------------------------------------

  def _pp_time(self,seconds):
    """ pritty-print time as mm:ss or hh:mm """

    m, s = divmod(seconds,60)
    h, m = divmod(m,60)
    if h > 0:
      return "{0:02d}:{1:02d}".format(h,m)
    else:
      return "{0:02d}:{1:02d}".format(m,s)

  # --- set info-variables of current file   ----------------------------------

  def _set_recinfo(self):
    """ gather info about current recording """

    cur_rec       = self._recordings[self._rec_index]
    total_secs    = int(subprocess.check_output(["mp3info", "-p","%S",cur_rec]))
    self._tottime = self._pp_time(total_secs)

    (_,rec) = os.path.split(cur_rec)                        # remove path
    (rec,_) = os.path.splitext(rec)                         # remove extension
    [date,time,self._channel_name] = rec.split("_")         # and split
    self._date = "%s.%s.%s" % (date[6:8],date[4:6],date[0:4])
    self._time = "%s:%s" % (time[0:2],time[2:4])

  # --- read existing recordings   --------------------------------------------

  def _read_recordings(self):
    """ read recordings from configured directory """

    self.msg("reading recordings")

    self._recordings = []
    for f in os.listdir(self._target_dir):
      rec_file = os.path.join(self._target_dir,f)
      if not os.path.isfile(rec_file):
        continue
      # check extension
      (_,ext) = os.path.splitext(rec_file)
      if ext in [".mp3",".ogg",".wav"]:
        self._recordings.append(rec_file)

    if len(self._recordings):
      self._recordings.sort()
      self._rec_index  = len(self._recordings)-1
      self._set_recinfo()
    else:
      self._rec_index  = None

  # --- toggle play/pause   ---------------------------------------------------

  def func_toggle_play(self,_):
    """ toggle play/pause """

    if not self._app.mpg123.is_active():
      # nothing is playing, so start player
      self.func_play('_')
    elif not self._play_pause:
      # something is playing, so pause now
      self.func_pause('_')
    else:
      # resume from pause
      self.msg("resuming playback")
      self._play_pause = False
      now = datetime.datetime.now()
      self._play_start_dt += (now-self._play_pause_dt)
      self._app.mpg123.resume()

  # --- start playing   -------------------------------------------------------

  def func_play(self,_):
    """ start playing """

    if not self._app.mpg123.is_active():
      if not self._rec_index is None:
        self.msg("starting playback")
        self._play_pause = False
        self._play_start_dt = datetime.datetime.now()
        self._app.mpg123.start(self._recordings[self._rec_index],False)
    elif self._play_pause:
      # resume from pause
      self.msg("resuming playback")
      self._play_pause = False
      now = datetime.datetime.now()
      self._play_start_dt += (now-self._play_pause_dt)
      self._app.mpg123.resume()

  # --- pause playing   -------------------------------------------------------

  def func_pause(self,_):
    """ pause playing """

    if self._app.mpg123.is_active() and  not self._play_pause:
      # something is playing, so pause now
      self.msg("pausing playback")
      self._play_pause = True
      self._app.mpg123.pause()
      self._play_pause_dt = datetime.datetime.now()

  # --- stop playing   --------------------------------------------------------

  def func_stop_play(self,_):
    """ stop playing """

    if self._play_start_dt:
      self.msg("stopping playback")
      self._app.mpg123.stop()
      self._play_start_dt = None

  # --- previous recording   --------------------------------------------------

  def func_prev_recording(self,_):
    """ switch to previous recording """

    if self._app.mpg123.is_active():
      self.msg("playback in progress, ignoring command")
    else:
      self.msg("switch to previous recording")
      if self._rec_index is None:
        return
      else:
        self._rec_index = (self._rec_index-1) % len(self._recordings)
        self.msg("current recording: %s" % self._recordings[self._rec_index])
        self._set_recinfo()

  # --- next recording   ------------------------------------------------------

  def func_next_recording(self,_):
    """ switch to next recording """

    if self._app.mpg123.is_active():
      self.msg("playback in progress, ignoring command")
      self.msg("switch to next recording")
    else:
      if self._rec_index is None:
        return
      else:
        self._rec_index = (self._rec_index+1) % len(self._recordings)
        self.msg("current recording: %s" % self._recordings[self._rec_index])
        self._set_recinfo()

  # --- delete recording   ----------------------------------------------------

  def func_delete_recording(self,_):
    """ delete current recording """

    if self._rec_index is None:
      return
    self.msg("deleting current recording")
    self.func_stop_play('-')
    self.msg("deleting %s" % self._recordings[self._rec_index])
    os.unlink(self._recordings[self._rec_index])
    del self._recordings[self._rec_index]
    if not len(self._recordings):
      self._rec_index = None
    else:
      if self._rec_index > len(self._recordings)-1:
        self._rec_index -= 1
      self._set_recinfo()
