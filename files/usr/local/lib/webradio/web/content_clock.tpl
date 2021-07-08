<!--
# ----------------------------------------------------------------------------
# Web-interface for pi-webradio.
#
# This file defines the content page for the clock
#
# Source: https://codepen.io/cassidoo/pen/LJBBaw (with minor modifications)
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-webradio
#
# ----------------------------------------------------------------------------
-->

<div id="wr_clock" class="clock_container content_area">
  <div class="rim"></div>
  <div class="outer"></div>
  <div class="inner">
  </div>
  <div id="clock"></div>
</div>

<script>
(function startTime() {
    var today = new Date();
    var h = today.getHours();
    var m = today.getMinutes();
    m = checkTime(m);
    document.getElementById('clock').innerHTML =
    h + ":" + m;
    var t = setTimeout(startTime, 2000);
})();

function checkTime(i) {
  if (i < 10) {i = "0" + i};
  return i;
}
</script>
