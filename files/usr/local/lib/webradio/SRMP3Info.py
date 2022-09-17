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

import os, subprocess, re, json, traceback, eyed3

from webradio import Base

class MP3Info(Base):
  """ query MP3-info from files """

  # encoding map to replace wrong encodings with the correct version
  _ENC_MAP = {
    "\u00c3\u0080": "À",
    "\u00c3\u0084": "Ä",
    "\u00c3\u0088": "È",
    "\u00c3\u0089": "É",
    "\u00c3\u0095": "Õ",
    "\u00c3\u0096": "Ö",
    "\u00c3\u009c": "Ü",
    "\u00c3\u009f": "ß",
    "\u00c3\u00a0": "à",
    "\u00c3\u00a1": "á",
    "\u00c3\u00a2": "â",
    "\u00c3\u00a4": "ä",
    "\u00c3\u00a7": "ç",
    "\u00c3\u00a8": "è",
    "\u00c3\u00a9": "é",
    "\u00c3\u00aa": "ê",
    "\u00c3\u00ab": "ë",
    "\u00c3\u00ac": "ì",
    "\u00c3\u00ad": "í",
    "\u00c3\u00ae": "î",
    "\u00c3\u00af": "ï",
    "\u00c3\u00b1": "ñ",
    "\u00c3\u00b2": "ò",
    "\u00c3\u00b3": "ó",
    "\u00c3\u00b4": "ô",
    "\u00c3\u00b5": "õ",
    "\u00c3\u00b6": "ö",
    "\u00c3\u00b9": "ù",
    "\u00c3\u00bb": "û",
    "\u00c3\u00bc": "ü"
    }

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
      fname = os.path.basename(f)[0:-4]
      dname = os.path.basename(os.path.dirname(f))
    else:
      f = os.path.join(dir,file)
      fname = file[0:-4]
      dname = os.path.basename(dir.rstrip(os.path.sep))

    # defaults for artist/album from dirname
    ind = dname.find(' - ')
    if ind > 0:
      artist = dname[:ind]
      album  = dname[ind+3:]
    else:
      artist = dname
      album  = ""
    self.msg("MP3Info: artist/album from directory: %s/%s" % (artist,album))

    # defaults for artist/title from filename (without extension)
    # Could be:
    #   "artist - title"
    #   "track.? ?title"
    #   "track.? ?artist - title"
    regex_track = r'(\d+.?)? ?(.+)'
    _,_,fname,_ = re.split(regex_track,fname)   # remove track-number
    ind = fname.find(' - ')
    if ind > 0:
      artist = fname[:ind]
      title  = fname[ind+3]
    else:
      title  = fname                           # uses artist from dirname
    self.msg("MP3Info: artist/title from filename: %s/%s" % (artist,title))

    mp3info = eyed3.load(f)
    info                 = {}
    info['total']        = int(mp3info.info.time_secs)
    info['total_pretty'] = self._pp_time(info['total'])
    info['fname']        = file
    if mp3info.tag:
      info['artist']       = mp3info.tag.artist if mp3info.tag.artist else artist
      info['album']        = mp3info.tag.album if mp3info.tag.album else album
      info['track']        = [mp3info.tag.track_num[0],
                     mp3info.tag.track_num[1] if mp3info.tag.track_num[1] else 1]
      info['title']        = mp3info.tag.title if mp3info.tag.title else title

      if len(mp3info.tag.comments):
        c = mp3info.tag.comments[0]
        if c.description:
          info['comment'] = "%s: %s" % (c.description,c.text)
        else:
          info['comment'] = c.text
      else:
        info['comment'] = ""

    else:
      info['artist']  = artist
      info['album']   = album
      info['track']   = [1,1]
      info['title']   = title
      info['comment'] = ""

    # fix some encoding errors
    for tag in ['artist','album','title','comment']:
      v = info[tag]
      if not v:
        continue
      for key,value in MP3Info._ENC_MAP.items():
        v = v.replace(key,value)
      info[tag] = v
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
        json.dump(dirinfo,f,indent=2,ensure_ascii=False)
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
