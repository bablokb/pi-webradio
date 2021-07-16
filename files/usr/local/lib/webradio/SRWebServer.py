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

import os, json, queue, traceback

from flask import Flask, render_template, request, make_response
from flask import send_from_directory

from werkzeug.serving import make_server

from webradio import Base

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
    self._flask = Flask('pi-webradio',template_folder=self._web_root,
                        root_path=self._web_root)
    self._set_routes()

  # --- read configuration   --------------------------------------------------

  def read_config(self,pgm_dir):
    """ read configuration from config-file """

    # section [WEB]
    self._port = int(self.get_value(self._app.parser,"WEB","port",9026))
    self._host = self.get_value(self._app.parser,"WEB","host","0.0.0.0")

    default_web_root = os.path.realpath(
      os.path.join(pgm_dir,"..","lib","webradio","web"))
    self._web_root  = self.get_value(self._app.parser,"WEB","web_root",
                                         default_web_root)

  # --- set up routing   -----------------------------------------------------

  def _set_routes(self):
    """ set up routing (decorators don't seem to work for methods within a class """

    # web-interface (GUI)
    self._flask.add_url_rule('/','main',self.main_page)
    self._flask.add_url_rule('/css/<path:filepath>','css',self.css_pages)
    self._flask.add_url_rule('/webfonts/<path:filepath>','webfonts',self.webfonts)
    self._flask.add_url_rule('/images/<path:filepath>','images',self.images)
    self._flask.add_url_rule('/js/<path:filepath>','js',self.js_pages)
    self._flask.add_url_rule('/api/get_events','get_events',self.get_events)
    self._flask.add_url_rule('/api/<path:api>','api',self.process_api)

  # --- return absolute path of web-files   ----------------------------------

  def _get_path(self,*path):
    """ absolute path of web-file """
    return os.path.join(self._web_root,*path)

  # --- static routes   ------------------------------------------------------

  def css_pages(self,filepath):
    return send_from_directory(self._get_path('css'),filepath)

  def webfonts(self,filepath):
    return send_from_directory(self._get_path('webfonts'),filepath)
  
  def images(self,filepath):
    return send_from_directory(self._get_path('images'),filepath)
  
  def js_pages(self,filepath):
    return send_from_directory(self._get_path('js'),filepath)
  
  # --- main page   ----------------------------------------------------------

  def main_page(self):
    return render_template("index.html")

  # --- update logo with correct path   ------------------------------------

  def _update_logo(self,channel):
    """ update logo in channel-dict """
    if os.path.exists(self._get_path('images',channel['logo'])):
      channel['logo'] = 'images/'+channel['logo']
    else:
      channel['logo'] = None
    return channel

  # --- process API-call   -------------------------------------------------

  def process_api(self,api):
    """ process api """

    if api.startswith("_"):
      # internal API, illegal request!
      self.msg("illegal api-call: %s" % api)
      msg = '"illegal request /api/%s"' % api
      response = make_response(('{"msg": ' + msg +'}',400))
      response.content_type = 'application/json'
      return response
    else:
      self.msg("processing api-call: %s" % api)
      try:
        response = self._api.exec(api,**request.args)
        if api in ['radio_play_channel','radio_get_channel']:
          self._update_logo(response)
        elif api == 'radio_get_channels':
          response = [self._update_logo(c) for c in response]
        return json.dumps(response)
      except NotImplementedError as err:
        self.msg("illegal request: /api/%s" % api)
        msg = '"/api/%s not implemented"' % api
        response = make_response(('{"msg": ' + msg +'}',400))
        response.content_type = 'application/json'
        return response
      except Exception as ex:
        self.msg("exception while calling: /api/%s" % api)
        traceback.print_exc()
        msg = '"internal server error"'
        response = make_response(('{"msg": ' + msg +'}',500))
        response.content_type = 'application/json'
        return response

  # --- stream SSE (server sent events)   ----------------------------------

  def get_events(self):
    """ stream SSE """

    ev_queue = queue.Queue()
    self._api._add_consumer("web",ev_queue)

    try:
#       bottle.response.content_type = 'text/event-stream'
#       bottle.response.set_header('Cache-Control','no-cache')
#       bottle.response.set_header('Connection','keep-alive')
      while True:
        ev = ev_queue.get()
        ev_queue.task_done()
        if ev:
          sse = "data: %s\n\n" % json.dumps(ev)
          self.msg("WebServer: serving event %s" % sse)
#           bottle.response.status = 200                 # OK
          # send data using SSE
          yield sse
        else:
          break
    except:
      traceback.print_exc()
#   bottle.response.content_type = 'text/plain'
#   bottle.response.status = 404

  # --- stop web-server   --------------------------------------------------

  def stop(self):
    """ stop the web-server """

    self.msg("WebServer: process stop-request")
    self._server.shutdown()

  # --- service-loop   -----------------------------------------------------

  def run(self):
    """ start and run the webserver """

    self._server = make_server(self._host,self._port,self._flask)
    ctx = self._flask.app_context()
    ctx.push()

    self.msg("WebServer: starting the web-server in debug-mode")
    self.msg("WebServer: listening on port %s" % self._port)
    self.msg("WebServer: using web-root: %s" % self._web_root)
    self._server.serve_forever()
    self.msg("WebServer: finished")
