#!/usr/bin/env python3

import difflib
import glob
import os
import os.path
import shutil
import subprocess
import sys

def add_countersheets_paths():
    sys.path.insert(0, os.getcwd())

add_countersheets_paths()

inputdir = os.path.join('svgtests', 'input')
outputdir = os.path.join('svgtests', 'output')
expecteddir = os.path.join('svgtests', 'expected')
logdir = os.path.join('svgtests', 'log')

if not os.path.exists(outputdir):
    os.mkdir(outputdir)

chosen = [a for a in sys.argv[1:]
          if not a.startswith("-")]

GRID = ["--layergrid=true"]
FILL = ["--layerfill=true"]
COORDINATES = ["--layercoordinates=true"]
CENTERDOTS = ["--layercenterdots=true"]
VERTICES = ["--layervertices=true"]
CIRCLES = ["--layercircles=true"]

GROUP_LAYERS = ["--layersingroup=true"]

BRICKS = ["--bricks=true"]
SQUAREBRICKS = ["--squarebricks=true"]
ROTATE = ["--rotate=true"]
HALFHEXES= ["--halfhexes=true"]
XSHIFT= ["--xshift=true"]
FIRSTCOLDOWN= ["--firstcoldown=true"]

ID = ["--id=foo"] # avoid crash in inkex.base.load

DEFAULT_LAYERS = GRID + FILL + COORDINATES + CENTERDOTS
ALL_LAYERS = DEFAULT_LAYERS + VERTICES + CIRCLES

def cr(c, r):
    return ["--cols=" + str(c),
            "--rows=" + str(r)]

def hexsize(s):
    return ['--hexsize=%s' % s]

def verticesize(s):
    return ["--verticesize=%d" % s]

def strokewidth(w):
    return ['--strokewidth="%s"' % w]

def coordseparator(s):
    return ['--coordseparator="%s"' % s]

COORDALPHACOL = ["--coordalphacol=true"]
COORDREVROW = ["--coordrevrow=true"]
COORDROWFIRST = ["--coordrowfirst=true"]
COORDZEROS = ["--coordzeros=true"]

def coordrows(r):
    return ["--coordrows=%d" % r]
def coordcolstart(r):
    return ["--coordcolstart=%d" % r]
def coordrowstart(r):
    return ["--coordrowstart=%d" % r]

DEFAULTS = ALL_LAYERS + cr(4,4) + verticesize(5) + hexsize("1in")

tests = {
    "simple_1x1" : cr(1, 1) + DEFAULT_LAYERS,
    "all_layers_1x1" : cr(1, 1) + ALL_LAYERS,
    "4x4" : cr(4, 4) + ALL_LAYERS,
    "defaults" : DEFAULTS
    }

successes = 0
fails = 0
skipped = 0
for name,options in tests.items():
    if chosen:
        matches = False
        for c in chosen:
            if c in name:
                matches = True
                break
        if not matches:
            skipped += 1
            continue
    svgoutbasename = "%s.svg" % name
    svgoutfile = os.path.join(outputdir, svgoutbasename)
    svginfile = os.path.join(inputdir, "test.svg")
    svgout = open(svgoutfile, "w")
    command = os.path.join('.', 'hexmap.py')
    logfile = os.path.join(logdir, 'cs_svgtests-%s.txt' % name)
    commandline = [command]
    commandline.extend(options + ID)
    commandline.append(svginfile)

    if ['-v' in sys.argv]:
        print(' '.join(commandline), file=sys.stderr)

    effect = subprocess.Popen(commandline,
                              stdout=svgout)
    effect.wait()
    svgout.close()
    if effect.returncode:
        sys.exit('Failed to run svgtest %s.'
                 % (name))

    expectedfile = os.path.join(expecteddir, svgoutbasename)
    outputsvg = open(svgoutfile).read()
    expectedsvg = open(expectedfile).read()
    if outputsvg == expectedsvg:
        successes += 1
    else:
        print("FAIL: diff %s %s" % (svgoutfile, expectedfile))
        fails += 1

print(("%d/%d tests OK (%d skipped, %d FAILED)\n"
       % (successes, len(tests), skipped, fails)))
