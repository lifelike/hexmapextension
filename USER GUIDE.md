# Inkscape Hex Map Extension User Guide

To use the Hex Map Extension, open "Extensions" in the Inkscape top menu and select "Boardgames", "Create Hexmap…" A dialog box should open with tabs for gathering parameters and "Apply" and "Close" buttons

## Size tab

### number of rows, columns

The number of rows (a row extends side-to-side) and columns (a column extends top-to-bottom) to be genrated.

### Hex Size

The Hex Size field allows the user to specify the point-to-point width of the hexagon. The value can be followed by a unit, e.g. "in", "cm", "px", etc. The default unit is pixels. 

If the hex size is left blank, the extension fits the specified number of hexes in so that they do not overflow in any direction. The lines have non-zero thickness, and are positioned using points in the middle of the line. When the extension caluculates the size based on the page size, it moves the hex vertices in so the line thickness fits inside the page limits. Depending on line thickness, the dimension of the "open" area of the hex will be slightly or substantially different from the hex size. The details of the calculation of the hex size are given in a [separate document](documentation/Calculated%20Hex%20Size.md).

If the hex size is specified, the generated hexes can overflow the page.

The height of a hex is √3/2*(Hex Size). The length of one of the sides of a hexagon is ½*(Hex Size).

![Hexes overlaid with bricks](documentation/images/bricks-over-hexes.png?raw=true "Bricks over hexes")

This example is a 5cm x 7cm page, with the extension set to create five rows and five columns. The hex size was left blank. As you can see the hexagons fill the width of the document before they fill the height. The hexagons are sized by the width of the page, and the rest of the page below the hexes is left blank.

In the example the extension has been run once to create hexes, then run a second time to create "bricks" (re-colored green). Unless the "bricks" are set to be square (on the [style tab](#force-square-bricks)), the width of the "bricks" is three-quarters of the "hex size" parameter, and the "brick" height is the same as the hex height, i.e. √3/2*(Hex Size). The "bricks" are centered at the same point as a similarly-sized hex.

### Stroke width
The width of the grid/vertices line segments. The stroke width also affects the size of the hex center dot, which will have a diameter of slightly more than twice the stroke width.

### Size of vertices (%)
Some games have partially drawn hexsides extending from the vertices (see picture below). This parameter determines how far the hexside extends out from the vertex, with the length of the hexside being 100%. Since the partial hexside extends out from both ends, the two partial hexsides meet in the middle when the size is 50%. If the size is 50% the result is not distinguishable from the regular grid. See also the [Layers tab](#layers-tab).

![Hex map using vertices](documentation/images/ten-percent-vertices.png?raw=true "Hex map using verticies")

## Style tab

### Bricks
Instead of hexagons draw rectangular "bricks." The "bricks" have their center in the same place as the hex center (unless )

### Force Square Bricks
Instead of generating rectangles with centers where the hexagons are, generate squares that are the "hex size". 

Note: if the hex size is calculated automatically, square "bricks" will overflow the page.

### Rotate
Generate the hexes pointy sides up-and-down instead of left-and-right. The coordinates are not rotated but zig-zag up and down. The result is not the same as generating the grid normally and rotating it in Inkscape.

### Half hexes at top and bottom
Generates a hex center for the half-hexes at the top and bottom. Generates a coordinate label for the half-hexes at the bottom.

### Shift grid to side and wrap
Instead of beginning with the point of the first hex column on the left-hand side, begin with the center of the hex. Also end with the center of the last column. The two halves at beginning and end are considered one column when calculating the number of columns. If four columns were specified, there would be a first half column labeled "A" (alpha column labeling), three full columns labeled "B"-"D" and a final half column labeled "E".

### First column half-hex down
By default the first column begins in the top left-hand of the page and the next column is shifted down a half hex. Checking this shifts the first column down a half hex instead.

## Coords tab

Various ways of structuring the hex coordinates.

## Layers tab

This determines which artifacts are generated. You might generate them all then turn the ones you don't need off by making them hidden in Inkscape. 

### Grid
The border line segments of the hexagons.

### Fill
Layer containing solid hexagon fills for each hex. The fills are generated as white fills with no stroke, but can be colored or otherwise altered using Inkscape tools. If you are planning to overlay the hexagon grid over your own map, hide or don't generate this layer.

### Coordinates
Layer containing the hex coordinates, structured per the [Coords tab](#coords-tab). They are positioned in the center near the bottom of the hex. You can use Inkscape tools to reposition 

### Center Dots
Layer containing the hex centers. These are always solid black circles. See [Alternate Hex Centers](documentation/Alternate%20Hex%20Centers.md) for steps to place different centers.

### Vertices
Some games print partial hexsides rather than full hexagons to mark the grid, as shown [previously](#size-of-vertices-). This layer is a redundant with the grid layer (although you could change the color or thickness of one/both layers for some interesting effects).

### Circles
Layer containing solid circles drawn with their centers where the hexagon centers are. These are generated as solid black circles with no stroke.

### Layers in Group
This option generates a parent layer that contains the other generated layers. It has no visible elements itself. Having a parent layer allows the child layers to be hidden/shown together as well as making it easy to rename or delete all the generated layers.


## Debug tab
If the log file field is filled in, the extension will output debug text to the file. This probably should not be filled in unless you are fixing a problem or developing a new feature. 

## "Apply" button

Generates the hexagon grid. The code will not overwrite any existing layer that match the names the extension uses. If for some reason you need to generate the hexagon grid again (e.g. you made a mistake in the parameters or you want to overlay a second grid over the first) you have to rename or delete the prior generation. 

## "Close" button

This button closes the Hex Map Dialog Box.

## Alternate Hex Centers

The hex center created by the Hex Map Extension is a single solid black circle, the size of which is determined by the stroke width. If you need a different shape for hex centers, [here](documentation/Alternate%20Hex%20Centers.md) is a detailed list of steps that will allow you to create them. 

## The Real World!

The Hex Map Extension creates regular hexagons, that is all the sides and angles are the same. If you are trying to create a hexmap that is compatible with an existing printed boardgame, be aware that it may be possible that the printed map is not made of regular hexagons. One very popular board game has hexes that are around 1.06% taller than they should be if they were regular. For a single hex this is not very apparent, but the cumulative error for ten hexes (the boards for this game are ten hexes wide) is near eleven percent, which is hard to miss. The fix for this is to scale the hexgrid in one dimension using Inkscape, but the discrepancy can be very confusing if you are unaware.