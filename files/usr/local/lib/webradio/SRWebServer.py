#!/usr/bin/python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Class SRWeb: serve gui and process API-requests
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-webradio
#
# ----------------------------------------------------------------------------

# --- System-Imports   -------------------------------------------------------

import os, bottle, json
from bottle import route, ServerAdapter

from webradio import Base

# --- helper class to enable stopping   --------------------------------------
# (this works around a shortcoming of Bottle)

class StoppableServer(ServerAdapter):

  def run(self, app): # pragma: no cover
    from wsgiref.simple_server import WSGIRequestHandler, WSGIServer
    from wsgiref.simple_server import make_server
    import socket

    class FixedHandler(WSGIRequestHandler):
      def address_string(self): # Prevent reverse DNS lookups please.
        return self.client_address[0]
      def log_request(*args, **kw):
        if not self.quiet:
          return WSGIRequestHandler.log_request(*args, **kw)

    handler_cls = self.options.get('handler_class', FixedHandler)
    server_cls  = self.options.get('server_class', WSGIServer)

    if ':' in self.host: # Fix wsgiref for IPv6 addresses.
      if getattr(server_cls, 'address_family') == socket.AF_INET:
        class server_cls(server_cls):
          address_family = socket.AF_INET6

    self._server = make_server(self.host, self.port, app, server_cls, handler_cls)
    self._server.serve_forever()

  def stop(self):
    if hasattr(self,'_server'):
      self._server.server_close()
      self._server.shutdown()

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------

# --- application web-server class   -----------------------------------------

class WebServer(Base):
  """ Serve GUI and process API-requests """

  # --- constructor   --------------------------------------------------------

  def __init__(self,app):
    """ constructor """

    self._app          = app
    self._api          = app.api
    self.debug         = app.debug

    self.stop_event    = app.stop_event
    self.read_config(app.options.pgm_dir)
    self._set_routes()

  # --- read configuration   --------------------------------------------------

  def read_config(self,pgm_dir):
    """ read configuration from config-file """

    # section [WEB]
    self._port = int(self.get_value(self._app.parser,"WEB","port",9026))
    self._host = self.get_value(self._app.parser,"WEB","host","0.0.0.0")

    default_web_root = os.path.realpath(
      os.path.join(pgm_dir,"..","lib","pi-webradio","web"))
    self._web_root  = self.get_value(self._app.parser,"WEB","web_root",
                                         default_web_root)

  # --- set up routing   -----------------------------------------------------

  def _set_routes(self):
    """ set up routing (decorators don't seem to work for methods within a class """

    # web-interface (GUI)
    bottle.get('/',callback=self.main_page)
    bottle.get('/css/<filepath:path>',callback=self.css_pages)
    bottle.get('/images/<filepath:path>',callback=self.images)
    bottle.get('/js/<filepath:path>',callback=self.js_pages)
    bottle.get('/api/<api:path>',callback=self.process_api)

  # --- return absolute path of web-files   ----------------------------------

  def _get_path(self,path):
    """ absolute path of web-file """
    return os.path.join(self._web_root,path)

  # --- static routes   ------------------------------------------------------

  def css_pages(self,filepath):
    return bottle.static_file(filepath, root=self._get_path('css'))
  
  def images(self,filepath):
      return bottle.static_file(filepath, root=self._get_path('images'))
  
  def js_pages(self,filepath):
      return bottle.static_file(filepath, root=self._get_path('js'))
  
  # --- main page   ----------------------------------------------------------

  def main_page(self):
    tpl = bottle.SimpleTemplate(name="index.html",lookup=[WEB_ROOT])
    return tpl.render()

  # --- process API-call   -------------------------------------------------

  def process_api(self,api):
    """ process api """

    if api.startswith("_"):
      # internal API, illegal request!
      self.msg("illegal api-call: %s" % api)
      msg = '"illegal request /api/%s" % api'
      bottle.response.content_type = 'application/json'
      bottle.response.status       = 400                 # bad request
      return '{"msg": ' + msg +'}'
    else:
      self.msg("processing api-call: %s" % api)
      try:
        response = self._api.exec(api)
        bottle.response.content_type = 'application/json'
        return json.dumps(response)
      except NotImplementedError as err:
        self.msg("illegal request: /api/%s" % api)
        msg = '"/api/%s not implemented" % api'
        bottle.response.content_type = 'application/json'
        bottle.response.status       = 400                 # bad request
        return '{"msg": ' + msg +'}'

  # --- stop web-server   --------------------------------------------------

  def stop(self):
    """ stop the web-server """

    self.msg("WebServer: process stop-request")
    self._server.stop()

  # --- service-loop   -----------------------------------------------------

  def run(self):
    """ start and run the webserver """

    self._server = StoppableServer(host=self._host,port=self._port)
    if self.debug:
      self.msg("WebServer: starting the web-server in debug-mode")
      self.msg("WebServer: listening on port %s" % self._port)
      self.msg("WebServer: using web-root: %s" % self._web_root)
      bottle.run(host='localhost',
                 port=self._port,
                 server=self._server,
                 debug=True,reloader=True)
    else:
      bottle.run(host=self._host,
                 port=self._port,
                 server=self._server,
                 debug=False,reloader=False)

    self.msg("WebServer: finished")
