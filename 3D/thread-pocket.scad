// -----------------------------------------------------------------------------
// 3D-Model (OpenSCAD) of thread-pocket
//
// Author: Bernhard Bablok
// License: GPL3
//
// Website: https://github.com/bablokb/pi-webradio
//
// -----------------------------------------------------------------------------

$fa = 1;
$fs = 0.4;

fuzz = 0.001;

use <cyl_00.scad>

module thread_pocket() {
  p_x = 8;            // dimensions of outer cube
  p_y = 8;
  p_z = 6.5;
  c_d = 4;            // diameter pocket
  c_z = 5.7;          // height pocket

  difference() {
    cube([p_x,p_y,p_z]);
    translate([(p_x-c_d)/2,(p_y-c_d)/2,p_z-c_z+fuzz]) cyl_00(d=c_d,h=c_z+fuzz,plane="xy");
  }
}
thread_pocket();
