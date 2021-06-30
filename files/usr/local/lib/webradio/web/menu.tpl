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
  <a class="active" href="#"><i class="fas fa-clock"></i></a>
  <a href="#"><i class="fas fa-broadcast-tower"></i></a>
  <a href="#"><i class="fas fa-file-audio"></i></a>
  <a href="#"><i class="fas fa-wrench"></i></a>
  <a href="#"><i class="fas fa-undo"></i></a>
  <a href="#"><i class="fas fa-power-off"></i></a>
</div>


<!--
  <a href="#"><i class="fas fa-play-circle"></i></a>
  <a href="#"><i class="fas fa-pause-circle"></i></a>
  <a href="#"><i class="fas fa-stop-circle"></i></a>
  <a href="#"><i class="fas fa-microphone-alt"></i></a>
-->