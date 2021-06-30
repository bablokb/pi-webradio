// -----------------------------------------------------------------------------
// 3D-Model (OpenSCAD) of power-connector (5.5/2.1mm screw-in socket)
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

module power_conn() {
  difference() {
    cube([20,1.67,20]);
    translate([4.1,-fuzz/2,4.1]) cyl_00(d=11.8,h=1.67+fuzz,plane="xz");
  }
}
