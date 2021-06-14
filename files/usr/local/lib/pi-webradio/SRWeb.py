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
from bottle import route
from gevent import monkey; monkey.patch_all()

class SRWeb(object):
  """ Serve GUI and process API-requests """

  # --- constructor   --------------------------------------------------------

  def __init__(self,options):
    """ constructor """

    self._options = options
    self._options.web_root = os.path.realpath(
      os.path.join(self._options.pgm_dir,"..","lib","pi-webradio","web"))
    self._set_routes()

  # --- set up routing   -----------------------------------------------------

  def _set_routes(self):
    """ set up routing (decorators don't seem to work for methods within a class """

    # web-interface (GUI)
    bottle.get('/',callback=self.main_page)
    bottle.get('/css/<filepath:path>',callback=self.css_pages)
    bottle.get('/images/<filepath:path>',callback=self.images)
    bottle.get('/js/<filepath:path>',callback=self.js_pages)
    bottle.get('/api/<api:path>',callback=self.process_api)

    # utilities and api
    bottle.get('/version',callback=self.version)
    bottle.get('/shutdown',callback=self.shutdown)
    bottle.get('/reboot',callback=self.reboot)
    bottle.get('/restart',callback=self.restart)

  # --- return absolute path of web-files   ----------------------------------

  def _get_path(self,path):
    """ absolute path of web-file """
    return os.path.join(self._options.web_root,path)

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

  # --- shutdown system   ----------------------------------------------------

  def shutdown(self):
    """ shutdowne the system """

    if self._options.debug:
      print("DEBUG: shutting down the system """)
      os.system("sudo /sbin/halt &")

  # --- rebooting the system   ---------------------------------------------

  def reboot(self):
    """ rebooting the system """

    if self._options.debug:
      print("DEBUG: rebooting the system")
      os.system("sudo /sbin/reboot &")

  # --- restart the service   ------------------------------------------------

  def restart(self):
    """ restart the service """

    if self._options.debug:
      print("DEBUG: restarting pi-webradio.service")
      os.system("sudo /sbin/systemctl restart pi-webradio.service &")

  # --- return version   ---------------------------------------------------

  def version(self):
    """ return version """

    if self._options.debug:
      print("DEBUG: method: SRWeb.version()")
    bottle.response.content_type = 'application/json'
    return json.dumps(self._options.version)

  # --- process API-call   -------------------------------------------------

  def process_api(self,api):
    """ process api """

    if self._options.debug:
      print("DEBUG: processing api-call: %s" % api)
    bottle.response.content_type = 'application/json'
    return json.dumps(api)

  # --- service-loop   -----------------------------------------------------

  def run(self):
    """ start and run the webserver """

    if self._options.debug:
      print("DEBUG: web-root directory: %s" % self._options.web_root)
      print("DEBUG: starting the webserver in debug-mode")
      bottle.run(host='localhost',
             port=self._options.port[0],
             debug=True,reloader=True,
             server='gevent')
    else:
      bottle.run(host=self._options.host[0],
             port=self._options.port[0],
             debug=False,reloader=False,
             server='gevent')
