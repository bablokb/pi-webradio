API-Definition
==============

Non-public APIs start with an underscrore and cannot be called via
the webinterface.

Legend:

  - Ok: implemented and tested
  - I:  implemented

| api                     | description             | class       | status |
|-------------------------|-------------------------|-------------|--------|
| get_version             | return version number   | WebRadio    |   Ok   |
| sys_restart             | restart application     | WebRadio    |   Ok   |
| sys_stop                | stop application        | WebRadio    |   Ok   |
| sys_reboot              | reboot system           | WebRadio    |   Ok   |
| sys_halt                | shutdown system         | WebRadio    |   Ok   |
|-------------------------|-------------------------|-------------|--------|
| radio_on                | play current station    | Radio       |   Ok   |
| radio_off               | stop playing            | Radio       |   Ok   |
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
| player_play_file(file)  | play selected file      | Player      |   Ok   |
| player_play_dir(dir)    | play all files in dir   | Player      |        |
| player_stop             | stop playing            | Player      |        |
| player_pause            | pause playing           | Player      |        |
| player_toggle           | toggle playing          | Player      |        |
| player_select           | select file for playing | Player      |        |
| player_next             | select next file        | Player      |        |
| player_prev             | select prev file        | Player      |        |
| player_delete           | delete selected file    | Player      |        |
|-------------------------|-------------------------|-------------|--------|
| _push_event(event)      | publish event           | RadioEvents |   Ok   |
| _add_consumer(id,queue) | register as an consumer | RadioEvents |   Ok   |
| _del_consumer(id)       | remove event-consumer   | RadioEvents |   Ok   |
|-------------------------|-------------------------|-------------|--------|
| get_events              | poll SSE                | WebServer   |        |
|-------------------------|-------------------------|-------------|--------|

    event: {'type': t, 
            'value': val}

`val` is type-specific
