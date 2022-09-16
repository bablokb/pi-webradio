// ---------------------------------------------------------------------------
// JS support functions.
//
// Author: Bernhard Bablok
// License: GPL3
//
// Website: https://github.com/bablokb/pi-webradio
//
// ---------------------------------------------------------------------------


/**
   local state. This is partly propagated to the server, and updated from the
   server through events.
*/

function init_state() {
  $(".tablink").removeClass("menu_active");     // deactivate everything
  $(".tablink").addClass("menu_disabled");      // disable    everything
  wr_state = {
    'webgui': {
      'tabid': 'tab_clock'
    },
    'mode':     null,
    'radio':    {
      'last_channel': null
    },
    'player': {
      'last_dir': null,
      'last_file': null,
      'last_index': -1,
      'time': [null,null]
    }
  };
  wr_wait = true;
  wait_for_server();
}

wr_wait = false;
function wait_for_server() {
  if (wr_wait) {
    showMsg("waiting for server ...",1000);
    setTimeout(wait_for_server,5000);
  }
};

init_state();
wr_file2index = {};

/**
  Timer-function for elapsed playing time

  This is not exact due to multiple reasons, e.g. server playing the file
  and client showing elapsed-time, elapsed time lost when toggling pause.
*/
wr_isPause = false;
wr_update_play_time_id = null;
function update_play_time(force=false) {
  if (!wr_isPause || force) {
    // update elapsed time and display
    wr_state.player.time[0] += 1;
    h = ~~(wr_state.player.time[0] / 3600);
    m = ~~((wr_state.player.time[0]-h*3600) / 60);
    s = Math.round(wr_state.player.time[0] -h*3600 - m*60);
    if (h>0) {
      elapsed = formatTime(h)+':'+formatTime(m)+':'+formatTime(s);
    } else {
      elapsed = formatTime(m)+':'+formatTime(s);
    }
    $("#wr_time_cur").text(elapsed);
    elapsed_pc = 100*wr_state.player.time[0]/wr_state.player.time[1];
    $("#wr_time_range").val(elapsed_pc);
    $("#wr_time_range").css("background-size",elapsed_pc+"% 100%");
  }
}


/**
  Tab navigation
*/

currentTab = 'tab_clock';

function openTab(tabId,data) {
  if (!wr_state.mode) {
    // state is initial, not updated from server
    return;
  }
  if (tabId === wr_state.webgui.tabid) {     // nothing to do
    return;
  } else {
    wr_state.webgui.tabid = tabId;
  }

  // change styles of menu+tab
  $(".content_area").hide();                    // hide everything
  $(".tablink").removeClass("menu_active");     // deactivate everything
  $("#"+tabId).show();                          // show selected tab
  $("#"+tabId+"_link").addClass("menu_active"); // style as active

  // execute event-handler
  if (window["on_open_"+tabId]) {
    window["on_open_"+tabId](data);
  }

  // update new state
  if (data !== 'sys') {
    $.post('/api/update_state',JSON.stringify(wr_state));
  }
};

/**
   handler for play-tab
*/

function on_open_tab_play(internal=false) {
  if (wr_state.mode == "player") {
    $('#wr_rec_btn').hide();
    $('#wr_radio').hide();
    $('#wr_player').show();
    $('#wr_time').show();
  } else {
    $('#wr_rec_btn').show();
    $('#wr_radio').show();
    $('#wr_player').hide();
    $('#wr_time').hide();
  }

  if (internal) {
    return;
  }

  // open of tab either from user, or from event, so just
  // play current file/current channel
  if (wr_state.mode == "player") {
    player_play_file({'file': null});
  } else {
    // play current channel
    radio_play_channel({'nr': 0});
  }
};

/**
   handler for files-tab
*/

function on_open_tab_files() {
  if (!wr_state.player.last_dir) {
    // get directory for server's current-directory
    player_select_dir({'dir': '.'});
    return;
  } else {
    scroll_to_current_file();
  }
};

/**
   Scroll to current file
*/

function scroll_to_current_file() {
  // scroll to current file
  if (wr_state.player.last_index > -1) {
    $("#file_list").scrollTop(0);
    $('#file_list').stop().animate({
      'scrollTop': $('#f_'+wr_state.player.last_index).offset().top},
      800, 'swing');
  } else {
    $("#file_list").scrollTop(0);
  }
}

