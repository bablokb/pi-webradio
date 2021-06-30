// -----------------------------------------------------------------------------
// 3D-Model (OpenSCAD) of HDMI-connector
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

module hdmi_conn() {
  difference() {
    cube([31.5,28.17,6.6]);
    translate([5,4.99,5]) cube([21.5,21.6,1.6+fuzz]);
  }
  difference() {
    color("blue") translate([0,26.5,6.6-fuzz]) cube([31.5,1.67,6.4]);
    translate([8.25,26.5-fuzz/2,6.6-fuzz/2]) cube([15.30,1.67+fuzz,6.4+fuzz]);
  }
}
