#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Pi-Webradio: implementation of class Api
#
# Collect all API-functions
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-webradio
#
# -----------------------------------------------------------------------------

from webradio import Base

class Api(Base):
  """ The class holds References to all API-functions """

  # --- execute API by name   -------------------------------------------------

  def exec(self,name,*args):
    """ execute an API by name """

    if hasattr(self,name):
      self.debug("executing: %s(%r)" % (name,(*args,)))
      getattr(self,name)(*args)
    else:
      raise NotImplementedError("API %s not implemented" % name)
