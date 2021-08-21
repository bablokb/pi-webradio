API-Definition
==============

The API consists of the web API (public API), internal API for internal use,
and events.

Web API
-------

| api                     | description             | class       | status |
|-------------------------|-------------------------|-------------|--------|
| get_api_list            | return API-list         | Api         |   Ok   |
|-------------------------|-------------------------|-------------|--------|
| get_version             | return version number   | WebRadio    |   Ok   |
| sys_restart             | restart application     | WebRadio    |   Ok   |
| sys_stop                | stop application        | WebRadio    |   Ok   |
| sys_reboot              | reboot system           | WebRadio    |   Ok   |
| sys_halt                | shutdown system         | WebRadio    |   Ok   |
|-------------------------|-------------------------|-------------|--------|
| radio_state             | return current state    | Radio       |        |
| radio_on                | play current station    | Radio       |   Ok   |
| radio_off               | stop playing            | Radio       |   Ok   |
| radio_pause             | pause playing           | Radio       |   Ok   |
| radio_resume            | resume playing          | Radio       |   Ok   |
| radio_toggle            | toggle playing          | Radio       |   Ok   |
| radio_get_channels      | return list of channels | Radio       |   Ok   |
| radio_get_channel       | return channel          | Radio       |   Ok   |
| radio_play_channel(nr)  | switch to given channel | Radio       |   Ok   |
| radio_play_next         | switch to next channel  | Radio       |   Ok   |
| radio_play_prev         | switch to prev channel  | Radio       |   Ok   |
|-------------------------|-------------------------|-------------|--------|
| vol_up(by)              | increase volume         | Mpg123      |   Ok   |
| vol_down(by)            | decrease volume         | Mpg123      |   Ok   |
| vol_set(val)            | set volume              | Mpg123      |   Ok   |
| vol_mute_on             | mute                    | Mpg123      |   Ok   |
| vol_mute_off            | restore last vol setting| Mpg123      |   Ok   |
| vol_mute_toggle         | toggle mute             | Mpg123      |   Ok   |
|-------------------------|-------------------------|-------------|--------|
| rec_start               | start recording         | Recorder    |   Ok   |
| rec_stop                | stop  recording         | Recorder    |   Ok   |
| rec_toggle              | toggle recording        | Recorder    |   Ok   |
|-------------------------|-------------------------|-------------|--------|
| player_mode_start       | start player mode       | WebRadio    |   I    |
| player_mode_exit        | leave player mode       | WebRadio    |   I    |
| player_mode_toggle      | toggle player mode      | WebRadio    |   Ok   |
| player_play_file(fname) | play selected file      | Player      |   Ok   |
| player_play_dir(dir)    | play all files in dir   | Player      |        |
| player_select_dir(dir)  | select directory        | Player      |   Ok   |
| player_stop             | stop playing            | Player      |   Ok   |
| player_pause            | pause playing           | Player      |   Ok   |
| player_resume           | resume playing          | Player      |   Ok   |
| player_toggle           | toggle playing          | Player      |   Ok   |
| player_delete           | delete selected file    | Player      |        |
|-------------------------|-------------------------|-------------|--------|
| get_events              | poll SSE                | WebServer   |   Ok   |
| publish_state           | publish state change    | WebServer   |        |
|-------------------------|-------------------------|-------------|--------|

Legend:

  - Ok: implemented and tested
  - I:  implemented


Notes
-----

  - All APIs use GET-requests except `publish_state`
  - Query-parameters are given in parenthesis, they are optional if
    sensible defaults exist


Internal API
------------

The webserver prevents the execution of API starting with an underscore.

| api                     | description             | class       | status |
|-------------------------|-------------------------|-------------|--------|
| _push_event(event)      | publish event           | RadioEvents |   Ok   |
| _add_consumer(id)       | register as an consumer | RadioEvents |   Ok   |
| _del_consumer(id)       | remove event-consumer   | RadioEvents |   Ok   |
|-------------------------|-------------------------|-------------|--------|


Events
------

Events are used to distribute information to clients. Clients must use the
API `get_events` to subscribe to events.

Every event is a json-structure in the format

    event: {'type': t, 
            'value': val,
            'text': text}

The format of the value (val) is specific to the type of the event. The
`text'-value is a formatted version of the event, and will hopefully be
i18n-enabled in the future.

You can use the commandline-client to subscribe to events and then use
another client to execute various APIs. You can also search the source-code
for `_push_event`.
