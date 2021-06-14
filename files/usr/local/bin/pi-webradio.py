#!/usr/bin/python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Web-interface for the pi-webradio project
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-webradio
#
# ----------------------------------------------------------------------------

VERSION      = 0.1
DEFAULT_PORT = 8026

# --- system  imports   ------------------------------------------------------

import os, sys
from argparse import ArgumentParser

# --- application imports   --------------------------------------------------

sys.path.append(os.path.join(
  os.path.dirname(sys.argv[0]),"../lib","pi-webradio"))

import SRWeb

# --- helper class for options   --------------------------------------------

class Options(object):
  pass

# --- commandline-parser   --------------------------------------------------

def get_parser():
  parser = ArgumentParser(add_help=False,
    description='Webinterface for the pi-webradio project')

  parser.add_argument('-H', '--host', nargs=1,
    metavar='host', default=['0.0.0.0'],
    dest='host',
    help='host-mask')
  parser.add_argument('-P', '--port', nargs=1,
    metavar='port', default=[DEFAULT_PORT],
    dest='port',
    help='port the server is listening on (default: %d)' % DEFAULT_PORT)

  parser.add_argument('-d', '--debug',
    dest='debug', default=False, action='store_true',
    help='start in debug-mode')

  parser.add_argument('-h', '--help', action='help',
    help='display this help')
  return parser

# --- main program   --------------------------------------------------------

if __name__ == '__main__':
  # read options
  opt_parser = get_parser()
  options = opt_parser.parse_args(namespace=Options)
  options.version = VERSION
  options.pgm_dir = os.path.dirname(os.path.abspath(__file__))
  if options.debug:
    print("DEBUG: running version:   %s" % options.version)
    print("DEBUG: pgm_dir directory: %s" % options.pgm_dir)

  # start server
  server = SRWeb.SRWeb(options)
  server.run()
