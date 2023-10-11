#! /usr/bin/env python3

# Example script to decompose the composite glyphs in a TTF into
# non-composite outlines.


import sys
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen

try:
    import pathops
except ImportError:
    sys.exit(
        "This script requires the skia-pathops module. "
        "`pip install skia-pathops` and then retry."
    )


src =  "./files/1.ttf"
dst =  "./out2.otf"

with TTFont(src) as f:
    glyfTable = f["glyf"]
    glyphSet = f.getGlyphSet()

    for glyphName in glyphSet.keys():
        # if not glyfTable[glyphName].isComposite():
            # continue


        # record TTGlyph outlines without components
        dcPen = DecomposingRecordingPen(glyphSet)
        # glyphSet[glyphName].draw(dcPen)
        dcPen.moveTo((0,0))
        dcPen.lineTo((0,200))
        dcPen.lineTo((200,200))
        dcPen.lineTo((200,0))
        dcPen.lineTo((0,0))
        dcPen.closePath()
        dcPen.moveTo((100,100))
        dcPen.lineTo((100,300))
        dcPen.lineTo((300,300))
        dcPen.lineTo((300,100))
        dcPen.lineTo((100,100))
        dcPen.closePath()
        # replay recording onto a skia-pathops Path
        path = pathops.Path()
        pathPen = path.getPen()
        dcPen.replay(pathPen)
        # pathops.operations.difference(path,path,pathPen)

        # remove overlaps
        # path.simplify()
        path1 = pathops.Path()
        path1.moveTo(100,100)
        path1.lineTo(100,300)
        path1.lineTo(300,300)
        path1.lineTo(300,100)
        path1.lineTo(100,100)
        path2 = pathops.Path()
        path2.moveTo(0,0)
        path2.lineTo(0,200)
        path2.lineTo(200,200)
        path2.lineTo(200,0)
        path2.lineTo(0,0)

        path = pathops.Path()
        pathops.operations.xor([path1],[path2],path.getPen())
        path.simplify()

            # create new TTGlyph from Path
        ttPen = TTGlyphPen(None)
        path.draw(ttPen)
        glyfTable[glyphName] = ttPen.glyph()

    f.save(dst)
