#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Simple radio: implementation of class Base
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

class Base(object):
  """ base class with common methods """

  # --- print debug messages   ------------------------------------------------

  def debug(self,text):
    """ print debug-message """

    if self._debug:
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

  # --- return function-map of this class   -----------------------------------

  def get_funcs(self):
    """ return map of user-accessible functions """

    return {key[5:]:getattr(self,key)
            for key in dir(self) if key.startswith("func_")}

  # --- return persistent state of this class   -------------------------------

  def get_persistent_state(self):
    """ return persistent state (implemented by subclasses) """
    return {}

  # --- set state state of this class   ---------------------------------------

  def set_persistent_state(self,state_map):
    """ set state (implemented by subclasses) """
    pass

  # --- return active-state of the object   -----------------------------------

  def is_active(self):
    """ return active-state (overriden by subclasses) """
    return True
