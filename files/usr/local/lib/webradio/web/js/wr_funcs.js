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
  Show message in message-area
*/

showMsg=function(text,time) {
  $("#msgarea").text(text);
  setTimeout(function() {
               $("#msgarea").empty();
             }, time);
};

/**
   Query channels and create content
*/

getChannels=function() {
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
  Switch to given channel (data should be {'nr': value})
*/

function radio_play_channel(data) {
  $.getJSON('/api/radio_play_channel',data,
    function(channel) {
      openTab(null,'wr_play');
      $('#wr_play_link').addClass('menu_active');
      if (channel.logo) {
        $('#wr_play_logo').attr('src',channel.logo);
        $('#wr_play_name').empty();
      } else {
        $('#wr_play_logo').attr('src','/images/default.png');
        $('#wr_play_name').html(channel.name);
      }
    }
  );
};

/**
  Setup SSE
*/

setup_SSE=function() {
  if (!!window.EventSource) {
    var source = new EventSource('/get_events');
    source.addEventListener('message', function(e) {
      data = JSON.parse(e.data);
     }, false);
  }
};

/**
  Handle restart
*/

doRestart=function() {
  $.get("/api/sys_restart");
  showMsg("Restarting the application ...",2000);
};

/**
  Handle stop
*/

doStop=function() {
  $.get("/api/sys_stop");
  showMsg("Stopping the application ...",2000);
};

/**
  Handle halt
*/

doHalt=function() {
  $.get("/api/sys_halt");
  showMsg("Shutting down the system ...",2000);
};

/**
  Handle reboot
*/

doReboot=function() {
  $.get("/api/sys_reboot");
  showMsg("Rebooting the system ...",2000);
};

/**
  turn radio on
*/

function radio_on() {
  $.get("/api/radio_on");
};

/**
  turn radio off
*/

function radio_off() {
  $.get("/api/radio_off");
};

/**
  toggle radio-state
*/

function radio_toggle() {
  $.get("/api/radio_toggle");
};

/**
  toggle mute
*/

function vol_mute_toggle() {
  $.get("/api/vol_mute_toggle");
};

/**
  toggle recording
*/

function rec_toggle() {
  $.get("/api/rec_toggle");
  // toggle solid/regular btn
  $('#wr_rec_btn').toggleClass('fas').toggleClass('far');
};

