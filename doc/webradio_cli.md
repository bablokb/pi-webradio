Webradio Commandline-Client
===========================

The webradio client is a python-implemented commandline client. Besides
being a showcase and a test-tool for the [web-API](API.md), it supports
the following modes of operation:

  - direct api execution, e.g.: `webradio_cli.py radio_on`
  - process apis from stdin, e.g.:

      echo -e "radio_on\n radio_play_channel nr=7" | webradio_cli.py

  - keyboard control, e.g.: `webradio_cli.py -k -e -o`
  - interactive shell-mode with readline-support and tab-completion, e.g:
    `webradio_cli.py -i -e -o`

For a complete list of options, run `webradio_cli.py -h`.


Key-Mapping
-----------

The current implementation supports the following keys:


|Key        | API                 |
|-----------|---------------------|
|KEY_1      | radio_play_channel  |
|KEY_2      | radio_play_channel  |
|KEY_3      | radio_play_channel  |
|KEY_4      | radio_play_channel  |
|KEY_5      | radio_play_channel  |
|KEY_6      | radio_play_channel  |
|KEY_7      | radio_play_channel  |
|KEY_8      | radio_play_channel  |
|KEY_9      | radio_play_channel  |
|KEY_0      | radio_play_channel  |
|KEY_D      | player_play_dir     |
|KEY_F      | player_play_file    |
|KEY_I      | radio_state         |
|KEY_O      | radio_toggle        |
|KEY_P      | player_mode_toggle  |
|KEY_Q      | sys_stop            |
|KEY_R      | rec_toggle          |
|KEY_L      | radio_get_channels  |
|KEY_M      | vol_mute_toggle     |
|KEY_LEFT   | radio_play_prev     |
|KEY_RIGHT  | radio_play_next     |
|KEY_UP     | vol_up              |
|KEY_DOWN   | vol_down            |
|KEY_ENTER  | player_select       |
|-----------|---------------------|


Extending the Client
--------------------

For your own client, you can take `bin/webradio_cli.py` as a basis. But
instead of duplicating code, it is better to extend the class `RadioCli`
from that file. See the file `bin/webradio_pirate_audio.py` for an
example. The latter extends the class and overwrites two methods to
implement the logo-display on the small integrated display of the
Pirate-Audio hat.
