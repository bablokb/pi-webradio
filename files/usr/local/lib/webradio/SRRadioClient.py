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

import requests
import sseclient
import http.client as httplib

class RadioClient:
  """ python-client for the webradio-api """

  # --- constructor   --------------------------------------------------------

  def __init__(self,host,port,timeout=10):
    """ constructor """

    self._host    = host
    self._port    = port
    self._request = httplib.HTTPConnection(host,port,timeout)
    self._client  = None

  # --- close request object   -----------------------------------------------

  def close(self):
    """ close internal request object """

    self._request.close()
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

  # --- set up SSE and return generator   ------------------------------------

  def get_events(self):
    """ set up SSE client and return event-queue """

    url = 'http://{0}:{1}/api/get_events'.format(self._host,self._port)
    headers = {'Accept': 'text/event-stream'}
    response = requests.get(url, stream=True, headers=headers)
    self._client = sseclient.SSEClient(response)
    return self._client.events();
