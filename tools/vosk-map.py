#!/usr/bin/python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# A simple cli-client for the pi-webradio.
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

WORDS_DE = {
  "on":          "an",
  "off":         "aus",
  "volume up":   "lauter",
  "volume down": "leiser",
  "channel":     "kanal",
  "next":        "weiter",
  "previous":    "zurück",
  "stop":        "stop",
  "quit":        "ende",
  "radio":       "radio",
  1:             "eins",
  2:             "zwei",
  3:             "drei",
  4:             "vier",
  5:             "fünf"
  }

WORDS_EN = {
  "on":          "on",
  "off":         "off",
  "volume up":   "volume up",
  "volume down": "volume down",
  "channel":     "channel",
  "next":        "next",
  "previous":    "previous",
  "stop":        "stop",
  "quit":        "quit",
  "radio":       "radio",
  1:             "one",
  2:             "two",
  3:             "three",
  4:             "four",
  5:             "five"
  }

WORDS_MAPS = {
  "de": WORDS_DE,
  "en": WORDS_EN
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

  # --- read channel file   --------------------------------------------------

  def read_channels(self):
    """ read channel file """

    self._channels = []

    print("Loading channels from %s" % self.file[0])
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
        config["api_map"][key] = value

      # add api by channel name
      key = channel["name"]
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
