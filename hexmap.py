#!/usr/bin/env python3

import inkex
import sys
from inkex import NSS
import math
import lxml
from lxml import etree

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "%f,%f" % (self.x, self.y)

    def y_mirror(self, h):
        return Point(self.x, h - self.y);

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __mul__(self, k):
        return Point(self.x * k, self.y * k)

    def rotated(self, total_width):
        return Point(self.y, total_width - self.x)

def nrdigits(f):
    return int(math.floor(math.log10(f))) + 1

def alphacol(c):
    d = c / 26
    r = c % 26
    return ("%c" % (r + 65)) * (d + 1)

def calc_hex_height(hex_width):
    return 0.25 * hex_width / math.tan(math.pi / 6) * 2

COORD_SIZE_PART_OF_HEX_HEIGHT = 0.1
COORD_YOFFSET_PART = 75
CENTERDOT_SIZE_FACTOR = 1.1690625

LAYERS = ["grid", "centerdots", "vertices", "fill", "coordinates", "circles"]

class HexmapEffect(inkex.EffectExtension):
    def __init__(self):
        super().__init__()
        self.log = False

    def add_arguments(self, pars):
        pars.add_argument("--tab")
        pars.add_argument('--log', type = str)
        pars.add_argument('--cols',
                          type = int,
                          default = 10,
                          help = 'Number of columns.')
        pars.add_argument('--rows',
                          type = int,
                          default = 10,
                          help = 'Number of columns.')
        pars.add_argument('--hexsize',
                          default = "",
                          type = str,)
        pars.add_argument('--strokewidth',
                          default = "1pt",
                          type = str)
        pars.add_argument('--coordrows',
                          type = int,
                          default = 1)
        pars.add_argument('--coordcolstart',
                          type = int,
                          default = 1)
        pars.add_argument('--coordrowstart',
                          type = int,
                          default = 1)
        pars.add_argument('--bricks',
                          type = inkex.Boolean,
                          default = False)
        pars.add_argument('--squarebricks',
                          type = inkex.Boolean,
                          default = False)
        pars.add_argument('--rotate',
                          type = inkex.Boolean,
                          default = False)
        pars.add_argument('--coordseparator',
                          default = '',
                          type = str)
        pars.add_argument('--layersingroup',
                          type = inkex.Boolean,
                          default = False,
                          help = "Put all layers in a layer group.")
        pars.add_argument('--coordalphacol',
                          type = inkex.Boolean,
                          default = False,
                          help = "Reverse row coordinates.")
        pars.add_argument('--coordrevrow',
                          type = inkex.Boolean,
                          default = False,
                          help = "Reverse row coordinates.")
        pars.add_argument('--coordzeros',
                          type = inkex.Boolean,
                          default = True)
        pars.add_argument('--coordrowfirst',
                          type = inkex.Boolean,
                          default = False,
                          help = "Reverse row coordinates.")
        pars.add_argument('--xshift',
                          type = inkex.Boolean,
                          default = False,
                          help = "Shift grid half hex and wrap.")
        pars.add_argument('--firstcoldown',
                          type = inkex.Boolean,
                          default = False,
                          help = "Make first column half-hex down.")
        pars.add_argument('--halfhexes',
                          type = inkex.Boolean,
                          default = False)
        pars.add_argument('--verticesize',
                          default = 1,
                          type = int)
        for layer in LAYERS:
            pars.add_argument('--layer' + layer,
                              type = inkex.Boolean,
                              default = False)

    def createLayer(self, name):
        layer = etree.Element(inkex.addNS('g', 'svg'))
        layer.set(inkex.addNS('label', 'inkscape'), name)
        layer.set(inkex.addNS('groupmode', 'inkscape'), 'layer')
        return layer

    def logwrite(self, msg):
        if not self.log and self.options.log:
            self.log = open(self.options.log, 'w')
        if self.log:
            self.log.write(msg)

    def svg_line(self, p1, p2):
        line = etree.Element('line')
        line.set("x1", str(p1.x + self.xoffset))
        line.set("y1", str(p1.y + self.yoffset))
        line.set("x2", str(p2.x + self.xoffset))
        line.set("y2", str(p2.y + self.yoffset))
        line.set("stroke", "black")
        line.set("stroke-width", str(self.stroke_width))
        line.set("stroke-linecap", "round")
        return line

    def svg_circle(self, p, radius):
        circle = etree.Element("circle")
        circle.set("cx", str(p.x + self.xoffset))
        circle.set("cy", str(p.y + self.yoffset))
        circle.set("r", str(radius))
        circle.set("fill", "black")
        return circle

    def svg_polygon(self, points):
        poly = etree.Element("polygon")
        pointsdefa = []
        for p in points:
            offset_p = Point(p.x + self.xoffset, p.y + self.yoffset)
            pointsdefa.append(str(offset_p))
        pointsdef = " ".join(pointsdefa)
        poly.set("points", pointsdef)
        poly.set("style", "stroke:none;fill:#ffffff;fill-opacity:1")
        poly.set("stroke-width", str(self.stroke_width))
        poly.set("stroke-linecap", "round")
        return poly

    def svg_coord(self, p, col, row, cols, rows, anchor='middle'):
        if self.coordrevrow:
            row = rows - row
        else:
            row = row + 1
        if self.coordrevcol:
            col = cols - col
        else:
            col = col + 1
        row = row + self.options.coordrowstart - 1
        col = col + self.options.coordcolstart - 1
        if ((row != 1 and row % self.coordrows != 0)
             or row < 1 or col < 1):
             return None

        if self.coordrowfirst:
             col,row = [row,col]

        if self.coordalphacol:
            acol = alphacol(col - 1)
            if self.coordzeros:
                zrow = str(row).zfill(self.rowdigits)
                coord = acol + self.coordseparator + zrow
            else:
                coord = acol + self.coordseparator + str(row)
        elif self.coordzeros:
            zcol = str(col).zfill(self.coldigits)
            zrow = str(row).zfill(self.rowdigits)
            coord = zcol + self.coordseparator + zrow
        else:
            coord = str(col) + self.coordseparator + str(row)

        self.logwrite(" coord-> '%s'\n" % (coord))
        text = etree.Element('text')
        text.set('x', str(p.x + self.xoffset))
        text.set('y', str(p.y + self.yoffset))
        style = ("text-align:center;text-anchor:%s;font-size:%fpt"
                 % (anchor, self.coordsize))
        text.set('style', style)
        text.text = coord
        return text

    def add_hexline(self, gridlayer, verticelayer, p1, p2):
        if gridlayer is not None:
            gridlayer.append(self.svg_line(p1, p2))
        if verticelayer is not None:
            verticelayer.append(self.svg_line(p1, (p2 - p1)
                                            * self.verticesize + p1))
            verticelayer.append(self.svg_line(p2, p2 - (p2 - p1)
                                            * self.verticesize))

    def effect(self):
        strokewidth = self.options.strokewidth

        cols = self.options.cols
        rows = self.options.rows
        halves = self.options.halfhexes
        xshift = self.options.xshift
        firstcoldown = self.options.firstcoldown
        bricks = self.options.bricks
        squarebricks = self.options.squarebricks
        rotate = self.options.rotate
        layersingroup = self.options.layersingroup

        self.coordseparator = self.options.coordseparator
        if self.coordseparator == None:
            self.coordseparator = ""
        self.coordrevrow = self.options.coordrevrow
        self.coordrevcol = False
        self.coordalphacol = self.options.coordalphacol
        self.coordrows = self.options.coordrows
        self.coordrowfirst = self.options.coordrowfirst
        self.coordzeros = self.options.coordzeros

        self.enabled_layers = set()

        for layer in LAYERS:
            if getattr(self.options, "layer" + layer):
                self.enabled_layers.add(layer)

        if len(self.enabled_layers) == 0:
            raise ValueError("No layers are enabled.")

        if rotate:
            self.coordrowfirst = not self.coordrowfirst
            self.coordrevcol = not self.coordrevrow
            self.coordrevrow = False

        self.verticesize = self.options.verticesize / 100.0
        self.logwrite("verticesize: %f\n" % self.verticesize)
        if self.verticesize < 0.01 or self.verticesize > 0.5:
            self.logwrite("verticesize out of range\n")
            self.verticesize = 0.15

        self.coldigits = nrdigits(cols + self.options.coordcolstart)
        self.rowdigits = nrdigits(rows + self.options.coordrowstart)
        if self.coldigits < 2:
            self.coldigits = 2
        if self.rowdigits < 2:
            self.rowdigits = 2
        if self.coordrowfirst:
            self.coldigits,self.rowdigits = [self.rowdigits,self.coldigits]

        self.logwrite("cols: %d, rows: %d\n" % (cols, rows))
        self.logwrite("xshift: %s, halves: %s\n" % (str(xshift), str(halves)))

        svg = self.document.xpath('//svg:svg' , namespaces=NSS)[0]

        self.stroke_width = self.parse_float_with_unit(
            self.options.strokewidth, "stroke width")

        width = float(self.svg.unittouu(svg.get('width'))) - self.stroke_width
        height = float(self.svg.unittouu(svg.get('height'))) - self.stroke_width

        # So I was a bit lazy and only added an offset to all the
        # svg_* functions to compensate for the stroke width.
        # There should be a better way.
        self.xoffset = self.stroke_width * 0.5
        self.yoffset = self.stroke_width * 0.5

        # FIXME there is room for improvement here
        if 'grid' in self.enabled_layers:
            hexgrid = self.createLayer("Hex Grid")
        else:
            hexgrid = None
        if 'centerdots' in self.enabled_layers:
            hexdots = self.createLayer("Hex Centerdots")
        else:
            hexdots = None
        if 'vertices' in self.enabled_layers:
            hexvertices = self.createLayer("Hex Vertices")
        else:
            hexvertices = None
        if 'fill' in self.enabled_layers:
            hexfill = self.createLayer("Hex Fill")
        else:
            hexfill = None
        if 'coordinates' in self.enabled_layers:
            hexcoords = self.createLayer("Hex Coordinates")
        else:
            hexcoords = None
        if 'circles' in self.enabled_layers:
            hexcircles = self.createLayer("Hex Circles")
        else:
            hexcircles = None

        if hexvertices is not None and hexgrid is not None:
            hexgrid.set("style", "display:none")

        self.logwrite("w, h : %f, %f\n" % (width, height))

        if xshift:
            hex_cols = (cols * 3.0) * 0.25
        else:
            hex_cols = (cols * 3.0 + 1.0) * 0.25

        if halves:
            hex_rows = rows
        else:
            hex_rows = rows + 0.5

        hex_width = width / hex_cols

        if self.options.hexsize and self.options.hexsize != "":
            hex_width = self.parse_float_with_unit(self.options.hexsize,
                                                   "hex size")
        hex_height = calc_hex_height(hex_width)

        # square bricks workaround
        if bricks and squarebricks:
            hex_height = hex_width
            hex_width = hex_width / 0.75

        hexes_height = hex_height * hex_rows
        hexes_width = hex_width * 0.75 * cols + hex_width * 0.25

        self.coordsize = hex_height * COORD_SIZE_PART_OF_HEX_HEIGHT
        if self.coordsize > 1.0:
            self.coordsize = round(self.coordsize)
        self.centerdotsize = self.stroke_width * CENTERDOT_SIZE_FACTOR
        self.circlesize = hex_height / 2

        self.logwrite("hex_width: %f, hex_height: %f\n" %(hex_width,
                                                          hex_height))

        # FIXME try to remember what 0.005 is for
        coord_yoffset = COORD_YOFFSET_PART * hex_height * 0.005

        for col in range(cols + 1):
            cx = (2.0 + col * 3.0) * 0.25 * hex_width
            if xshift:
                cx = cx - hex_width * 0.5
            coldown = col % 2
            if firstcoldown:
                coldown = not coldown
            for row in range(rows + 1):
                cy = (0.5 + coldown * 0.5 + row) * hex_height
                self.logwrite("col: %d, row: %d, c: %f %f\n" % (col, row,
                                                                cx, cy))
                c = Point(cx, cy)
                if rotate:
                    c = c.rotated(hexes_width)
                if (hexcoords is not None
                    and (col < cols or xshift) and row < rows):
                    cc = c + Point(0, coord_yoffset)
                    anchor = 'middle'
                    if xshift and col == 0:
                        anchor = 'start'
                    elif xshift and col == cols:
                        anchor = 'end'
                    coord = self.svg_coord(cc, col, row, cols, rows, anchor)
                    if coord != None:
                        hexcoords.append(coord)
                if (hexdots is not None
                    and (col < cols or xshift) and row < rows):
                    cd = self.svg_circle(c, self.centerdotsize)
                    cd.set('id', "hexcenter_%d_%d"
                           % (col + self.options.coordcolstart,
                              row + self.options.coordrowstart))
                    hexdots.append(cd)
                #FIXME make half-circles in half hexes
                if (hexcircles is not None and (col < cols or xshift)
                    and row < rows):
                    el = self.svg_circle(c, self.circlesize)
                    el.set('id', "hexcircle_%d_%d"
                           % (col + self.options.coordcolstart,
                              row + self.options.coordrowstart))
                    hexcircles.append(el)
                x = [cx - hex_width * 0.5,
                     cx - hex_width * 0.25,
                     cx + hex_width * 0.25,
                     cx + hex_width * 0.5]
                y = [cy - hex_height * 0.5,
                     cy,
                     cy + hex_height * 0.5]
                if bricks and xshift:
                    sys.exit('No support for bricks with x shift.')
                if xshift and col == 0:
                    x[0] = cx
                    x[1] = cx
                elif xshift and col == cols:
                    x[2] = cx
                    x[3] = cx
                if halves and coldown and row == rows-1:
                    y[2] = cy
                # with bricks pattern, shift some coordinates a bit
                # to make correct shape
                if bricks:
                    brick_adjust = hex_width * 0.125
                else:
                    brick_adjust = 0
                p = [Point(x[2] + brick_adjust, y[0]),
                     Point(x[3] - brick_adjust, y[1]),
                     Point(x[2] + brick_adjust, y[2]),
                     Point(x[1] - brick_adjust, y[2]),
                     Point(x[0] + brick_adjust, y[1]),
                     Point(x[1] - brick_adjust, y[0])]
                if rotate:
                    p = [point.rotated(hexes_width) for point in p]
                if (hexfill is not None
                    and (col < cols or xshift) and row < rows):
                    if row < rows or (halves and coldown):
                        sp = self.svg_polygon(p)
                    if halves and coldown and row == rows - 1:
                        p2 = [x.y_mirror(hexes_height) for x in p]
                        sp = self.svg_polygon(p)
                    sp.set('id', "hexfill_%d_%d"
                           % (col + self.options.coordcolstart,
                              row + self.options.coordrowstart))
                    hexfill.append(sp)
                if ((col < cols and (not halves or row < rows
                                     or not coldown))
                    or (xshift and col == cols
                        and not (halves and row == rows))):
                    self.add_hexline(hexgrid, hexvertices, p[5], p[0])
                    self.logwrite("line 0-5\n")
                if row < rows:
                    if ((coldown or row > 0 or col < cols
                         or halves or xshift)
                        and not (xshift and col == 0)):
                        self.add_hexline(hexgrid, hexvertices, p[5], p[4])
                        self.logwrite("line 4-5\n")
                    if not coldown and row == 0 and col < cols:
                        self.add_hexline(hexgrid, hexvertices, p[0], p[1])
                        self.logwrite("line 0-1\n")
                    if not (halves and coldown and row == rows-1):
                        if (not (xshift and col == 0)
                            and not (not xshift and col == cols
                                     and row == rows-1 and coldown)):
                            self.add_hexline(hexgrid, hexvertices, p[4], p[3])
                            self.logwrite("line 3-4\n")
                        if coldown and row == rows - 1 and col < cols:
                            self.add_hexline(hexgrid, hexvertices, p[1], p[2])
                            self.logwrite("line 1-2\n")
        parent = svg
        if layersingroup:
            parent = self.createLayer("Hex Map")
            self.append_if_new_name(svg, parent)
        self.append_if_new_name(parent, hexfill)
        self.append_if_new_name(parent, hexcircles)
        self.append_if_new_name(parent, hexgrid)
        self.append_if_new_name(parent, hexvertices)
        self.append_if_new_name(parent, hexcoords)
        self.append_if_new_name(parent, hexdots)

    def parse_float_with_unit(self, value, name):
        try:
            result = hex_width = self.svg.unittouu(value.strip())
        except:
            sys.exit("Failed to parse %s '%s'. Must be "
                     "digits followed by optional unit name "
                     "(e.g. mm, cm, in, pt). If no unit is "
                     "named the default will be whatever the "
                     "default units for the document is."
                     % (name, value))
        if result <= 0:
            sys.exit("%s must be positive" % name)
        return result

    def append_if_new_name(self, svg, layer):
        if layer is not None:
            name = layer.get(inkex.addNS('label', 'inkscape'))
            if not name in [c.get(inkex.addNS('label', 'inkscape'), 'name')
                            for c in svg.iterchildren()]:
                svg.append(layer)

if __name__ == '__main__':
    HexmapEffect().run()
