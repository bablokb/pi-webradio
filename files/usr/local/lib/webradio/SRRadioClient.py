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

import urllib3, threading
import sseclient
import http.client as httplib

from webradio import Base

class RadioClient(Base):
  """ python-client for the webradio-api """

  # --- constructor   --------------------------------------------------------

  def __init__(self,host,port,debug=False,timeout=10):
    """ constructor """

    self._host    = host
    self._port    = port
    self.debug    = debug
    self._request = httplib.HTTPConnection(host,port,timeout)
    self._client  = None
    self._stop    = threading.Event()

  # --- close request object   -----------------------------------------------

  def close(self):
    """ close internal request object """

    self._request.close()
    self._stop.set()
    if self._client:
      self._client.close()

  # --- execute request   ----------------------------------------------------

  def exec(self,api,qdict=None,qstring=None,close=False):
    """ execute api with given parameters """

    # build api-url
    query = ""
    if qdict:
      for k,v in qdict.items():
        query=query+"&"+k+"="+v
    if qstring:
      query=query+"&"+qstring

    query=query.lstrip('&')        # remove leading & if necessary

    if len(query):
      url = '/api/'+api+'?'+query
    else:
      url = '/api/'+api

    # send, get request and parse response
    self._request.request("GET",url)
    response = self._request.getresponse()
    data = (response.status,response.reason,response.read())

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
    response = http.request('GET', url, preload_content=False, headers=headers)

    self._client = sseclient.SSEClient(response)
    return self._client.events();

  # --- process events   -----------------------------------------------------

  def _process_events(self,callback):
    """ process events """

    events = self.get_events()
    for event in events:
      if callback:
        callback(event)
      if self._stop.is_set():
        break

  # --- start event processing   ---------------------------------------------

  def start_event_processing(self,callback=None):
    """ create and start event-processing """

    threading.Thread(target=self._process_events,args=(callback,)).start()
    return self._stop
