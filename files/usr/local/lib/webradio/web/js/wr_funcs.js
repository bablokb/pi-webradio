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
                  "onclick": "playChannel({'nr': "+channel.nr+"})"})
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

playChannel=function(data) {
  $.get('/api/radio_play_channel',data);
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

