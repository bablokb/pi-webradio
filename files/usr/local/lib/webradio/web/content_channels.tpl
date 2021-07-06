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

<style>
.ch_grid {
  display: grid;
  grid-gap: 15px;
  overflow: hidden;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  grid-auto-flow: dense;
}

.txt {
  background-image: linear-gradient(224deg, blue 0%, lightblue 100%);
  display: flex;
  height: 100%;
  width: 100%;
  align-items: center;
  justify-content: center;
  font-size: auto;
  color: #B0C5FF;
  text-shadow: 0 1px 1px #26145F;
}

.ch_item {
  max-height: 180px;
  max-width: 180px;
  min-height: 100px;
  min-width: 100px;
  width: inherit;
  display: flex;
  align-items: center;
  justify-content: center;
}

img {
  display: flex;
  height: auto;
  width: 100%;
  align-items: center;
  justify-content: center;
}
</style>

<div id="wr_channels" style="width: 80%; display: none" class="container tabcontent">
  <div id="channel_grid" class="ch_grid">
      <div id="ch_0" class="ch_item"></div>
  </div>
</div>

<script>
  $(document).ready(function() {
    getChannels();
  });
</script>
