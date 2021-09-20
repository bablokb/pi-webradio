// ---------------------------------------------------------------------------
// JS support functions.
//
// Author: Bernhard Bablok
// License: GPL3
//
// Website: https://github.com/bablokb/pi-webradio
//
// ---------------------------------------------------------------------------


wr_state = {
  'webgui': {
    'tabid': 'wr_clock'
  },
  'mode':     null,
  'radio':    {
    'last_channel': null,
  },
  'player': {
    'last_dir': null,
    'last_file': null,
  }
};

/**
  Tab navigation
*/

currentTab = 'wr_clock';

function openTab(evt, tabId) {
  // Declare all variables
  var i, content_area, tablinks;

  if (tabId === wr_state.webgui.tabid) {   // nothing to do
    return;
  } else {
    wr_state.webgui.tabid = tabId;
  }

  // Get all elements with class="content_area" and hide them
  content_area = document.getElementsByClassName("content_area");
  for (i = 0; i < content_area.length; i++) {
    content_area[i].style.display = "none";
  }

  // Get all elements with class="tablink" and remove the class "menu_active"
  tablinks = document.getElementsByClassName("tablink");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" menu_active", "");
  }

  // Show the current tab, and add an "menu_active" class to the link that opened the tab
  document.getElementById(tabId).style.display = "block";
  if (evt) {
    evt.currentTarget.className += " menu_active";
  }

  if (tabId == 'wr_play' && !wr_state.mode) {
    // initial state: play last channel
    radio_play_channel({'nr': 0});
  } else if (tabId == 'wr_files' && !wr_state.player.last_dir) {
    // get directory for server's current-directory
    player_select_dir({'dir': '.'});
  }

  // publish new state
  $.post('/api/publish_state',JSON.stringify(wr_state));
};

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
  var info_div = $('#wr_infos');
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
  Setup SSE
*/

function get_events() {
  if (!!window.EventSource) {
    var source = new EventSource('/api/get_events');
    source.addEventListener('message', function(e) {
      data = JSON.parse(e.data);
      if (['icy_meta', 'icy_name','id3'].includes(data.type)) {
        addInfo(data.text);
      } else {
        // window["handle_event_"+data.type]?.(data.value);
        if (window["handle_event_"+data.type]) {
          window["handle_event_"+data.type](data.value);
        } else {
          console.log('ignoring event: ', data);
        }
      }
     }, false);
  }
};

function handle_event_state(data) {
  if (data.webgui) {
    // current support is limited to tabid
    if (data.webgui.tabid) {
      openTab(null,data.webgui.tabid);
    }
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

function handle_event_play(data) {
  $('#wr_play_btn').removeClass('fas').addClass('far');
  $('#wr_pause_btn').removeClass('far').addClass('fas').prop("disabled", false);
  $('#wr_off_btn').removeClass('far').addClass('fas');
}

function handle_event_pause(data) {
  $('#wr_play_btn').removeClass('far').addClass('fas');
  $('#wr_pause_btn').removeClass('fas').addClass('far');
}

function handle_event_eof(data) {
  $('#wr_infos').empty();
  $('#wr_play_btn').removeClass('far').addClass('fas');
  $('#wr_pause_btn').removeClass('far').addClass('fas').prop("disabled", true);
  $('#wr_off_btn').removeClass('fas').addClass('far');
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
  $('#wr_infos').empty();
  $('#wr_play_link').addClass('menu_active');
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
      var item = $("#dir_0").clone(true).attr({"id": "d_"+index,
            "onclick": "player_select_dir({'dir': '"+dir+"'})"})
          .appendTo("#file_list");
      item.html("<div class=\"ch_txt\">"+dir+"</div>");
      item.show();
    });
  $(".file_item:gt(0)").remove();              // only keep template
  $.each(dirInfo.files,function(index,file) {
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
        .html("<div class=\"ch_txt\">"+dirInfo.dur[index][1]+"</div>");
      // highlight current file
      if (file == dirInfo.cur_file) {
        item.addClass('file_item_selected');
      }
    });
  $("#file_list").scrollTop(0);
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
      openTab(null,'wr_play');
      $('#wr_rec_btn').show();
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
    } else {
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
  $.getJSON('/api/player_select_dir',data,
    function(result) {
      openTab(null,'wr_files');
      update_player_list(result);
    }
  );
};

/**
   play given file (data should be {'file': name})
*/

function player_play_file(data) {
  wr_state.mode = 'player';
  $('#wr_infos').empty();
  $.getJSON('/api/player_play_file',data,
    function(result) {
      showMsg("playing " + result.name,2000);
    }
  );
  $('#wr_rec_btn').hide();
  openTab(null,'wr_play');
};

/**
   play dir from given file (data should be {'start': name})
*/

function player_play_dir(data) {
  wr_state.mode = 'player';
  $('#wr_infos').empty();
  $.getJSON('/api/player_play_dir',data,
    function(result) {
      showMsg("playing directory",2000);
    }
  );
  $('#wr_rec_btn').hide();
  openTab(null,'wr_play');
};

/**
  Handle restart
*/

function doRestart() {
  $.get("/api/sys_restart");
  showMsg("Restarting the application ...",2000);
};

/**
  Handle stop
*/

function doStop() {
  $.get("/api/sys_stop");
  showMsg("Stopping the application ...",2000);
};

/**
  Handle halt
*/

function doHalt() {
  $.get("/api/sys_halt");
  showMsg("Shutting down the system ...",2000);
};

/**
  Handle reboot
*/

function doReboot() {
  $.get("/api/sys_reboot");
  showMsg("Rebooting the system ...",2000);
};

/**
  turn radio/player on
*/

function audio_on() {
  if (wr_state.mode == 'player') {
    $.get("/api/player_play");
  } else {
    $.get("/api/radio_on");
  }
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

