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

<style>
.container {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.rim {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 300px;
  height: 300px;
  border: 20px solid #000;
  border-radius: 50%;
  animation: shift-rim 16s infinite;
  z-index: 10;
}

.outer {
  width: 300px;
  height: 300px;
  background: linear-gradient(to bottom, rgba(0,0,0,1) 0%, rgba(8,8,71,1) 100%);
  border: 10px solid #1A23F2;
  border-radius: 50%;
  box-sizing: border-box;
  filter: blur(2px);
  animation: shift 16s infinite;
  &::before {
    display: block;
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 104%;
    height: 104%; 
    border: 1px solid #fff;
    box-sizing: border-box;
    border-radius: 50%;
    opacity: 1;
    filter: blur(2px);
  }
}

.inner {
  position: absolute;
  top: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 200px;
  height: 200px;
    background: linear-gradient(to bottom, rgba(8,8,71,1) 0%, rgba(0,0,0,1) 100%);
  border: 8px solid #1A23F2;
  border-radius: 50%;
  box-sizing: border-box;
  box-shadow: 0 10px 20px 10px #000;
  filter: blur(1px);
  animation: shift-inner 16s infinite;
    &::before {
    display: block;
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 100%;
    height: 100%; 
    border: 8px solid #000;
    box-sizing: border-box;
    border-radius: 50%;
    opacity: 1;
    filter: blur(5px);
  }
   &::after {
    display: block;
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 105%;
    height: 105%; 
    border: 1px solid #6AAEE9;
    box-sizing: border-box;
    border-radius: 50%;
    opacity: 1;
    filter: blur(3px);
  }
}

#clock {
  position: absolute;
  top: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  height: 50px;
  color: #fff;
  font-family: 'Baloo Tammudu', cursive;
  font-size: 40px;
  text-align: center;
  text-shadow: 0 0 30px #8DCAED;
  animation: shift-clock 16s infinite;
}

@keyframes shift {
  0% {
    height: 100px;
  }
  50% {
    height: 280px;
  }
  100% {
    height: 100px;
  }
}

@keyframes shift-rim {
  0% {
    top: 40%;
    height: 100px;
  }
  50% {
    top: 50%;
    height: 280px;
  }
  100% {
    top: 40%;
    height: 100px;
  }
}

@keyframes shift-inner {
  0% {
    top: -10px;
    height: 50px;
  }
  50% {
    top: 40px;
    height: 190px;
  }
  100% {
    top: -10px;
    height: 50px;
  }
}

@keyframes shift-clock {
  0% {
    top: -10px;
    transform:  translateX(-50%) scaleY(.2);
  }
  50% {
    top: 100px;
    transform:  translateX(-50%) scaleY(1);
  }
  100% {
    top: -10px;
    transform:  translateX(-50%) scaleY(.2);
  }
}
</style>

<div id="wr_clock" class="container tabcontent">
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
