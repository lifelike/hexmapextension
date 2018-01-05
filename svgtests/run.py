#!/usr/bin/env python2

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

GRID = ["--layer-grid=true"]
FILL = ["--layer-fill=true"]
COORDINATES = ["--layer-coordinates=true"]
CENTERDOTS = ["--layer-centerdots=true"]
VERTICES = ["--layer-vertices=true"]
CIRCLES =  ["--layer-circles=true"]

DEFAULT_LAYERS = GRID + FILL + COORDINATES + CENTERDOTS
ALL_LAYERS = DEFAULT_LAYERS + VERTICES + CIRCLES

def cr(c, r):
    return ["-c", str(c),
            "-r", str(r)]

tests = {
    "simple_1x1" : cr(1, 1) + DEFAULT_LAYERS,
    "all_layers_1x1" : cr(1, 1) + ALL_LAYERS,
    }

successes = 0
fails = 0
skipped = 0
for name,options in tests.iteritems():
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
    commandline.extend(options)
    commandline.append(svginfile)

    if ['-v' in sys.argv]:
        print >> sys.stderr, ' '.join(commandline)

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
        print "FAIL: diff %s %s" % (svgoutfile, expectedfile)
        fails += 1

print ("%d/%d tests OK (%d skipped, %d FAILED)\n"
       % (successes, len(tests), skipped, fails))
