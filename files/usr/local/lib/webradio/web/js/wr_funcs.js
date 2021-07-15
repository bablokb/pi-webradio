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
  Tab navigation
*/

function openTab(evt, tabId) {
  // Declare all variables
  var i, content_area, tablinks;

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

  // turn radio of if not switching to channels or play
  if (!['wr_channels','wr_play'].includes(tabId)) {
    radio_off();
  }
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

showMsg=function(text,time) {
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
  shouldScroll = info_div[0].scrollTop +
        info_div[0].clientHeight === info_div[0].scrollHeight;
  if (!shouldScroll) {
    info_div.find(':first-child').remove();
    scrollToBottom(info_div[0]);
  }
};

/**
  Scroll info-area
*/

function scrollToBottom(div) {
  div.scrollTop = div.scrollHeight;
}

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

