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
  <a id="tab_clock_link" class="tablink menu_active" href="#"
         onclick="openTab('tab_clock')"><i class="fas fa-clock"></i></a>
  <a id="tab_channels_link" class="tablink" href="#"
        onclick="openTab('tab_channels')">
        <i class="fas fa-broadcast-tower"></i></a>
  <a id="tab_play_link" class="tablink" href="#"
        onclick="openTab('tab_play')"><i class="fas fa-play"></i></a>
  <a id="tab_files_link" class="tablink" href="#"
        onclick="openTab('tab_files')"><i class="fas fa-file-audio"></i></a>
  <a id="tab_add_channel_link" class="tablink" href="#"
        onclick="openTab('tab_add_channel')"><i class="fas fa-folder-plus"></i></a>
  <a id="tab_special_link" class="tablink" href="#"
        onclick="openTab('tab_special')"><i class="fas fa-wrench"></i></a>
</div>
