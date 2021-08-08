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

import locale, os, sys, json, shlex, threading, signal, readline
from   argparse import ArgumentParser

# --- application imports   --------------------------------------------------

sys.path.append(os.path.join(
  os.path.dirname(sys.argv[0]),"../lib"))

from webradio import RadioClient, KeyController

# --- application class   ----------------------------------------------------

class RadioCli(object):

  # --- constructor   --------------------------------------------------------

  def __init__(self):
    """ constructor """

    parser = self._get_parser()
    parser.parse_args(namespace=self)
    self._cli = RadioClient(self.host[0],self.port[0],debug=self.debug)

  # --- cmdline-parser   -----------------------------------------------------

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
      help="key-control mode (maps keys to APIs)")

    parser.add_argument('-e', '--events', action='store_true',
      dest='events', default=False,
      help="start event-processing")
    parser.add_argument('-o', '--on', action='store_true',
      dest='on', default=False,
      help="turn radio on")

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

  # --- return stop-event   --------------------------------------------------

  def get_stop_event(self):
    """ return stop event """

    return self._cli.get_stop_event()

  # --- setup signal handler   ------------------------------------------------

  def signal_handler(self,_signo, _stack_frame):
    """ signal-handler for clean shutdown """

    self.msg("webradio_cli: received signal, stopping program ...")
    self.close()

  # --- close connection   ---------------------------------------------------

  def close(self):
    """ close connection """

    try:
      self._cli.close()
    except:
      pass

  # --- print message   ------------------------------------------------------

  def msg(self,text,force=False):
    """ print message """

    self._cli.msg(text,force)

  # --- dump output of API   -------------------------------------------------

  def print_response(self,response):
    """ write response to stderr and stdout """

    if self.quiet:
      return
    elif self.debug:
      sys.stderr.write("%d %s\n" % (response[0],response[1]))
      sys.stderr.flush()
    try:
      obj = json.loads(response[2])
      print(json.dumps(obj,indent=2,sort_keys=True))
    except:
      print("response: " + response[2])

  # --- print event   --------------------------------------------------------

  def handle_event(self,event):
    """ print event (depending on mode) """

    raw = self.debug or (not self.interactive and not self.keyboard)
    if raw:
      print(json.dumps(json.loads(event.data),indent=2,sort_keys=True))
    elif not self.quiet:
      ev_data = json.loads(event.data)
      if ev_data['type'] != 'keep_alive':
        print(ev_data['text'])

  # --- process single api   -------------------------------------------------

  def process_api(self,api,args=[],sync=True):
    """ process a single API-call """

    qstring = None
    qstring = '&'.join(args)

    # execute api
    if api == "get_events":
      if sync:
        events = self._cli.get_events()
        for event in events:
          self.handle_event(event)
      else:
        self._cli.start_event_processing(callback=self.handle_event)
    else:
      # use synchronous calls for all other events
      resp = self._cli.exec(api,qstring=qstring)
      self.print_response(resp)

  # --- process stdin   ------------------------------------------------------

  def process_stdin(self):
    """ check for stdin and process commands """

    # test for stdin
    try:
      _ = os.tcgetpgrp(sys.stdin.fileno())
      self.msg("webradio_cli: no stdin ...")
      return
    except:
      pass

    # read commands from stdin
    for line in sys.stdin:
      line = line.rstrip()
      if not len(line):
        break
      cmd  = shlex.split(line)
      self.process_api(cmd[0],cmd[1:],sync=False)

  # --- completer for readline   ---------------------------------------------

  def completer(self,text,state):
    """ implement completer """

    self.msg("RadioCli: completer(%s,%d)" % (text,state))
    if state == 0:
      # buffer list of hits
      if text in self._cli.API_LIST:
        self._completions = [text]
      else:
        self._completions = [api for api in self._cli.API_LIST
                             if api.startswith(text)]

    if state < len(self._completions):
      self.msg("RadioCli: returning %s" % self._completions[state])
      return self._completions[state]
    else:
      return True

  # --- run application   ----------------------------------------------------

  def run(self):
    """ run application """

    # setup signal-handler
    signal.signal(signal.SIGTERM, self.signal_handler)
    signal.signal(signal.SIGINT,  self.signal_handler)

    # process special options
    if self.events:
      self.process_api("get_events",sync=False)
    if self.on:
      self.process_api("radio_on")

    # process cmdline
    if self.api:
      self.process_api(self.api,self.args,
                      sync=not (self.keyboard or self.interactive))

    # process stdin (if available)
    self.process_stdin()

    # process keyboard / interactive input
    if self.keyboard:
      kc = KeyController(self.get_stop_event(),self.debug)
      for api in kc.api_from_key():
        self.process_api(api[0],api[1:],sync=False)
        if api[0] == 'sys_stop':
          break
    elif self.interactive:
      readline.set_completer(lambda text,state: self.completer(text,state))
      readline.parse_and_bind("tab: complete")
      while True:
        line = input("webradio > ").strip()
        if not len(line):
          continue
        elif line in ['q','Q','quit','Quit']:
          break
        api  = shlex.split(line)
        self.process_api(api[0],api[1:],sync=False)
        if api[0] == 'sys_stop':
          break

    self.close()

# --- main program   ---------------------------------------------------------

if __name__ == '__main__':

  # set local to default from environment
  locale.setlocale(locale.LC_ALL, '')

  # create client-class and parse arguments
  app = RadioCli()
  app.run()
