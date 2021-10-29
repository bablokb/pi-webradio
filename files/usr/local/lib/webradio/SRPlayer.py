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

import os, datetime, subprocess, threading, copy, queue

from webradio import Base

class Player(Base):
  """ Player-controller """

  def __init__(self,app):
    """ initialization """

    self._app     = app
    self.debug    = app.debug
    self._api     = app.api
    self._backend = app.backend

    self._lock    = threading.Lock()
    self._file    = None
    self._dirinfo = None
    self._dirplay = None
    self._dirstop = threading.Event()

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
    self._api.player_play_dir   = self.player_play_dir
    self._api._player_get_cover_file = self._player_get_cover_file

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
    self._api.update_state(section="player",key="last_dir",
                           value=self._dir[len(self._root_dir):]+os.path.sep,
                           publish=False)

    self._get_dirinfo(self._dir)
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
      return "{0:02d}:{1:02d}".format(m,s)

  # --- start playing   -------------------------------------------------------

  def player_play_file(self,file=None,last=True):
    """ start playing """

    if file:
      if not os.path.isabs(file):
        file = os.path.join(self._dir,file)
      if not self._check_file(file):
        raise ValueError("invalid filename %s" % file)
      self._file = file

    if not self._file:
      raise ValueError("default file not set")

    if self._dirinfo:
      self._dirinfo['cur_file'] = self._file

    # this will push the information to all clients, even if the file
    # is already playing.
    # We might also need to push the elapsed time?!

    total_secs = int(subprocess.check_output(["mp3info", "-p","%S",self._file]))
    file_info = {'name': os.path.basename(self._file),
                 'duration': self._pp_time(total_secs),
                 'last': last}
    self._api._push_event({'type': 'file_info', 'value': file_info })
    if self._backend.play(self._file,last):
      self._api.update_state(section="player",key="last_file",
                             value=os.path.basename(self._file),publish=False)
    return file_info

  # --- stop playing   -------------------------------------------------------

  def player_stop(self):
    """ stop playing (play->stop, pause->stop)"""

    if self._dirplay:
      self._dirstop.set()         # this will also stop the backend
      self._dirplay.join()
    else:
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
    """ select directory:
        a directory starting with a / is always interpreted relative
        to root_dir, otherwise relative to the current directory
    """

    self._lock.acquire()

    if not dir:
      # use current directory, keep current file
      dir = self._dir
    else:
      if os.path.isabs(dir):
        dir = os.path.normpath(self._root_dir+dir)   # cannot use join here!
        self.msg("Player: dir is absolute, fullpath %s" % dir)
      else:
        dir = os.path.normpath(os.path.join(self._dir,dir))
        self.msg("Player: dir is relative, fullpath %s" % dir)
      if not self._check_dir(dir):
        self._lock.release()
        raise ValueError("invalid directory %s" % dir)

    cache_valid = False
    if dir == self._dir:
      if self._dirinfo:
        cache_valid = True
    else:
      # set new current directory
      self._dir = dir

    # publish event first (return dir relative to root_dir)
    cur_dir = self._dir[len(self._root_dir):]+os.path.sep
    self._api._push_event({'type':  'dir_select', 'value': cur_dir})
    self._api.update_state(section="player",key="last_dir",
                           value=cur_dir,
                           publish=False)

    # then query new directory info
    if not cache_valid:
      self._get_dirinfo(dir)
      self._dirinfo['cur_dir'] = cur_dir
    else:
      self.msg("Player: using cached dir-info for %s" % dir)

    self._lock.release()
    return self._dirinfo

  # --- play all files in directory   -----------------------------------------

  def player_play_dir(self,start=None):
    """ play all files in the current directory starting with
        the given file
    """

    # check existing player-thread, stop it and wait until it is finished
    if self._dirplay:
      self._dirstop.set()
      self._dirplay.join()

    # copy file-list
    if not start:
      files = copy.deepcopy(self._dirinfo['files'])
    else:
      try:
        index = self._dirinfo['files'].index(start)
        self.msg("Player: starting play_dir with file %s (index %i)" %
                 (start,index))
        files = copy.deepcopy(self._dirinfo['files'][index:])
      except ValueError:
        raise ValueError("file %s does not exist" % start)

    # start player-thread, pass files as argument
    self._dirstop.clear()
    self._dirplay = threading.Thread(target=self._play_dir,args=(files,))
    self._dirplay.start()

  # --- play all files (helper)   --------------------------------------------

  def _play_dir(self,files):
    """ play all given files """

    ev_queue = self._api._add_consumer("_play_dir")
    do_exit = False

    index_last = len(files)-1
    for index,fname in enumerate(files):
      if do_exit:
        break
      self.msg("Player: _play_dir: playing next file %s" % fname)
      self.player_play_file(fname,last=index==index_last)
      while True:
        # a naive implementation would just block on the queue, but
        # then we could stop this thread only after an event occurs
        if self._dirstop.wait(timeout=1.0):
          do_exit = True
          break
        try:
          ev = ev_queue.get(block=False)
          ev_queue.task_done()
          if ev:
            if ev['type'] == 'eof' and ev['value']['name'] == fname:
              self.msg("Player: processing eof for %s" % fname)
              break                              # start next file
          else:
            do_exit = True
            break
        except queue.Empty:
          pass

    # cleanup
    self.msg("Player: stopping _play_dir and cleaning up")
    self._api._del_consumer("_play_dir")
    self._backend.stop()
    self._dirplay = None

  # --- return name of cover file (currently only cover.jpg)   ---------------

  def _player_get_cover_file(self):
    """ return name of cover file """

    cover = os.path.join(self._dir,"cover.jpg")
    if os.path.exists(cover):
      return cover
    else:
      return None

  # --- create directory info for given dir   --------------------------------

  def _get_dirinfo(self,dir):
    """ create directory info """

    self._dirinfo =  {'dirs':  [], 'files': [], 'dur': []}
    self.msg("Player: collecting dir-info for %s" % dir)

    # first entry is parent directory
    if self._dir != self._root_dir:
      self._dirinfo['dirs'].append('..')

    for f in os.listdir(dir):
      if os.path.isfile(os.path.join(dir,f)):
        if f.endswith(".mp3"):
          self._dirinfo['files'].append(f)
      else:
        self._dirinfo['dirs'].append(f)

    # ... and sort results
    self._dirinfo['files'].sort()
    self._dirinfo['dirs'].sort()

    # set current file (keep existing)
    if self._file:
      self._dirinfo['cur_file'] = os.path.basename(self._file)
    else:
      if len(self._dirinfo['files']):
        self._file = os.path.join(self._dir,self._dirinfo['files'][0])
        self._dirinfo['cur_file'] = self._dirinfo['files'][0]
      else:
        self._dirinfo['cur_file'] = None
      self._api.update_state(section="player",key="last_file",
                             value= self._dirinfo['cur_file'],publish=False)

    # add add time-info
    for f in self._dirinfo['files']:
      secs = int(subprocess.check_output(["mp3info",
                                          "-p","%S",
                                          os.path.join(dir,f)]))
      self._dirinfo['dur'].append((secs,self._pp_time(secs)))
