#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Pi-Webradio: implementation of class RadioEvents
#
# The class RadioEvents multiplexes events to multiple consumers.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-webradio
#
# -----------------------------------------------------------------------------

import queue
import threading

from webradio import Base
from webradio import EventFormatter

class RadioEvents(Base):
  """ Multiplex events to consumers """

  def __init__(self,app):
    """ initialization """

    self._api         = app.api
    self.debug        = app.debug
    self._stop_event  = app.stop_event
    self._input_queue = queue.Queue()
    self._lock        = threading.Lock()
    self._consumers   = {}
    self._formatter   = EventFormatter()
    self.register_apis()
    threading.Thread(target=self._process_events).start()

  # --- register APIs   ------------------------------------------------------

  def register_apis(self):
    """ register API-functions """

    self._api._push_event   = self.push_event
    self._api._add_consumer = self.add_consumer
    self._api._del_consumer = self.del_consumer

  # --- push an event to the input queue   -----------------------------------

  def push_event(self,event):
    """ push event to the  input queue """

    self._input_queue.put(event)

  # --- add a consumer   -----------------------------------------------------

  def add_consumer(self,id,queue):
    """ add a consumer to the list of consumers """

    if not id in self._consumers:
      self.msg("RadioEvents: adding consumer with id %s" % id)
      with self._lock:
        self._consumers[id] = queue
      try:
        ev = {'type': 'version','value': self._api.get_version()}
        ev['text'] = self._formatter.format(ev)
        queue.put_nowait(ev)
      except:
        with self._lock:
          del self._consumers[id]

  # --- remove a consumer   --------------------------------------------------

  def del_consumer(self,id):
    """ delete a consumer from the list of consumers """

    if id in self._consumers:
      self._consumers[id].put(None)
      with self._lock:
        del self._consumers[id]

  # --- multiplex events   ---------------------------------------------------

  def _process_events(self):
    """ pull events from the input-queue and distribute to the consumer queues """

    self.msg("RadioEvents: starting event-processing")
    while not self._stop_event.is_set():
      try:
        event = self._input_queue.get(block=True,timeout=1)   # block 1s
      except queue.Empty:
        continue
      self.msg("RadioEvents: received event: %r" % (event,))
      event['text'] = self._formatter.format(event)
      stale_consumers = []
      for consumer in self._consumers.values():
        try:
          consumer.put_nowait(event)
        except queue.Full:
          stale_consumers.append(consumer['id'])
      self._input_queue.task_done()

      # delete stale consumers
      with self._lock:
        for id in stale_consumers:
          del self._consumers[id]

    self.msg("RadioEvents: stopping event-processing")
    for consumer in self._consumers.values():
      consumer.put(None)
    self.msg("RadioEvents: event-processing finished")
