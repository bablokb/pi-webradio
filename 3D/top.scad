// -----------------------------------------------------------------------------
// 3D-Model (OpenSCAD) of upper-part of the case.
//
// Note: the construction is upside-down with negative coordinates.
//
// Author: Bernhard Bablok
// License: GPL3
//
// Website: https://github.com/bablokb/pi-webradio
//
// -----------------------------------------------------------------------------

use <thread-pocket.scad>

$fa = 1;
$fs = 0.4;

w4 = 1.67;    // wall thickness 4 layers
h_wall = 67;
fuzz = 0.001; // fuzzing to ensure overlap

// --- base plate   ------------------------------------------------------------

translate([-250,0,0]) difference() {
  color("red") cube([250,200,2]);
 
  // ventilation
  v_depth = 5;
  for (dy=[15:10:45]) {
    translate([55,dy,0]) cube([110,5,2]);
  }
}

// --- cutout back-side   ------------------------------------------------------

  x_add = 0.2;

  x_usb = 22.0+x_add;                // should be 21.34
  z_usb = 14.4;   // 4.7+9.6 + 0.1

  x_hdmi = 31.3-x_add/2;
  z_hdmi = 13.1;  // 6.6+6.4 + 0.1

  x_power = 20+x_add;
  z_power = 20;

module cutout(x_usb,z_usb,x_hdmi,z_hdmi,x_power,z_power) {

  rotate([0,-180,0]) union() {
    cube([x_usb,w4+2*fuzz,z_usb]);
    color("blue") translate([x_usb-fuzz,0,0]) cube([x_hdmi+2*fuzz,w4+2*fuzz,z_hdmi]);
    translate([x_usb+x_hdmi-2*fuzz,0,0]) cube([x_power,w4+2*fuzz,z_power]);
  }
}

// --- walls   -----------------------------------------------------------------

translate([-250,0,2-fuzz]) color("orange") cube([250,w4,7]);    // front
translate([-250,0,2-fuzz]) color("orange") cube([w4,200,h_wall]);   // left
translate([-w4,0,2-fuzz]) color("orange") cube([w4,200,h_wall]);    // right
color("orange") difference() {                                  // back
  translate([-250,200-w4,2-fuzz]) cube([250,w4,h_wall]);
  translate([-87.4,200-w4,2+h_wall+fuzz]) cutout(x_usb,z_usb,x_hdmi,z_hdmi,x_power,z_power);  // -87.91
}


// --- screw-sockets   ---------------------------------------------------------

color("green")
  for (dy=[w4,96,190.33]) {
    translate([-w4,dy+8,h_wall])
        rotate([0,0,-180]) thread_pocket(chamfer=true);
    translate([-250+w4,dy,h_wall])
        rotate([0,0,0]) thread_pocket(chamfer=true);
  }

// --- support   ---------------------------------------------------------------

translate([-250,100,2-fuzz]) color("green") cube([250,w4,15]);
