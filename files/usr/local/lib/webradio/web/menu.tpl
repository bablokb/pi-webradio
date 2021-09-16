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

<div id="menu">
  <a class="tablink menu_active" href="#"
         onclick="openTab(event,'wr_clock')"><i class="fas fa-clock"></i></a>
  <a class="tablink" href="#"
        onclick="openTab(event,'wr_channels')">
        <i class="fas fa-broadcast-tower"></i></a>
  <a id="wr_play_link" class="tablink" href="#"
        onclick="openTab(event,'wr_play')"><i class="fas fa-play"></i></a>
  <a class="tablink" href="#"
        onclick="openTab(event,'wr_files')"><i class="fas fa-file-audio"></i></a>
  <a class="tablink" href="#"
        onclick="openTab(event,'wr_special')"><i class="fas fa-wrench"></i></a>
</div>
