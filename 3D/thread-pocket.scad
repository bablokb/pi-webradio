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
use <prism.scad>

module thread_pocket(chamfer=false) {
  p_xy = 8;            // dimensions of outer cube
  p_z = 6.5;
  c_d = 4;            // diameter pocket
  c_z = 5.7;          // height pocket

  if (chamfer) {
    ch_z = 2*p_xy;
    translate([0,0,-p_z]) rotate([180,0,90]) prism(p_xy,p_xy,ch_z,plane="yz");
  }

  translate([0,0,-p_z]) difference() {
    cube([p_xy,p_xy,p_z]);
    translate([(p_xy-c_d)/2,(p_xy-c_d)/2,p_z-c_z+fuzz]) cyl_00(d=c_d,h=c_z+fuzz,plane="xy");
  }
}
thread_pocket(chamfer=true);