/**
  Update functions for all clocks
*/

function startTime() {
  var today = new Date();
  var h = today.getHours();
  var m = today.getMinutes();
  h = formatTime(h);
  m = formatTime(m);
  $('.clock').text(h + ":" + m);
  var t = setTimeout(startTime, 2000);
};

/**
  Format digits
*/

function formatTime(i) {
  if (i < 10) {i = "0" + i};
  return i;
}

/**
  Show message in message-area
*/

function showMsg(text,time) {
  $("#msgarea").text(text);
  setTimeout(function() {
               $("#msgarea").empty();
             }, time);
};


/**
  Add event to info-area
*/


function addInfo(txt) {
  var info_div = $('#wr_radio');
  info_div.append('<div>'+txt+'</div>');
  shouldScroll = false;
  while (!shouldScroll) {
    shouldScroll = info_div[0].scrollTop +
      info_div[0].clientHeight === info_div[0].scrollHeight;
    if (!shouldScroll) {
      info_div.find(':first-child').remove();
    } else {
      break;
    }
  }
};

/**
  Update id3-tags
*/

function update_id3_tags() {
  $.each(['artist','title','album','comment'],function(i,tag) {
      $('#wr_'+tag).text(wr_state.player.file_info[tag]);
    }) 
}

/**
  Setup SSE
*/

function get_events() {
  if (!!window.EventSource) {
    var source = new ReconnectingEventSource('/api/get_events',
                                             {max_retry_time: 5000});
    source.addEventListener('message', function(e) {
      data = JSON.parse(e.data);
      if (['icy_meta', 'icy_name'].includes(data.type)) {
        addInfo(data.text);
      } else {
        // window["handle_event_"+data.type]?.(data.value);
        if (window["handle_event_"+data.type]) {
          window["handle_event_"+data.type](data.value);
        } else if (data.type !== "keep_alive") {
          console.log('ignoring event: ', data);
        }
      }
     }, false);
  }
};

function handle_event_state(data) {
  var update = false;
  // only update selected fields
  if (data.webgui) {
    if (data.webgui.tabid) {
      update = wr_state.webgui.tabid !== data.webgui.tabid;
    }
  }
  if (data.mode) {
    if (!wr_state.mode) {
      wr_wait = false;                             // stop waiting message
      $(".tablink").removeClass("menu_disabled");  // enable everything
    }
    wr_state.mode = data.mode;
  }
  if (data.player && data.player.time) {
    wr_state.player.time[1] = data.player.time[1];
    $("#wr_time_tot").text(data.player.time[2]);
  }
  // open tab according to state
  if (update) {
    openTab(data.webgui.tabid);
  }
}

function handle_event_rec_start(data) {
  // toggle solid/regular btn
  $('#wr_rec_btn').removeClass('fas').addClass('far');
  showMsg("Recording "+data.name+" for "+data.duration+"min",2000);
}

function handle_event_rec_stop(data) {
  $('#wr_rec_btn').removeClass('far').addClass('fas');
  showMsg("Recording finished. File: "+data.file+", duration: "+
          data.duration+"min",5000);
}

function handle_event_play(file) {

  // start timer for update of elapsed-time
  clearInterval(wr_update_play_time_id);
  wr_isPause = false;
  wr_update_play_time_id = setInterval(update_play_time,1000);

  // enable pause-button
  $('#wr_pause_btn').removeClass('far').addClass('fas').prop("disabled", false);

  // update state
  if (wr_state.mode === 'player') {
    wr_state.player.last_file = file;
    // update highlight
    if (wr_state.player.last_index > -1) {
      $('#f_'+wr_state.player.last_index).removeClass('file_item_selected');
    }
    wr_state.player.last_index = wr_file2index[file];
    $('#f_'+wr_state.player.last_index).addClass('file_item_selected');
    cover_url = '/api/player_get_cover?dir='+encodeURIComponent(
          wr_state.player.last_dir);
    $('#wr_play_logo').attr('src',cover_url);
  }
}

function handle_event_pause(data) {
  wr_isPause = true;
  $('#wr_pause_btn').removeClass('fas').addClass('far');
}

