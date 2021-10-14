<!--
# ----------------------------------------------------------------------------
# Web-interface for pi-webradio.
#
# This file defines the content page for the radio-channels
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-webradio
#
# ----------------------------------------------------------------------------
-->

<div id="tab_channels" style="display: none" class="content_area">
  <div id="channel_grid" class="ch_grid">
      <div id="ch_0" class="ch_item"></div>
  </div>
</div>

<script>
  $(document).ready(function() {
    getChannels();
  });
</script>
