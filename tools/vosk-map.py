#!/usr/bin/python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Create phrase-api map from pi-webradio.channels (pass as argument).
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-webradio
#
# ----------------------------------------------------------------------------

import locale, os, sys, json
from   argparse import ArgumentParser

# --- language-mappings   ----------------------------------------------------

from word_map_de import words_de
from word_map_en import words_en

WORDS_MAPS = {
  "de": words_de,
  "en": words_en
  }

# --- application class   ----------------------------------------------------

class App(object):

  # --- constructor   --------------------------------------------------------

  def __init__(self):
    """ constructor """

    parser = self._get_parser()
    parser.parse_args(namespace=self)

  # --- cmdline-parser   -----------------------------------------------------

  def _get_parser(self):
    """ configure cmdline-parser """

    parser = ArgumentParser(add_help=False,description='Vosk Word-Map creator')

    parser.add_argument('-d', '--debug', action='store_true',
      dest='debug', default=False,
      help="force debug-mode")
    parser.add_argument('-q', '--quiet', action='store_true',
      dest='quiet', default=False,
      help="don't print messages")
    parser.add_argument('-h', '--help', action='help',
      help='print this help')

    parser.add_argument('-L', '--language', dest="lang",
                        metavar="language", default="de",
                        choices = WORDS_MAPS.keys(),
       help='language for phrase-mappings ('+", ".join(WORDS_MAPS.keys())+')')

    parser.add_argument('file', nargs=1, metavar='channel-file',
      default=1, help='channel file name')
    return parser

  # --- convert name   -------------------------------------------------------

  def _convert_name(self,name):
    """ convert numbers within name """

    words = WORDS_MAPS[self.lang]

    name = name.lower()

    parts = name.split()
    result = []
    for part in parts:
      # check for number ...
      try:
        part_int = int(part)
        is_int = True
      except:
        is_int = False

      if is_int and part_int in words:
        # ...  and convert to text
        result.append(words[part_int])
      else:
        result.append(part)

    return " ".join(result)

  # --- read channel file   --------------------------------------------------

  def read_channels(self):
    """ read channel file """

    self._channels = []

    f = open(self.file[0],"r")
    self._channels = json.load(f)
    f.close()
    nr=1
    for channel in self._channels:
      channel['nr'] = nr
      nr += 1

  # --- print phrase-map   ---------------------------------------------------

  def print_config(self):
    """ print config for Vosk """

    words = WORDS_MAPS[self.lang]
    config = {
      "model":     "/usr/local/lib/vosk/model",
      "device_id": 1,
      "api_map": {
        words["radio"]:       ["_set_cmd_mode"],
        words["on"]:          ["radio_on"],
        words["off"]:         ["radio_off"],
        words["volume up"]:   ["vol_up"],
        words["volume down"]: ["vol_down"],
        words["next"]:        ["radio_play_next"],
        words["previous"]:    ["radio_play_prev"],
        words["stop"]:        ["sys_stop"],
        words["quit"]:        ["_quit"]
        }
      }

    for channel in self._channels:
      # add api by channel number
      nr = channel["nr"]
      value = ["radio_play_channel", "nr=%d" % nr]
      if nr in words:
        key = "%s %s" % (words["channel"], words[nr])
      else:
        key = "%s %d" % (words["channel"], nr)
      config["api_map"][key] = value

      # add api by channel name
      key = self._convert_name(channel["name"])
      config["api_map"][key] = value

    print(json.dumps(config,indent=2,ensure_ascii=False))

# --- main program   ---------------------------------------------------------

if __name__ == '__main__':

  # set local to default from environment
  locale.setlocale(locale.LC_ALL, '')

  # create client-class and parse arguments
  app = App()
  app.read_channels()
  app.print_config()
