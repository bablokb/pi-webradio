// -----------------------------------------------------------------------------
// 3D-Model (OpenSCAD) of bottom
//
// Author: Bernhard Bablok
// License: GPL3
//
// Website: https://github.com/bablokb/pi-webradio
//
// -----------------------------------------------------------------------------

$fa = 1;
$fs = 0.4;

w4 = 1.67;    // wall thickness 4 layers
fuzz = 0.001; // fuzzing to ensure overlap

use <cyl_00.scad>

// --- module screw_plate: inner plate for screw   -----------------------------

module screw_plate(s,d) {
  difference() {
    cube([s,s,2]);
    translate([(s-d)/2,(s-d)/2,0]) cyl_00(2,d);
  }
}

// --- base plate   -------------------------------------------------------------

difference() {
  color("red") cube([250,200,2]);

  // holes for screws
  d_screw = 4.4;
  for (dx=[3.47,242.13]) {
    for (dy=[3.47,97.8,192.13]) {
      translate([dx,dy,0])
          cyl_00(2,4.4);
    }
  }
 
  // ventilation
  v_depth = 5;
  for (dy=[15:10:45]) {
    translate([55,dy,0]) cube([110,5,2]);
  }
}
translate([18.23,0,2-fuzz]) cube([213.64,12.14,2]);

// --- screw-plates   ---------------------------------------------------------

color("green") for (dx=[w4,240.33]) {
  for (dy=[w4,96,190.33]) {
    translate([dx,dy,2-fuzz])
        screw_plate(8,2.6);
  }
}

// --- front walls   ----------------------------------------------------------

difference() {
  color("orange") translate([0,0,2-fuzz]) cube([30,w4,67]);
  // --- LED hole   -----------------------------------------------------------
  translate([12.56,0,11]) cyl_00(w4,3.1,plane="yz");
  // --- IR hole   ------------------------------------------------------------
  translate([11.86,0,57.46]) cyl_00(w4,4.55,plane="yz");
}
color("orange") translate([220,0,2-fuzz]) cube([30,w4,67]);
color("pink") translate([0,0,2-fuzz]) cube([250,w4,7]);

// --- screen holder (small diffs between left/right are due to the screen   --

color("brown") translate([18.23,0,2-fuzz]) cube([w4,12.14,67]);
color("brown") translate([230.20,0,2-fuzz]) cube([w4,12.14,67]);
color("brown") translate([18.23,9.67,2-fuzz]) cube([28.77,w4,67]);
color("brown") translate([203,10.47,2-fuzz]) cube([28.87,w4,67]);

