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

import os, time, datetime, threading, copy, queue

from webradio import Base, MP3Info

class Player(Base):
  """ Player-controller """

  def __init__(self,app):
    """ initialization """

    self._app     = app
    self.debug    = app.debug
    self._api     = app.api
    self._backend = app.backend

    self._lock        = threading.Lock()
    self._file        = None
    self._dirinfo     = None
    self._dirplay     = None
    self._dirstop     = threading.Event()
    self._init_thread = None

    self.read_config()
    self.register_apis()

    self._mp3info = MP3Info(app)

  # --- read configuration   --------------------------------------------------

  def read_config(self):
    """ read configuration from config-file """

    # section [PLAYER]
    self._wait_dir = int(self.get_value(self._app.parser,"PLAYER",
                                        "player_wait_dir",10))
    self._root_dir = self.get_value(self._app.parser,"PLAYER",
                                    "player_root_dir",
                                    os.path.expanduser("~"))
    self._root_dir = os.path.abspath(self._root_dir)

    self._def_dir = self.get_value(self._app.parser,"PLAYER",
                                    "player_def_dir",
                                    self._root_dir)
    self._def_dir = os.path.abspath(self._def_dir)

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
    self._api.player_set_pos    = self.player_set_pos
    self._api.player_select_dir = self.player_select_dir
    self._api.player_play_dir   = self.player_play_dir
    self._api._player_get_cover_file = self._player_get_cover_file

  # --- return persistent state of this class   -------------------------------

  def get_persistent_state(self):
    """ return persistent state (overrides SRBase.get_pesistent_state()) """
    return {
      'player_dir': self._dir,
      'player_file': self._file,
      'player_elapsed': self._backend.elapsed()   # 0.0-1.0 elapsed (relative)
      }

  # --- restore persistent state of this class   ------------------------------

  def set_persistent_state(self,state_map):
    """ restore persistent state (overrides SRBase.set_pesistent_state()) """

    self.msg("Player: restoring persistent state")
    if 'player_dir' in state_map:
      self._dir = state_map['player_dir']
      self.msg("Player: currrent dir (tentative):  %s" % self._dir)
    if 'player_file' in state_map:
      self._file = state_map['player_file']
      self.msg("Player: currrent file (tentative): %s" % self._file)
    if 'player_elapsed' in state_map:
      self._elapsed = state_map['player_elapsed']
      self.msg("Player: elapsed: %s" % self._elapsed)
    self._api.update_state(section="player",key="last_dir",
                           value=self._dir[len(self._root_dir):]+os.path.sep,
                           publish=False)
    self._init_thread = threading.Thread(target=self._init_state)
    self._init_thread.start()

  # --- lazy query of dir-info during initialization   ----------------------

  def _init_state(self):
    """ wait for directory and query dir-info """

    # check directory (wait if necessary)
    self.msg("Player: waiting for %s" % self._dir)
    while not os.path.exists(self._dir) and self._wait_dir:
      time.sleep(1)
      self._wait_dir -= 1

    # check again
    if self._check_dir(self._dir):
      self._get_dirinfo(self._dir,True)

    else:
      # oops, check failed, now check everything
      if not os.path.exists(self._root_dir):
        self.msg("[WARNING] Player: root-directory %s of player does not exist" %
                 self._root_dir,True)
        self._root_dir = os.path.expanduser("~")
        self.msg("[WARNING] Player: using %s as fallback" % self._root_dir,True)
      if not self._check_dir(self._def_dir):
        self._def_dir = self._root_dir
        self.msg("[WARNING] Player: using %s as fallback" % self._root_dir,True)
      self._dir = self._def_dir
      self._get_dirinfo(self._dir,True)

    # also check files now
    if self._file and not self._check_file(self._file):
      self._file = None
      self._elapsed = 0

    self._init_thread = None
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

  # --- start playing   -------------------------------------------------------

  def player_play_file(self,file=None,last=True):
    """ start playing """

    if self._init_thread:
      self._init_thread.join()

    if file:
      if not os.path.isabs(file):
        file = os.path.join(self._dir,file)
      if not self._check_file(file):
        raise ValueError("invalid filename %s" % file)
      if self._file != file:
        self._elapsed = 0
      #else:
      #  self._elapsed = self._backend.elapsed()
      self._file = file

    if not self._file:
      raise ValueError("default file not set")

    # query fileinfo.
    base = os.path.basename(self._file)
    if self._dirinfo:
      self._dirinfo['cur_file'] = base
      _,file_info = self._get_index(base)
      file_info = copy.deepcopy(file_info)      # keep original as is
    else:
      file_info = self._mp3info.get_fileinfo(None,self._file)
    # add info
    file_info['last']  = last

    # this will push the information to all clients, even if the file
    # is already playing.

    self._api._push_event({'type': 'file_info', 'value': file_info })
    if self._backend.play(self._file,last,self._elapsed*file_info['total']):
      self._api.update_state(section="player",key="last_file",
                             value=os.path.basename(self._file),publish=False)
    self._api.update_state(section="player",key="file_info",
                           value=file_info,
                           publish=False)
    return file_info

  # --- stop playing   -------------------------------------------------------

  def player_stop(self):
    """ stop playing (play->stop, pause->stop)"""

    if self._dirplay:
      self._dirstop.set()         # this will also stop the backend
      self._dirplay.join()
    else:
      self._backend.stop()        # backend will publish eof-event
    self._elapsed = 0

  # --- pause playing   -----------------------------------------------------

  def player_pause(self):
    """ pause playing (play->pause) """

    self._backend.pause()
    self._elapsed = self._backend.elapsed()

  # --- resume playing   ----------------------------------------------------

  def player_resume(self):
    """ resume playing (pause->play) """

    self._backend.resume()

  # --- toggle playing   ------------------------------------------------------

  def player_toggle(self):
    """ toggle playing (play->pause, pause->play) """

    self._backend.toggle()
    self._elapsed = self._backend.elapsed()

  # --- jump to selected position   -------------------------------------------

  def player_set_pos(self,elapsed):
    """ jump to given absolute position in seconds """

    self._backend.jump(elapsed)

  # --- select directory, return entries   ------------------------------------

  def player_select_dir(self,dir=None):
    """ select directory:
        a directory starting with a / is always interpreted relative
        to root_dir, otherwise relative to the current directory
    """

    if self._init_thread:
      self._init_thread.join()

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

    if self._init_thread:
      self._init_thread.join()

    # check existing player-thread, stop it and wait until it is finished
    if self._dirplay:
      self._dirstop.set()
      self._dirplay.join()

    # copy file-list
    if not start:
      files = copy.deepcopy(self._dirinfo['files'])
    else:
      try:
        index,_ = self._get_index(start)
        self.msg("Player: starting play_dir with file %s (index %i)" %
                 (start,index))
        files = copy.deepcopy(self._dirinfo['files'][index:])
      except ValueError:
        raise ValueError("file %s does not exist" % start)

    # start player-thread, pass files as argument
    self._dirstop.clear()
    self._dirplay = threading.Thread(target=self._play_dir,args=(files,))
    self._dirplay.start()

  # --- get index within file-list   -----------------------------------------

  def _get_index(self,start):
    """ return index for given filename """

    for index, item in enumerate(self._dirinfo['files']):
      if item['fname'] == start:
        return index,item
    raise ValueError()

  # --- play all files (helper)   --------------------------------------------

  def _play_dir(self,files):
    """ play all given files """

    ev_queue = self._api._add_consumer("_play_dir")
    do_exit = False

    index_last = len(files)-1
    for index,f in enumerate(files):
      fname = f['fname']
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
              self._elapsed = 0
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

  def _get_dirinfo(self,dir,init=False):
    """ create directory info """

    self._dirinfo = self._mp3info.get_dirinfo(dir)

    # first entry is parent directory unless in root-dir
    if self._dir != self._root_dir:
      self._dirinfo['dirs'].insert(0,'..')

    # set current file
    if self._file and init:
      self._dirinfo['cur_file'] = os.path.basename(self._file)
    else:
      if len(self._dirinfo['files']):
        self._file = os.path.join(self._dir,self._dirinfo['files'][0]['fname'])
        self._dirinfo['cur_file'] = self._dirinfo['files'][0]['fname']
      else:
        self._dirinfo['cur_file'] = None
      self._api.update_state(section="player",key="last_file",
                             value= self._dirinfo['cur_file'],publish=False)
