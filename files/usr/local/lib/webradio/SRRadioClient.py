#!/usr/bin/python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Pi-Webradio: implementation of class RadioClient
#
# The class RadioClient implements a simple python-client for the webradio-api.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-webradio
#
# ----------------------------------------------------------------------------

import urllib, urllib3, threading, time, json
import sseclient
import http.client as httplib

from webradio import Base

class RadioClient(Base):
  """ python-client for the webradio-api """

  # --- constructor   --------------------------------------------------------

  def __init__(self,host,port,debug=False,timeout=10):
    """ constructor """

    self._host      = host
    self._port      = port
    self.debug      = debug
    self._request   = httplib.HTTPConnection(host,port,timeout)
    self._sseclient = None
    self._stop      = threading.Event()
    self._have_ev   = False
    self._api_list  = None

  # --- close request object   -----------------------------------------------

  def close(self):
    """ close internal request object """

    self._request.close()
    self._stop.set()
    if self._sseclient:
      self._sseclient.close()

  # --- execute request   ----------------------------------------------------

  def exec(self,api,params=None,close=False):
    """ execute api with given parameters """

    if len(params):
      qstring = urllib.parse.urlencode(params,quote_via=urllib.parse.quote)
      url = '/api/{0}?{1}'.format(api,qstring)
    else:
      url = '/api/'+api

    # send, get request and parse response
    try:
      self._request.request("GET",url)
      response = self._request.getresponse()
      data = (response.status,response.reason,response.read())
    except Exception as ex:
      self.msg("RadioClient: exception: %s" % ex)
      self._request = httplib.HTTPConnection(self._host,self._port)
      data = (-1,"connect error",None)

    if close:
      self.close()

    return data

  # --- return stop-event   --------------------------------------------------

  def get_stop_event(self):
    """ return stop event """

    return self._stop

  # --- set up SSE and return generator   ------------------------------------

  def get_events(self):
    """ set up SSE client and return event-queue """

    url      = 'http://{0}:{1}/api/get_events'.format(self._host,self._port)
    headers  = {'Accept': 'text/event-stream'}
    http     = urllib3.PoolManager()

    try:
      response = http.request('GET', url, preload_content=False, headers=headers)
      self._sseclient = sseclient.SSEClient(response)
      return self._sseclient.events()
    except Exception as ex:
      self.msg("RadioClient: exception: %s" % ex)
      return None

  # --- query API-list   -----------------------------------------------------

  def get_api_list(self):
    """ query API list """

    if self._api_list:
      return self._api_list
    else:
      _1,_2,apis = self.exec("get_api_list")
      self.msg("RadioClient: API-list: %r" % (apis,))
      if apis:
        self._api_list = json.loads(apis)
        return self._api_list
      else:
        return ""

  # --- process events   -----------------------------------------------------

  def _process_events(self,callback):
    """ process events """

    try:
      while True and not self._stop.is_set():
        events = self.get_events()
        self.msg("RadioClient: events: %r" % (events,))
        if not events:
          time.sleep(3)
          continue
        self._have_ev = True
        for event in events:
          if callback:
            callback(event)
          if self._stop.is_set():
            return
    except:
      pass

  # --- start event processing   ---------------------------------------------

  def start_event_processing(self,callback=None):
    """ create and start event-processing """

    threading.Thread(target=self._process_events,args=(callback,)).start()
    while not self._have_ev:
      # no events yet from server, so wait
      time.sleep(0.1)
    self.msg("RadioClient: event-processing activated")
    return self._stop
