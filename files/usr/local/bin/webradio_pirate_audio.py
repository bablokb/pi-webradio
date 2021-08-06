#!/usr/bin/python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# A control program for Pimoroni's Pirate-Audio hats.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-webradio
#
# ----------------------------------------------------------------------------

import locale, os, sys, json
from webradio_cli import RadioCli

# --- application class   ----------------------------------------------------

class PirateAudio(RadioCli):
  """ application class """

  # --- handle event   -------------------------------------------------------

  def handle_event(self,event):
    """ override to display channel-logo """

    ev_data = json.loads(event.data)
    if ev_data['type'] != 'radio_play_channel':
      self.msg("PirateAudio: ignoring event with type %s" % ev_data['type'])
      return

    try:
      self.msg("PirateAudio: logo: %s" % ev_data['value']['logo'])
    except:
      pass
    
# --- main program   ---------------------------------------------------------

if __name__ == '__main__':

  # set local to default from environment
  locale.setlocale(locale.LC_ALL, '')

  # create client-class and parse arguments
  app = PirateAudio()
  app.run()
