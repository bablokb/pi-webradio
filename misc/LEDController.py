#!/usr/bin/python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Pi-Webradio: sample implementation of the class LEDController
#
# The methods of this class will be called by VoskController. For your
# own version, you have to implement all methods.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-webradio
#
# ----------------------------------------------------------------------------

import webradio.apa102 as apa102
import time
from gpiozero import LED

class LEDController:
  """ change LED according to events """

  NUM_PIXELS = 12
  DELAY      = 0.5

  # --- constructor   --------------------------------------------------------

  def __init__(self):
    """ constructor """

    self._leds = apa102.APA102(num_led=LEDController.NUM_PIXELS,
                               global_brightness=2)
        
    self._power = LED(5)
    self._power.on()

  # --- set color (helper method)   ------------------------------------------

  def _set_color(self,r,g,b,flash=1):
    """ set color-ring and flash it """

    for f in range(flash):
      for i in range(LEDController.NUM_PIXELS):
        self._leds.set_pixel(i,r,g,b)
      self._leds.show()
      time.sleep(LEDController.DELAY)
      self._leds.clear_strip()
      time.sleep(LEDController.DELAY)

    for i in range(LEDController.NUM_PIXELS):
      self._leds.set_pixel(i,r,g,b)
    self._leds.show()

  # --- after mic is activated by wake-word   --------------------------------
  
  def active(self):
    """ active state (waiting for a command) """

    self._set_color(0,0,255)   # all blue

  # --- after mic is waiting for wake-word   ---------------------------------
  
  def inactive(self):
    """ inactive, waiting for wake word """

    self._leds.clear_strip()

  # --- after successful detection of a command   ----------------------------
  
  def success(self):
    """ detected valid command in active mode """

    self._set_color(0,255,0)   # all green

  # --- after detection of an unknown command   ------------------------------
  
  def unknown(self):
    """ detected unknown command in active mode """

    self._set_color(255,0,0,flash=2)   # all red

# --- main (test) program   --------------------------------------------------

if __name__ == '__main__':

  ctrl = LEDController()
  print("activating...")
  ctrl.active()
  time.sleep(3)

  print("deactivating...")
  ctrl.inactive()
  time.sleep(1)

  print("activating...")
  ctrl.active()
  time.sleep(2)

  print("success...")
  ctrl.success()
  time.sleep(2)

  print("unknown...")
  ctrl.unknown()
  time.sleep(2)

  print("the end")
  ctrl.inactive()
