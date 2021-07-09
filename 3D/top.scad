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

$fa = 1;
$fs = 0.4;

w4 = 1.67;    // wall thickness 4 layers
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

module cutout() {
  x_usb = 21.34;
  z_usb = 4.7+9.6;
  translate([-87.91,200-fuzz/2,67-z_usb+2-fuzz]) cube([x_usb,w4+fuzz,z_usb]);

  x_hdmi = 21.34;
  z_hdmi = 4.7+9.6;
  translate([-109.25,200-fuzz/2,67-z_hdmi+2-fuzz]) cube([x_hdmi,w4+fuzz,z_hdmi]);

  x_power = 21.34;
  z_power = 4.7+9.6;
  translate([-140.75,200-fuzz/2,67-z_power+2-fuzz]) cube([x_power,w4+fuzz,z_power]);
}

// --- walls   -----------------------------------------------------------------

translate([-250,0,2-fuzz]) color("orange") cube([250,w4,7]);    // front
translate([-250,0,2-fuzz]) color("orange") cube([w4,200,67]);   // left
translate([-w4,0,2-fuzz]) color("orange") cube([w4,200,67]);    // right
color("orange") difference() {                                  // back
  translate([-250,200,2-fuzz]) cube([250,w4,67]);
  cutout();
}

// --- screw-sockets   ---------------------------------------------------------

