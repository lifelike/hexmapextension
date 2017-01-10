#!/usr/bin/env python

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
CENTERDOT_SIZE_PART_OF_HEX_HEIGHT = 0.02

class HexmapEffect(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        # quick attempt compatibility with Inkscape older than 0.91:
        if not hasattr(self, 'unittouu'):
            self.unittouu = inkex.unittouu
        self.log = False
        self.OptionParser.add_option('-l', '--log', action = 'store',
                                     type = 'string', dest = 'logfile')
        self.OptionParser.add_option('-c', '--cols', action = 'store',
                                     type = 'int', dest = 'cols',
                                     default = '10',
                                     help = 'Number of columns.')
        self.OptionParser.add_option('-r', '--rows', action = 'store',
                                     type = 'int', dest = 'rows',
                                     default = '10',
                                     help = 'Number of columns.')
        self.OptionParser.add_option('-z', '--hexsize',
                                     action = 'store', default = 0.0,
                                     type = 'float', dest = 'hexsize')
        self.OptionParser.add_option('-O', '--coordrows', action = 'store',
                                     type = 'int', dest = 'coordrows',
                                     default = '1')
        self.OptionParser.add_option('-s', '--coordcolstart',
                                     action = 'store',
                                     type = 'int', dest = 'coordcolstart',
                                     default = '1')
        self.OptionParser.add_option('-o', '--coordrowstart',
                                     action = 'store',
                                     type = 'int', dest = 'coordrowstart',
                                     default = '1')
        self.OptionParser.add_option('-b', '--bricks',
                                     action = 'store',
                                     type = 'string',
                                     dest = 'bricks',
                                     default = False)
        self.OptionParser.add_option('-t', '--rotate',
                                     action = 'store',
                                     type = 'string',
                                     dest = 'rotate',
                                     default = False)
        self.OptionParser.add_option('-C', '--coordseparator',
                                     action = 'store',
                                     default = '',
                                     type = 'string',
                                     dest = 'coordseparator')
        self.OptionParser.add_option('-A', '--coordalphacol', action = 'store',
                                     dest = 'coordalphacol', default = False,
                                     help = "Reverse row coordinates.")
        self.OptionParser.add_option('-R', '--coordrevrow', action = 'store',
                                     dest = 'coordrevrow', default = False,
                                     help = "Reverse row coordinates.")
        self.OptionParser.add_option('-Z', '--coordzeros', action = 'store',
                                     dest = 'coordzeros', default = True)
        self.OptionParser.add_option('-F', '--coordrowfirst', action = 'store',
                                     dest = 'coordrowfirst', default = False,
                                     help = "Reverse row coordinates.")
        self.OptionParser.add_option('-X', '--xshift', action = 'store',
                                     dest = 'xshift', default = False,
                                     help = "Shift grid half hex and wrap.")
        self.OptionParser.add_option('-f', '--firstcoldown', action = 'store',
                                     dest = 'firstcoldown', default = False,
                                     help = "Make first column half-hex down.")
        self.OptionParser.add_option('-H', '--halfhexes', action = 'store',
                                     dest = 'halfhexes', default = False)
        self.OptionParser.add_option('-Q', '--cornersize', action = 'store',
                                     dest = 'cornersize', default = 1,
                                     type = 'int')

    def createLayer(self, name):
        layer = etree.Element(inkex.addNS('g', 'svg'))
        layer.set(inkex.addNS('label', 'inkscape'), name)
        layer.set(inkex.addNS('groupmode', 'inkscape'), 'layer')
        return layer

    def logwrite(self, msg):
        if not self.log and self.options.logfile:
            self.log = open(self.options.logfile, 'w')
        if self.log:
            self.log.write(msg)

    def svg_line(self, p1, p2):
        line = etree.Element('line')
        line.set("x1", str(p1.x))
        line.set("y1", str(p1.y))
        line.set("x2", str(p2.x))
        line.set("y2", str(p2.y))
        line.set("stroke", "black")
	line.set("stroke-width", str(self.unittouu("%fin" % (1 / 90.0))))
        return line

    def svg_circle(self, p, radius):
        circle = etree.Element("circle")
        circle.set("cx", str(p.x))
        circle.set("cy", str(p.y))
        circle.set("r", str(radius))
        circle.set("fill", "black")
        return circle

    def svg_polygon(self, points):
        poly = etree.Element("polygon")
        pointsdefa = []
        for p in points:
            pointsdefa.append(str(p))
        pointsdef = " ".join(pointsdefa)
        poly.set("points", pointsdef)
        poly.set("style", "stroke:none;fill:#ffffff;fill-opacity:1")
	poly.set("stroke-width", str(self.unittouu("%fin" % (1 / 90.0))))
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
#        value = self.document.createTextNode(coord)
        text.set('x', str(p.x))
        text.set('y', str(p.y))
        style = ("text-align:center;text-anchor:%s;font-size:%fpt"
                 % (anchor, self.coordsize))
        text.set('style', style)
        text.text = coord
#        text.appendChild(value)
        return text

    def add_hexline(self, gridlayer, cornerlayer, p1, p2):
        gridlayer.append(self.svg_line(p1, p2))
        cornerlayer.append(self.svg_line(p1, (p2 - p1) * self.cornersize + p1))
        cornerlayer.append(self.svg_line(p2 - (p2 - p1) * self.cornersize, p2))
        #cornerlayer.append(self.svg_circle(p1, 4))

    def effect(self):
        cols = self.options.cols
        rows = self.options.rows
        halves = self.options.halfhexes == "true"
        xshift = self.options.xshift == "true"
        firstcoldown = self.options.firstcoldown == "true"
        bricks = self.options.bricks == "true"
        rotate = self.options.rotate == "true"

        self.coordseparator = self.options.coordseparator
        if self.coordseparator == None:
            self.coordseparator = ""
        self.coordrevrow = self.options.coordrevrow == "true"
        self.coordrevcol = False
        self.coordalphacol = self.options.coordalphacol == "true"
        self.coordrows = self.options.coordrows
        self.coordrowfirst = self.options.coordrowfirst == "true"
        self.coordzeros = self.options.coordzeros == "true"

        if rotate:
            self.coordrowfirst = not self.coordrowfirst
            self.coordrevcol = not self.coordrevrow
            self.coordrevrow = False

        self.cornersize = self.options.cornersize / 100.0
        self.logwrite("cornersize: %f\n" % self.cornersize)
        if self.cornersize < 0.01 or self.cornersize > 0.5:
            self.logwrite("cornersize out of range\n")
            self.cornersize = 0.15

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
        width = float(self.unittouu(svg.get('width')))
        height = float(self.unittouu(svg.get('height')))

        hexgrid = self.createLayer("Hex Grid")
        hexdots = self.createLayer("Hex Centerdots")
        hexcorners = self.createLayer("Hex Corners")
        hexcorners.set("style", "display:none")
        hexfill = self.createLayer("Hex Fill")
        hexcoords = self.createLayer("Hex Coordinates")

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

        if self.options.hexsize and self.options.hexsize > 0.1:
            hex_width = self.unittouu("%fin" % self.options.hexsize)
            hex_height = calc_hex_height(hex_width)
        else:
            hex_height = calc_hex_height(hex_width)

        hexes_height = hex_height * hex_rows
        hexes_width = hex_width * 0.75 * cols + hex_width * 0.25

        self.coordsize = hex_height * COORD_SIZE_PART_OF_HEX_HEIGHT
        if self.coordsize > 1.0:
            self.coordsize = round(self.coordsize)
        self.centerdotsize = hex_height * CENTERDOT_SIZE_PART_OF_HEX_HEIGHT

        self.logwrite("hex_width: %f, hex_height: %f\n" %(hex_width,
                                                          hex_height))

        # FIXME try to remember what 0.005 is for
        yoffset = COORD_YOFFSET_PART * hex_height * 0.005

        for col in xrange(cols + 1):
            cx = (2.0 + col * 3.0) * 0.25 * hex_width
            if xshift:
                cx = cx - hex_width * 0.5
            coldown = col % 2
            if firstcoldown:
                coldown = not coldown
            for row in xrange(rows + 1):
                cy = (0.5 + coldown * 0.5 + row) * hex_height
                self.logwrite("col: %d, row: %d, c: %f %f\n" % (col, row,
                                                                cx, cy))
                c = Point(cx, cy)
                if rotate:
                    c = c.rotated(hexes_width)
                if (col < cols or xshift) and row < rows:
                    cc = c + Point(0, yoffset)
                    anchor = 'middle'
                    if xshift and col == 0:
                        anchor = 'start'
                    elif xshift and col == cols:
                        anchor = 'end'
                    coord = self.svg_coord(cc, col, row, cols, rows, anchor)
                    if coord != None:
                        hexcoords.append(coord)
                if (col < cols or xshift) and row < rows:
                    cd = self.svg_circle(c, self.centerdotsize)
                    cd.set('id', "hexcenter_%d_%d"
                           % (col + self.options.coordcolstart,
                              row + self.options.coordrowstart))
                    hexdots.append(cd)
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
                if (col < cols or xshift) and row < rows:
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
                    self.add_hexline(hexgrid, hexcorners, p[5], p[0])
                    self.logwrite("line 0-5\n")
                if row < rows:
                    if ((coldown or row > 0 or col < cols
                         or halves or xshift)
                        and not (xshift and col == 0)):
                        self.add_hexline(hexgrid, hexcorners, p[5], p[4])
                        self.logwrite("line 4-5\n")
                    if not coldown and row == 0 and col < cols:
                        self.add_hexline(hexgrid, hexcorners, p[0], p[1])
                        self.logwrite("line 0-1\n")
                    if not (halves and coldown and row == rows-1):
                        if (not (xshift and col == 0)
                            and not (not xshift and col == cols
                                     and row == rows-1 and coldown)):
                            self.add_hexline(hexgrid, hexcorners, p[4], p[3])
                            self.logwrite("line 3-4\n")
                        if coldown and row == rows - 1 and col < cols:
                            self.add_hexline(hexgrid, hexcorners, p[1], p[2])
                            self.logwrite("line 1-2\n")

        # fixme - don't waste cpu generating layers that already exist...
        self.append_if_new_name(svg, hexfill)
        self.append_if_new_name(svg, hexgrid)
        self.append_if_new_name(svg, hexcorners)
        self.append_if_new_name(svg, hexcoords)
        self.append_if_new_name(svg, hexdots)

    def append_if_new_name(self, svg, layer):
        name = layer.get(inkex.addNS('label', 'inkscape'))
        if not name in [c.get(inkex.addNS('label', 'inkscape'), 'name')
                        for c in svg.iterchildren()]:
            svg.append(layer)

effect = HexmapEffect()
effect.affect()
