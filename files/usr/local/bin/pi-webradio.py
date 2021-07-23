#!/usr/bin/python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Main application program for the pi-webradio.
#
# This program starts the application either in synchronous mode or in
# server mode. The latter is usually done from a systemd-service.
# Synchronous mode is for listing channels, direct recording and direct
# playing. Note that direct playing does not allow any interaction, so
# this feature is mainly useful for development and debugging.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-webradio
#
# ----------------------------------------------------------------------------

import locale, os, sys, signal, queue, threading
from   argparse import ArgumentParser

# --- application imports   --------------------------------------------------

sys.path.append(os.path.join(
  os.path.dirname(sys.argv[0]),"../lib"))

from webradio import *

# --- helper class for options   --------------------------------------------

class Options(object):
  pass

# --- cmdline-parser   ------------------------------------------------------

def get_parser():
  """ configure cmdline-parser """

  parser = ArgumentParser(add_help=False,description='Pi-Webradio')

  parser.add_argument('-p', '--play', action='store_true',
    dest='do_play', default=False,
    help="play radio/file (direct, no web-interface, needs channel/file as argument)")

  parser.add_argument('-l', '--list', action='store_true',
    dest='do_list', default=False,
    help="display radio-channels")

  parser.add_argument('-r', '--record', action='store_true',
    dest='do_record', default=False,
    help="record radio (direct, no webinterface, needs channel as argument)")
  parser.add_argument('-t', '--tdir', nargs=1,
    metavar='target directory', default=None,
    dest='target_dir',
    help='target directory for recordings')

  parser.add_argument('-d', '--debug', action='store_true',
    dest='debug', default=False,
    help="force debug-mode (overrides config-file)")
  parser.add_argument('-q', '--quiet', action='store_true',
    dest='quiet', default=False,
    help="don't print messages")
  parser.add_argument('-h', '--help', action='help',
    help='print this help')

  parser.add_argument('channel', nargs='?', metavar='channel',
    default=0, help='channel number/filename')
  parser.add_argument('duration', nargs='?', metavar='duration',
    default=0, help='duration of recording')
  return parser

# --- validate and fix options   ---------------------------------------------

def check_options(options):
  """ validate and fix options """

  # record needs a channel number
  if options.do_record and not options.channel:
    print("[ERROR] record-option (-r) needs channel nummber as argument")
    sys.exit(3)

# --- process events   -------------------------------------------------------

def process_events(app,options,queue):
  while True:
    ev = queue.get()
    if ev:
      if not options.quiet:
        print(ev['text'])
      queue.task_done()
      if ev['type'] == 'eof' and options.do_play:
        break
      if ev['type'] == 'sys':
        break
    else:
      break
  app.msg("pi-webradio: finished processing events")
  try:
    os.kill(os.getpid(), signal.SIGTERM)
  except:
    pass

# --- main program   ----------------------------------------------------------

if __name__ == '__main__':

  # set local to default from environment
  locale.setlocale(locale.LC_ALL, '')

  # parse commandline-arguments
  opt_parser     = get_parser()
  options        = opt_parser.parse_args(namespace=Options)
  options.pgm_dir = os.path.dirname(os.path.abspath(__file__))
  check_options(options)

  app = WebRadio(options)

  # setup signal-handler
  signal.signal(signal.SIGTERM, app.signal_handler)
  signal.signal(signal.SIGINT,  app.signal_handler)

  if options.do_list:
    if not options.quiet:
      app.msg("pi-webradio version %s" % app.api.get_version(),force=True)
    channels = app.api.radio_get_channels()
    PRINT_CHANNEL_FMT="{0:2d}: {1}"
    for channel in channels:
      print(PRINT_CHANNEL_FMT.format(channel['nr'],channel['name']))
  else:
    ev_queue = queue.Queue()
    app.api._add_consumer("main",ev_queue)
    threading.Thread(target=process_events,args=(app,options,ev_queue)).start()
    if options.do_record:
      app.api.rec_start(nr=int(options.channel),sync=True)
      app.cleanup()
    elif options.do_play:
      try:
        nr = int(options.channel)
        app.api.radio_play_channel(nr)
      except ValueError:
        app.api.player_play_file(options.channel) # assume argument is a filename
      signal.pause()
    else:
      app.run()
      signal.pause()
    app.api._del_consumer("main")
  sys.exit(0)
