#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Pi-Webradio: implementation of class Base
#
# The class Base is the root-class of all classes and implements common methods
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-webradio
#
# -----------------------------------------------------------------------------

import sys

class Base:
  """ base class with common methods """

  # --- print debug messages   ------------------------------------------------

  def msg(self,text,force=False):
    """ print debug-message """

    if force:
      sys.stderr.write("%s\n" % text)
    elif self.debug:
      sys.stderr.write("[DEBUG] %s\n" % text)
    sys.stderr.flush()

  # --- read configuration value   --------------------------------------------

  def get_value(self,parser,section,option,default):
    """ get value of config-variables and return given default if unset """

    if parser.has_section(section):
      try:
        value = parser.get(section,option)
      except:
        value = default
    else:
      value = default
    return value

  # --- return persistent state of this class   -------------------------------

  def get_persistent_state(self):
    """ return persistent state (implemented by subclasses) """
    return {}

  # --- set state state of this class   ---------------------------------------

  def set_persistent_state(self,state_map):
    """ set state (implemented by subclasses) """
    pass
