
import numpy as np
import potrace
from fontTools.pens.freetypePen import FreeTypePen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Offset
from PIL import ImageDraw, Image, ImageOps, ImageFilter, ImageMath

test_bool = 0

potrace_curves = 1.0
potrace_simple = 0
potrace_min = 1.0
potrace_simplify = 0.2
potrace_size = 1
display_points = 0

imgMargin = 200


def glyph_to_raster(font, glyph):
    pen = FreeTypePen(None)
    glyph = font.getGlyphSet()[glyph]
    glyph.draw(pen)
    ascender = font['OS/2'].usWinAscent
    descender = -font['OS/2'].usWinDescent
    height = ascender - descender + 2*imgMargin
    width = glyph.width + 2*imgMargin

    # img = pen.image(width=width, height=height, transform=Offset(0, -descender))
    img = pen.image(width=width, height=height, transform=Offset(imgMargin, -descender+2*imgMargin))
    img = img.getchannel('A')
    img = ImageOps.invert(img)
    return img

def vectorization(img):
    width = float(img.size[0])*potrace_size
    wpercent = (float(width)/float(img.size[0]))
    height = int((float(img.size[1])*float(wpercent)))
    img = img.resize((int(width),int(height)), Image.Resampling.LANCZOS)
    data = np.asarray(img) #  PIL image to a numpy array
    bmp = potrace.Bitmap(data) # Create a bitmap from the array
    path = bmp.trace( alphamax=potrace_curves, opticurve=potrace_simple, opttolerance=potrace_simplify, turdsize=potrace_min)
    return path

def path_to_font(path, glyph, font):
    if 'glyf' in font : pen = TTGlyphPen( font.getGlyphSet() )
    if 'CFF ' in font : pen = T2CharStringPen(600, font.getGlyphSet())
    tpen = TransformPen(pen, (1, 0, 0, -1, -imgMargin, font['OS/2'].usWinAscent))

    for curve in path:
        last = (curve.start_point.x, curve.start_point.y)
        tpen.moveTo(( curve.start_point.x , curve.start_point.y ))
        for segment in curve:
            # print(segment)
            x = segment.end_point.x
            y = segment.end_point.y
            if segment.is_corner:
                # print(segment.c)
                tpen.lineTo((segment.c.x, segment.c.y))
                tpen.lineTo((x, y))
            else:
                # pen.qCurveTo(  last, (segment.c1.x,segment.c1.y),last)
                # pen.qCurveTo((segment.c2.x,segment.c2.y),(x,y),  (x,y))
                tpen.curveTo( (segment.c1.x,segment.c1.y), (segment.c2.x,segment.c2.y), (x, y))
            last = (segment.end_point.x, segment.end_point.y)

        pen.closePath()
    if 'glyf' in font : font['glyf'][glyph] = pen.glyph(dropImpliedOnCurves=True)
    if 'CFF ' in font : font['CFF '].cff.topDictIndex[0].CharStrings[glyph] = pen.getCharString()


def draw_points(path, img): # draw visual beziers
    if display_points :
        img = ImageMath.eval("a+157", a=img)
        img = img.convert('RGB')
        draw = ImageDraw.Draw(img)
        bleu = (0, 127, 255)
        bleu2 = (0, 85, 180)
        for curve in path: # draw beziers
            last = curve.start_point
            for segment in curve:
                x = segment.end_point.x
                y = segment.end_point.y
                if not segment.is_corner:
                    draw.line((segment.c1.x,segment.c1.y,last.x,last.y), bleu2, width=2)
                    draw.line((segment.c2.x,segment.c2.y,x,y), bleu2, width=2)
                    ellipse(4,segment.c1.x,segment.c1.y, bleu2, draw)
                    ellipse(4,segment.c2.x,segment.c2.y, bleu2, draw)
                last = segment.end_point

        for curve in path: # then draw points
            for segment in curve:
                x = segment.end_point.x
                y = segment.end_point.y
                ellipse( 7, x, y, bleu, draw)
                # rectangle(5, x, y, bleu, draw)
                if segment.is_corner:
                    rectangle(5,segment.c.x,segment.c.y, bleu, draw)
            ellipse(11,curve.start_point.x,curve.start_point.y, bleu, draw)
            ellipse(7,curve.start_point.x,curve.start_point.y, "white", draw)
        del draw
    return img

def ellipse(size,x,y, fill, draw):
    s = int(size/2)
    draw.ellipse((x-s,y-s,x+s,y+s), fill )
def rectangle(size,x,y, fill, draw):
    s = int(size/2)
    draw.rectangle((x-s,y-s,x+s,y+s), fill )
