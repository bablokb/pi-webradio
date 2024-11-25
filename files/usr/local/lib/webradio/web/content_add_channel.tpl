<!--
# ----------------------------------------------------------------------------
# Web-interface for pi-webradio.
#
# This file adds new channels to the channels file
#
# Author: Johannes Derrer
# License: GPL3
#
# Website: https://github.com/bablokb/pi-webradio
#
# ----------------------------------------------------------------------------
-->
<!-- TODO make own css class for this UI -->
<div id="tab_add_channel" style="display: none" class="content_area">
  <div class="play_clock">Add a channel</div>
  <br/>
  <div class="play_clock">
    <div class="play_clock">Name</div>
    <input id="add_channel_name"/>
    <div class="play_clock">Stream url</div>
    <input id="add_channel_url"/>

    <!--  TODO not yet implemented -->
<!--  <div> Logo (png) or leave empty</div> -->
<!--  <form id="add_channel_form_logo">-->
<!--    -->
<!--  </form>-->
  </div>
  <div class="play_clock" >
    <button type="button" id="add_channel_add_button" class="play_clock" style="center">
      <span>Add</span>
    </button>
  </div>
</div>