function handle_event_eof(data) {
  if (wr_update_play_time_id) {
    clearInterval(wr_update_play_time_id);
    wr_update_play_time_id = null;
  }
  $('#wr_radio').empty();
  $('#wr_pause_btn').removeClass('far').addClass('fas').prop("disabled", true);
  if (data.last) {
    if (wr_state.mode == 'radio') {
      openTab('tab_channels');
    } else {
      openTab('tab_files');
    }
  }
}

function handle_event_radio_play_channel(data) {
  if (data.nr !== wr_state.radio.last_channel) {
    wr_state.radio.last_channel = data.nr;
    update_channel_info(data);
  }
}

function handle_event_dir_select(data) {
  if (wr_state.player.last_dir !== data) {
    player_select_dir({'dir': data});
  }
}

function handle_event_file_info(data) {
  if (!wr_update_play_time_id) {
    wr_state.player.time[0] = 0;
    $("#wr_time_cur").text("00:00");
  }
  wr_state.player.time[1] = data.total;
  $("#wr_time_tot").text(data.total_pretty);

  wr_state.player.file_info = data;
  update_id3_tags();
}

function handle_event_sample(data) {
  wr_isPause = data.pause;
  wr_state.player.time[0] = ~~(data.elapsed*wr_state.player.time[1]);
  if (wr_isPause) {
    wr_state.player.time[0] -= 1;
    update_play_time(true);
  }
  if (!wr_update_play_time_id) {
    wr_update_play_time_id = setInterval(update_play_time,1000);
  }
}

/**
   Query channels and create content
*/

function getChannels() {
  $.getJSON('/api/radio_get_channels',
    function(channelInfo) {
      $.each(channelInfo,function(index,channel) {
        var item = $("#ch_0").clone(true).attr({"id": "ch_"+channel.nr,
                  "onclick": "radio_play_channel({'nr': "+channel.nr+"})"})
          .appendTo("#channel_grid");
        if (channel.logo) {
          // create image
          item.html("<img class=\"ch_img\" src=\""+channel.logo+"\"/>");
          } else {
            // create text
          item.html("<div class=\"ch_txt\">"+channel.name+"</div>");
          }
        });
      $("#ch_0").remove();   // remove template
    });
};

/**
  show channel-info
*/

function update_channel_info(channel) {
  $('#wr_radio').empty();
  if (channel.logo) {
    $('#wr_play_logo').attr('src',channel.logo);
    $('#wr_play_name').empty();
  } else {
    $('#wr_play_logo').attr('src','/images/default.png');
    $('#wr_play_name').html(channel.name);
  }
}

/**
  update dir/file list in player-tab
*/

function update_player_list(dirInfo) {
  $(".dir_item:gt(0)").remove();              // only keep template
  $.each(dirInfo.dirs,function(index,dir) {
      var sep = "'";
      if (dir.includes(sep)) {
        sep = '"';
      }
      var item = $("#dir_0").clone(true).attr({"id": "d_"+index,
            "onclick": "player_select_dir({'dir': "+sep+dir+sep+"})"})
          .appendTo("#file_list");
      item.html("<div class=\"ch_txt\">"+dir+"</div>");
      item.show();
    });

  $(".file_item:gt(0)").remove();              // only keep template
  wr_file2index = {};
  $.each(dirInfo.files,function(index,f) {
      var file = f.fname;
      wr_file2index[file] = index;
      var sep = "'";
      if (file.includes(sep)) {
        sep = '"';
      }
      var item = $("#file_0").clone(true).attr({"id": "f_"+index,
            "style": "display:flex"})
        .appendTo("#file_list");
      item.children().eq(0).attr({"id": "f_"+index+"_pd",
            "onclick": "player_play_dir({'start': "+sep+file+sep+"})"});
      item.children().eq(1).attr({"id": "f_"+index+"_pf",
            "onclick": "player_play_file({'file': "+sep+file+sep+"})"});
      item.children().eq(2).attr({"id": "f_"+index+"_file",
            "onclick": "player_play_file({'file': "+sep+file+sep+"})"})
        .html("<div class=\"ch_txt\"></div>").text(file);
      item.children().eq(3).attr({"id": "f_"+index+"_duration",
            "onclick": "player_play_file({'file': "+sep+file+sep+"})"})
        .html("<div class=\"ch_txt\">"+f.total_pretty+"</div>");
      // highlight current file
      if (file == dirInfo.cur_file) {
        item.addClass('file_item_selected');
        wr_state.player.last_index = index;
        wr_state.player.last_file  = file;
      }
    });
}

