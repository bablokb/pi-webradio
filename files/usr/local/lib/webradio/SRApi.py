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

  def __init__(self,app):
    """ initialization """

    self._app          = app
    self.debug         = app.debug

  # --- execute API by name   -------------------------------------------------

  def _exec(self,name,**args):
    """ execute an API by name """

    if hasattr(self,name):
      self.msg("executing: %s(%r)" % (name,dict(**args)))
      return getattr(self,name)(**args)
    else:
      self.msg("unknown API-method %s" % name)
      raise NotImplementedError("API %s not implemented" % name)
