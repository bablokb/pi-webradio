#!/usr/bin/python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# A simple cli-client for the pi-webradio.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-webradio
#
# ----------------------------------------------------------------------------

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 8026

import locale, os, sys, json, shlex, threading
from   argparse import ArgumentParser

# --- application imports   --------------------------------------------------

sys.path.append(os.path.join(
  os.path.dirname(sys.argv[0]),"../lib"))

from webradio import RadioClient

# --- application class   ---------------------------------------------------

class RadioCli(object):

  # --- constructor   -------------------------------------------------------

  def __init__(self):
    """ constructor """

    parser = self._get_parser()
    parser.parse_args(namespace=self)
    self._cli = RadioClient(self.host[0],self.port[0])

  # --- cmdline-parser   ----------------------------------------------------

  def _get_parser(self):
    """ configure cmdline-parser """

    parser = ArgumentParser(add_help=False,description='Pi-Webradio CLI')

    parser.add_argument('-H', '--host', nargs=1,
      metavar='host', default=[DEFAULT_HOST],
      dest='host',
      help='host-mask')
    parser.add_argument('-P', '--port', nargs=1,
      metavar='port', default=[DEFAULT_PORT],
      dest='port',
      help='port the server is listening on (default: %d)' % DEFAULT_PORT)

    parser.add_argument('-i', '--interactive', action='store_true',
      dest='interactive', default=False,
      help="interactive mode (read APIs from interactive shell)")

    parser.add_argument('-k', '--keyboard', action='store_true',
      dest='keyboard', default=False,
      help="interactive mode (read APIs from interactive shell)")

    parser.add_argument('-d', '--debug', action='store_true',
      dest='debug', default=False,
      help="force debug-mode")
    parser.add_argument('-q', '--quiet', action='store_true',
      dest='quiet', default=False,
      help="don't print messages")
    parser.add_argument('-h', '--help', action='help',
      help='print this help')

    parser.add_argument('api', nargs='?', metavar='api',
      default=0, help='api name')
    parser.add_argument('args', nargs='*', metavar='name=value',
      help='api arguments')
    return parser

  # --- close connection   ------------------------------------------------------

  def close(self):
    """ close connection """

    self._cli.close()

  # --- dump output of API   ----------------------------------------------------

  def print_response(self,response):
    """ write response to stderr and stdout """

    if self.debug:
      sys.stderr.write("%d %s\n" % (response[0],response[1]))
      sys.stderr.flush()
    try:
      obj = json.loads(response[2])
      print(json.dumps(obj,indent=2,sort_keys=True))
    except:
      print("response: " + response[2])

  # --- print event   -----------------------------------------------------------

  def print_event(self,event):
    """ print event (depending on mode) """

    raw = self.debug or (not self.interactive and not self.keyboard)
    if raw:
      print(json.dumps(json.loads(event.data),indent=2,sort_keys=True))
    else:
      print(json.loads(event.data)['text'])

  # --- process single api   ----------------------------------------------------

  def process_api(self,api,args,sync=True):
    """ process a single API-call """

    qstring = None
    qstring = '&'.join(args)

    # execute api
    if api == "get_events":
      if sync:
        events = self._cli.get_events()
        for event in events:
          self.print_event(event)
      else:
        self._cli.start_event_processing(callback=self.print_event)
    else:
      # use synchronous calls for all other events
      resp = self._cli.exec(api,qstring=qstring)
      self.print_response(resp)

# --- main program   ----------------------------------------------------------

if __name__ == '__main__':

  # set local to default from environment
  locale.setlocale(locale.LC_ALL, '')

  # create client-class and parse arguments
  app = RadioCli()

  # process cmdline
  if app.api:
    app.process_api(app.api,app.args)

  # read commands from stdin
  try:
    _ = os.tcgetpgrp(sys.stdin.fileno())
  except:
    for line in sys.stdin:
      line = line.rstrip()
      if not len(line):
        break
      cmd  = shlex.split(line)
      api  = cmd[0]
      args = cmd[1:]
      app.process_api(api,args,sync=False)
    app.close()
