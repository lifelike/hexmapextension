# Alternate Hex Centers

The Hex Map Extension creates hex center markers as black, solid circles with a size determined by the stroke width. Simple changes to these shapes (e.g. changing color) can be made in Inkscape using standard tools. If you want to have hex centers that are different shapes (e.g. rectangles, triangles, stars, etc.), this page will show you how you can create a single object then clone it into the right positions. The procedure is not difficult, but does require some (simple) math. The procedure tries to be detailed about each step, so don't be discouraged if it looks a bit long.

Make sure all measurements are in the same units. The type of units chosen will not matter because the final calculated values are percents. As long as the units are consistent any unit should produce the same answer.

## Creating a set of alternate set of center objects
1. Lock all layers except the center dots (and the group layer if you have the hex map grouped).
1. Get the size of one existing hex center by selecting it using the select tool (arrow). The width and height are given in the top toolbar. This value will be refered to as size_old_center_x (the width in the toolbar; should be the same as size_old_center_y or height because it is a circle).
1. If you specified the hex size when creating the hex grid, that is the center_distance_x.
1. If you did not specify the hex size or don't know it, you can measure it in the image. 
    - Select two hex centers that are in adjacent columns in adjacent hexes
    - The width of the two selected objects minus the size_old_center_x is the center_distance_x
1. The center_distance_y = center_distance_x*√3/2
1. Create a new layer
1. Create a new hex center object on that new layer
1. Get the size of the new hex center object by selecting it, recording the size_new_center_x and size_new_center_y
1. Select the upper left existing hex center then the new hex center object. Use Inkscape to align to first object vertical and horizontal to position the new center over the old upper-left object.
1. Lock the old hex centers layer
1. Unselect the pair, then select the new hex center object
1. top menu, edit, create tiled clones
    - symmetry=simple translation
    - shift: as many rows as needed, two columns
    - per row:  shift x=0, shift y=100*(center_distance_y - size_new_center_y)/size_new_center_y
    - per col: shift x=100*(center_distance_x - size_new_center_x)/size_new_center_x; shift y=100*(center_distance_y - size_new_center_y/2)/2*size_new_center_y
1. Click the "Create" button
1. [If something goes wrong, remove. Do not keep applying without removing. Bad things happen. Otherwise, at this point the first two columns should be correct.]
1. Select all the new hex center objects, original and clones
1. Record the width (group_size_x)
1. top menu, edit, create tiled clones
    - symmetry=simple translation
    - shift: one row, as many cols as needed divided by two
    - shift per row:  shift x=0, shift y=0
    - per col: shift x=100*(2*center_distance_x - group_size_x)/group_size_x; shift y=0
1. Click the "Create" button
1. Hide old hex centers, lock new hex centers
