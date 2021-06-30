// -----------------------------------------------------------------------------
// 3D-Model (OpenSCAD) of USB-connector
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

use <MCAD/triangles.scad>

module prism(x,y,h) {
  triangle(y,x,h);
}

module trapez() {
  difference() {
    cube([18,7+fuzz,9.6]);
    prism(5,7+fuzz,9.6);
    translate([5+13,0,0]) rotate([0,0,90]) prism(7,5+fuzz,9.6);
  }
}

module usb_conn() {
  // base
  cube([21.34,40.5,4.7]);

  // upper-part
  difference() {
    color("blue") translate([0,0,4.7]) cube([21.34,40.5,9.6]);
    translate([6.67,0-fuzz,5.35+fuzz]) cube([8,11+fuzz,8.95]);
    translate([1.67,11-2*fuzz,4.7+fuzz]) trapez();
    translate([1.67,11+7-3*fuzz,4.7+fuzz]) cube([18,15+fuzz,9.6]);
    translate([4.17,11+7+15-4*fuzz,6.6+fuzz]) cube([13,7.5+5*fuzz,7.7]);
  }
}
