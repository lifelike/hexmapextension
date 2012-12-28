#!/bin/sh

if [ -e ~/.config/inkscape/extensions/ ]; then
    EXTDIR=~/.config/inkscape/extensions/
else
    EXTDIR=~/.inkscape/extensions/
fi

cp *.inx *.py $EXTDIR

if [ -e /Applications/Inkscape.app ] ; then
    /Applications/Inkscape.app/Contents/MacOS/Inkscape
else
    inkscape $*
fi
