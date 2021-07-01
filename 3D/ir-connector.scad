// -----------------------------------------------------------------------------
// 3D-Model (OpenSCAD) of IR-connector
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

use <prism.scad>

module ir_conn() {
  irw = 0.86;    // wall thickness
  irx = 7.72;
  iry = 2.3;
  irpz = 6;      // z of prism
  ircz = 8.82;   // z of outer-cube

  color("lightblue") translate([irx,0,irpz]) rotate([0,180,0]) prism(irx,iry,irpz,plane="yz");
  translate([0,0,irpz-fuzz]) difference() {
    cube([irx,iry,ircz]);
    translate([irw,-fuzz,irw]) cube([irx-2*irw,iry+2*fuzz,ircz-2*irw]);
  };
}

//color("pink") translate([10.3,1.67,49]) ir_conn();
