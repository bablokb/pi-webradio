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
      self._consumers[id] = queue
      try:
        ev = {'type': 'version','value': self._api.get_version()}
        ev['text'] = self._formatter.format(ev)
        queue.put_nowait(ev)
      except:
        del self._consumers[id]

  # --- remove a consumer   --------------------------------------------------

  def del_consumer(self,id):
    """ delete a consumer from the list of consumers """

    if id in self._consumers:
      self._consumers[id].put(None)
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
      for consumer in self._consumers.values():
        try:
          consumer.put(event)
        except queue.Full:
          # remove stale consumers
          del self._consumers[consumer['id']]
      self._input_queue.task_done()

    self.msg("RadioEvents: stopping event-processing")
    for consumer in self._consumers.values():
      consumer.put(None)
    self.msg("RadioEvents: event-processing finished")
