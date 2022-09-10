#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Pi-Webradio: implementation of helper class MP3Info
#
# The class MP3Info collects and caches MP3-infos of the files of a directory.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-webradio
#
# -----------------------------------------------------------------------------

import os, subprocess, json, traceback, eyed3

from webradio import Base

class MP3Info(Base):
  """ query MP3-info from files """

  def __init__(self,app):
    """ constructor """

    self.debug   = app.debug

  # --- pretty print duration/time   ----------------------------------------

  def _pp_time(self,seconds):
    """ pritty-print time as mm:ss or hh:mm """

    m, s = divmod(seconds,60)
    h, m = divmod(m,60)
    if h > 0:
      return "{0:02d}:{1:02d}:{2:02d}".format(h,m,s)
    else:
      return "{0:02d}:{1:02d}".format(m,s)

  # --- create file info for a given file   ----------------------------------

  def get_fileinfo(self,dir,file):
    """ create file info """

    if os.path.isabs(file):
      f = file
    else:
      f = os.path.join(dir,file)

    # as fallback, assume file = "artist - title.mp3"
    ind = file.find(' - ')
    if ind > 0:
      artist = file[:ind]
      title  = file[ind+3:len(file)-4]
    else:
      artist = ""
      title  = file[0:len(file)-4]

    mp3info = eyed3.load(f)
    info                 = {}
    info['total']        = int(mp3info.info.time_secs)
    info['total_pretty'] = self._pp_time(info['total'])
    info                 = {} 
    info['fname']        = file
    info['artist']       = mp3info.tag.artist if mp3info.tag.artist else artist
    info['album']        = mp3info.tag.album
    info['track']        = mp3info.tag.track_num[0]
    info['title']        = mp3info.tag.title if mp3info.tag.title else title

    # read raw comment field to have a chance to decode it correctly
    # id2.3 does not support unicode, nevertheless it is used
    if len(mp3info.tag.comments):
      c = mp3info.tag.comments[0]
      try:
        info['comment'] = c.data[4:].lstrip(b'\x00').decode("utf-8")
      except:
        info['comment'] = c.data[4:].lstrip(b'\x00').decode("iso-8859-1")
      info['comment'] = info['comment'].replace("\x00 ",": ")
    else:
      info['comment'] = ""

    self.msg("MP3Info: file-info: %s" % json.dumps(info))
    return info

  # --- return directory info for given dir   --------------------------------

  def get_dirinfo(self,dir,force_save=False):
    """ return directory info """

    info_file = os.path.join(dir,".dirinfo")
    mtime_dir = os.path.getmtime(dir)
    if os.path.exists(info_file) and mtime_dir <= os.path.getmtime(info_file):
      try:
        f = open(info_file,"r")
        dirinfo = json.load(f)
        f.close()
        self.msg("MP3Info: using existing dir-info file %s" % info_file,force_save)
        return dirinfo
      except:
        self.msg("MP3Info: could not load dir-info file %s" % info_file)
        if self.debug:
          traceback.print_exc()

    dirinfo = self._create_dirinfo(dir)
    # only update dirinfo-file if it already existed before
    if os.path.exists(info_file) or force_save:
      try:
        f = open(info_file,"w")
        json.dump(dirinfo,f,indent=2)
        f.close()
        self.msg("MP3Info: saving dir-info file %s" % info_file,force_save)
      except:
        self.msg("MP3Info: could not write dir-info file %s" % info_file,force_save)
    return dirinfo

  # --- recursively write directory info for given dir   ---------------------

  def write_dirinfo(self,dir):
    """ recursively write directory info """

    if not os.path.isdir(dir):
      self.msg("MP3Info: error: %d is no directory" % dir,True)
      return
    dirinfo = self.get_dirinfo(dir,True)
    for d in dirinfo['dirs']:
      self.write_dirinfo(os.path.join(dir,d))

  # --- create directory info for given dir   --------------------------------

  def _create_dirinfo(self,dir):
    """ create directory info """

    dirinfo = {'dirs':  [], 'files': []}
    files   = []
    self.msg("MP3Info: collecting dir-info for %s" % dir)

    for f in os.listdir(dir):
      if os.path.isfile(os.path.join(dir,f)):
        if f.endswith(".mp3"):
          files.append(f)
      else:
        dirinfo['dirs'].append(f)

    # ... and sort results
    files.sort()
    dirinfo['dirs'].sort()

    # add add time and mp3-info
    for f in files:
      dirinfo['files'].append(self.get_fileinfo(dir,f))

    return dirinfo
