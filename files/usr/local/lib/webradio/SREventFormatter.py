#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Pi-Webradio: implementation of class EventFormatter
#
# The class EventFormatter converts events to a printable form.
# TODO: support i18n
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-webradio
#
# -----------------------------------------------------------------------------

class EventFormatter(object):
  """ format events """

  # --- format map: type:format   ---------------------------------------------
  _FMT_MAP = {
    'version': 'pi-webradio version {value}',
    'icy_meta': '{value}',
    'icy_name': 'channel name: {value}',
    'rec_start': 'recording {name} for {duration} minutes',
    'rec_stop': 'finished recording. File {file}, duration: {duration}m',
    'vol_set': 'setting current volume to {value}',
    'radio_play_channel': 'start playing channel {nr} ({name})',
    'play_file': 'playing file: {value}',
    'file_info': '{name}: {duration}',
    'id3': '{tag}: {value}',
    'keep_alive': 'current time: {value}',
    'eof': '{value} finished'
    }

  # --- format event   --------------------------------------------------------

  def format(self,event):
    """ format given event """

    key = event['type']
    if key in EventFormatter._FMT_MAP:
      if isinstance(event['value'],dict):
        return EventFormatter._FMT_MAP[key].format(**event['value'])
      else:
        return EventFormatter._FMT_MAP[key].format(**event)
    else:
      return "%r" % event
