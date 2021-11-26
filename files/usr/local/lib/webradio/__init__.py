#!/usr/bin/python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Pi-Webradio application module. The file just imports all classes
# into the wstation namespace
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-webradio
#
# ----------------------------------------------------------------------------

from . SRBase           import Base           as Base
from . SRApi            import Api            as Api
from . SREventFormatter import EventFormatter as EventFormatter
from . SRRadioEvents    import RadioEvents    as RadioEvents
from . SRRadio          import Radio          as Radio
from . SRPlayer         import Player         as Player
from . SRRecorder       import Recorder       as Recorder
from . SRMpg123         import Mpg123         as Mpg123
from . SRWebServer      import WebServer      as WebServer
from . SRWebRadio       import WebRadio       as WebRadio
from . SRRadioClient    import RadioClient    as RadioClient
from . SRKeyController  import KeyController  as KeyController

# voice control with Vosk is optional
_have_vosk = False
try:
  from . SRVoskController  import VoskController  as VoskController
  _have_vosk = True
except:
  pass
