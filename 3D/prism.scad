// -----------------------------------------------------------------------------
// 3D-Model (OpenSCAD) of a prism
//
// Author: Bernhard Bablok
// License: GPL3
//
// Website: https://github.com/bablokb/pi-webradio
//
// -----------------------------------------------------------------------------

use <MCAD/triangles.scad>

module prism(x,y,z,plane="xy") {
  // plane is the plane of the degenerated triangle
  if (plane == "yz")
    translate([x,0,0]) rotate([0,-90,0]) triangle(y,z,x);
  else if (plane == "xz")
    translate([0,y,0]) rotate([90,0,0]) triangle(z,x,y);
  else if (plane == "xy")
    triangle(y,x,z);
}
