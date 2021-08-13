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

import locale, os, sys, json, traceback
from webradio_cli import RadioCli

try:
  from ST7789 import ST7789
  from PIL import Image, ImageDraw
  have_st7789 = True
except:
  have_st7789 = False

# --- application class   ----------------------------------------------------

class PirateAudio(RadioCli):
  """ application class """

  # --- constructor   --------------------------------------------------------

  def __init__(self):
    """ constructor """

    super(PirateAudio,self).__init__()
    if have_st7789:
      self.msg("PirateAudio: detected ST7789")
      self._init_display()
    else:
      self.msg("PirateAudio: no ST7789")

  # --- init display   -------------------------------------------------------

  def _init_display(self):
    """ initialize the display """

    SPI_SPEED_MHZ = 80

    self._last_logo = ""

    self._screen = ST7789(
      rotation=90,  # Needed to display the right way up on Pirate Audio
      port=0,       # SPI port
      cs=1,         # SPI port Chip-select channel
      dc=9,         # BCM pin used for data/command
      backlight=13,
      spi_speed_hz=SPI_SPEED_MHZ * 1000 * 1000
      )

  # --- update display   -----------------------------------------------------

  def _update_display(self,logo):
    """ update display with logo """

    if logo == self._last_logo:
      return

    logo_file = os.path.join(self.pgm_dir,"..","lib","webradio",
                             "web","images",logo)
    if not os.path.exists(logo_file):
      logo_file = os.path.join(self.pgm_dir,"..","lib","webradio",
                             "web","images","default.png")
    self.msg("PirateAudio: logo-file: %s" % logo_file)

    try:
      img = None
      im  = Image.open(logo_file)
      img = im.resize((240,240))
      im.close()
      self._screen.display(img)
      self._last_logo = logo
    except:
      traceback.print_exc()
      self.msg("PirateAudio: failed to display %s" % logo_file)

  # --- handle event   -------------------------------------------------------

  def handle_event(self,event):
    """ override to display channel-logo """

    ev_data = json.loads(event.data)
    if ev_data['type'] != 'radio_play_channel':
      self.msg("PirateAudio: ignoring event with type %s" % ev_data['type'])
      return

    logo = ev_data['value']['logo']
    self.msg("PirateAudio: logo: %s" % logo)
    if have_st7789:
      self._update_display(logo)
    
  # --- close connection   ---------------------------------------------------

  def close(self):
    """ override to blank display """

    self._screen.set_backlight(0)
    super(PirateAudio,self).close()

# --- main program   ---------------------------------------------------------

if __name__ == '__main__':

  # set local to default from environment
  locale.setlocale(locale.LC_ALL, '')

  # create client-class and parse arguments
  app = PirateAudio()
  app.pgm_dir = os.path.dirname(os.path.realpath(__file__))
  app.run()
