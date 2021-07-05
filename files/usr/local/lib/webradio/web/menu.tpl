<!--
# ----------------------------------------------------------------------------
# Web-interface for pi-webradio.
#
# This file defines the navigation-menu
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-webradio
#
# ----------------------------------------------------------------------------
-->

<script>
function openTab(evt, tabId) {
  // Declare all variables
  var i, tabcontent, tablinks;

  // Get all elements with class="tabcontent" and hide them
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }

  // Get all elements with class="tablink" and remove the class "active"
  tablinks = document.getElementsByClassName("tablink");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }

  // Show the current tab, and add an "active" class to the link that opened the tab
  document.getElementById(tabId).style.display = "block";
  evt.currentTarget.className += " active";
}
</script>

<style>
body {margin:0}

.icon-bar {
  width: 90px;
  background-color: black;
}

.icon-bar a {
  display: block;
  text-align: center;
  padding: 16px;
  transition: all 0.3s ease;
  color: blue;
  font-size: 36px;
}

.icon-bar a:hover {
  background-color: white;
}

.active {
  background-color: #e0e0e0;
}
</style>


<div class="icon-bar">
  <a class="tablink active" href="#"
         onclick="openTab(event,'wr_clock')"><i class="fas fa-clock"></i></a>
  <a class="tablink" href="#"
        onclick="openTab(event,'wr_channels')"><i class="fas fa-broadcast-tower"></i></a>
  <a class="tablink" href="#"
        onclick="openTab(event,'wr_player')"><i class="fas fa-file-audio"></i></a>
  <a class="tablink" href="#"
        onclick="doStop()"><i class="fas fa-wrench"></i></a>
  <a class="tablink" href="#"
        onclick="doReboot()><i class="fas fa-undo"></i></a>
  <a class="tablink" href="#"
        onclick="doHalt()><i class="fas fa-power-off"></i></a>
</div>

<!--
  <a href="#"><i class="fas fa-play-circle"></i></a>
  <a href="#"><i class="fas fa-pause-circle"></i></a>
  <a href="#"><i class="fas fa-stop-circle"></i></a>
  <a href="#"><i class="fas fa-microphone-alt"></i></a>
-->