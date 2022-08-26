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

import os, subprocess, json

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
    mp3info = subprocess.check_output(
      ["mp3info","-p","%S\n%a\n%c\n%l\n%n\n%t",f])
    #                  total
    #                      artist
    #                          comment
    #                              album
    #                                  track
    #                                      title

    try:
      mp3info = mp3info.decode("utf-8")
    except:
      mp3info = mp3info.decode("iso-8859-1")

    #tokenize and convert
    tokens = mp3info.split("\n")
    info                 = {} 
    info['fname']        = file
    info['total']        = int(tokens[0])
    info['total_pretty'] = self._pp_time(info['total'])
    try:
      info['artist']       = tokens[1]
      info['comment']      = tokens[2]
      info['album']        = tokens[3]
      info['track']        = int(tokens[4])
      info['title']        = tokens[5]
    except:
      pass
    self.msg("MP3Info: file-info: %s" % json.dumps(info))
    return info

  # --- create directory info for given dir   --------------------------------

  def get_dirinfo(self,dir):
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
