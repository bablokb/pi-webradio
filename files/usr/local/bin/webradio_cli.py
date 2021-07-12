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

import locale, os, sys
from   argparse import ArgumentParser

# --- application imports   --------------------------------------------------

sys.path.append(os.path.join(
  os.path.dirname(sys.argv[0]),"../lib"))

from webradio import RadioClient

# --- application imports   --------------------------------------------------

sys.path.append(os.path.join(
  os.path.dirname(sys.argv[0]),"../lib"))

from webradio import RadioClient

# --- helper class for options   --------------------------------------------

class Options(object):
  pass

# --- cmdline-parser   ------------------------------------------------------

def get_parser():
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
    dest='inter', default=False,
    help="interactive mode (read APIs from stdin)")

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

# --- main program   ----------------------------------------------------------

if __name__ == '__main__':

  # set local to default from environment
  locale.setlocale(locale.LC_ALL, '')

  # parse commandline-arguments
  opt_parser     = get_parser()
  options        = opt_parser.parse_args(namespace=Options)

  cli     = RadioClient(options.host[0],options.port[0])
  qstring = None
  if len(options.args):
    qstring = '&'.join(options.args)
  resp = cli.exec(options.api,qstring=qstring)
  print(resp)
