// -----------------------------------------------------------------------------
// 3D-Module (OpenSCAD) of non-centered cylinder
//
// Author: Bernhard Bablok
// License: GPL3
//
// Website: https://github.com/bablokb/pi-webradio
//
// -----------------------------------------------------------------------------


module cyl_00(h,d,plane="xy") {
  r00 = d/2.0;
  if (plane == "xy")
    translate([r00,r00,0]) cylinder(h=h,r=r00,center=false);
  else if (plane == "yz")
    translate([0,h,0]) rotate([90,0,0]) cyl_00(h,d);
  else if (plane == "xz")
    translate([r00,0,r00]) rotate([-90,0,0]) cylinder(h=h,r=r00,center=false);
}
