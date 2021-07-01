// -----------------------------------------------------------------------------
// 3D-Model (OpenSCAD) of touch-connector
//
// This is just a holder for a small touch-sensor breakout.
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

module touch_conn() {
  tw = 0.86;    // wall thickness
  tx = 12.82;
  ty = 3.66;
  tpz = 7;       // z of prism
  tcy = 2.8;     // y of outer-cube
  tcz = 16.42;   // z of outer-cube
  tbz = 12.36;   // z of back-cube

  color("lightblue") translate([tx,0,tpz]) rotate([0,180,0]) prism(tx,ty,tpz,plane="yz");
  translate([0,0,tpz-fuzz]) difference() {
    cube([tx,tcy,tcz]);                                                // outer-cube
    translate([tw,-fuzz,tw]) cube([tx-2*tw,tcy+2*fuzz,tcz-tw+fuzz]);   // inner-cube
  };
  color("lightpink") translate([0,ty-tw-fuzz,tpz-fuzz]) cube([tx,tw,tbz]);       // back
}

touch_conn();

//color("pink") translate([231.87,1.67,45.58]) touch_conn();