/**
  Switch to given channel (data should be {'nr': value})
*/

function radio_play_channel(data) {
  wr_state.mode = 'radio';
  // check if channel is new
  if (data.nr != wr_state.radio.last_channel) {
    wr_state.radio.last_channel = data.nr;
  }
  $.getJSON('/api/radio_play_channel',data,
    function(channel) {
      openTab('tab_play',true);
      update_channel_info(channel);
    }
  );
};

/**
  Switch to given directory (data should be {'dir': value})
*/

function player_select_dir(data) {
  // check if directory is new
  var last_dir = wr_state.player.last_dir;
  if (data.dir != last_dir) {
    // this is a bit hacky to prevent unnecessary updates
    if (data.dir == '.') {
      // this should happen only once
      last_dir = data.dir;
    } else if (last_dir) {
      // cleanup last_dir if necessary
      last_dir = last_dir.startsWith('.') ? last_dir.slice(1) : last_dir;
    }
    if (data.dir.startsWith('/')) {
      last_dir = data.dir;
    } else if (data.dir == '..') {
      // remove last dir-part from last_dir
      last_dir =
        last_dir.substr(0,last_dir.lastIndexOf('/',last_dir.length-2)+1);
    } else if (data.dir !== '.') {
      last_dir = last_dir +
        (data.dir.endsWith('/') ? data.dir.slice(0,-1) : data.dir) + '/';
    }
    wr_state.player.last_dir = last_dir;
  } else {
    return;
  }
  $("#msgarea").text("loading directory " + data.dir + " ...");
  $.getJSON('/api/player_select_dir',data,
    function(result) {
      $("#msgarea").empty();
      update_player_list(result);
      if (data.dir == '.') {
        scroll_to_current_file();
      }
      openTab('tab_files');
    }
  );
};

/**
   play given file (data should be {'file': name})
*/

function player_play_file(data) {
  wr_state.mode = 'player';

  // tell server to start playing
  $.getJSON('/api/player_play_file',data,
    function(result) {
      // do nothing
    }
  );
  openTab('tab_play',true);
};

/**
   play dir from given file (data should be {'start': name})
*/

function player_play_dir(data) {
  wr_state.mode = 'player';
  $.getJSON('/api/player_play_dir',data,
    function(result) {
      // do nothing
    }
  );
  openTab('tab_play',true);
};

/**
  Handle restart
*/

function doRestart() {
  $.get("/api/sys_restart");
  showMsg("Restarting the application ...",2000);
  openTab('tab_clock','sys');
  init_state();
};

/**
  Handle stop
*/

function doStop() {
  $.get("/api/sys_stop");
  showMsg("Stopping the application ...",2000);
  openTab('tab_clock','sys');
  init_state();
};

/**
  Handle halt
*/

function doHalt() {
  $.get("/api/sys_halt");
  showMsg("Shutting down the system ...",2000);
  openTab('tab_clock','sys');
  init_state();
};

/**
  Handle reboot
*/

function doReboot() {
  $.get("/api/sys_reboot");
  showMsg("Rebooting the system ...",2000);
  openTab('tab_clock','sys');
  init_state();
};

/**
  turn radio/player off
*/

function audio_off() {
  if (wr_state.mode == 'player') {
    $.get("/api/player_stop");
  } else {
    $.get("/api/radio_off");
  }
};

/**
  toggle radio/player-state
*/

function audio_toggle() {
  if (wr_state.mode == 'player') {
    $.get("/api/player_toggle");
  } else {
    $.get("/api/radio_toggle");
  }
};

/**
  volume up
*/

function vol_up() {
  $.get("/api/vol_up",
        function(new_vol) {
          showMsg("volume: "+new_vol,2000);
        }
        );
};

/**
  toggle mute
*/

function vol_mute_toggle() {
  $.get("/api/vol_mute_toggle");
  $('#wr_mute_btn').toggleClass('fa-volume-mute').toggleClass('fa-volume-off');
  showMsg("toggle mute ...",2000);
};

/**
  volume up
*/

function vol_down() {
  $.get("/api/vol_down",
        function(new_vol) {
          showMsg("volume: "+new_vol,2000);
        }
        );
};

/**
  toggle recording
*/

function rec_toggle() {
  $.get("/api/rec_toggle");
};

