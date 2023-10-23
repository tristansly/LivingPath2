import freetype as ft
import numpy as np
import potrace # pip install potracer
from fontTools.pens.freetypePen import FreeTypePen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Offset
from PIL import ImageDraw, Image, ImageOps, ImageFilter, ImageMath, ImageChops

import utils
import pprint

test_bool = 0

potrace_curves = 0.90
potrace_simplify = 0.15
potrace_min = 2.0
potrace_size = 1
potrace_simple = 1
display_points = 0
outline_width = 100
outline_join = 2
outline_join_limit = 160000

imgMargin = 200

def glyph_to_img(font, glyph):
    gs = font.getGlyphSet()
    pen = FreeTypePen( gs )

    gs[glyph].draw(pen)
    height = font['OS/2'].usWinAscent + font['OS/2'].usWinDescent + 2*imgMargin
    width = gs[glyph].width + 2*imgMargin
    img = pen.image(width=width,height=height,transform=Offset(imgMargin,font['OS/2'].usWinDescent+2*imgMargin))
    return ImageOps.invert(img.getchannel('A'))


def glyph_to_img_outline(font,g):
    gs = font.getGlyphSet()
    pen = FreeTypePen( gs )
    gs[g].draw(pen)
    height = font['OS/2'].usWinAscent + font['OS/2'].usWinDescent + 2*imgMargin
    width = gs[g].width + 2*imgMargin

    outline = ft.Outline( pen.outline() )
    pen = FreeTypePen( gs ) # new empty pen

    stroker = ft.Stroker()
    stroker.set(outline_width*50, ft.FT_STROKER_LINECAP_ROUND, ft.FT_STROKER_LINEJOIN_ROUND, 0)
    stroker.parse_outline(outline, False)

    n_points, n_contours = stroker.get_counts()
    with utils.new_outline(n_points, n_contours) as stroked_outline:
        stroker.export(stroked_outline)
        stroked_outline.decompose(pen, move_to=move_to, line_to=line_to, conic_to=conic_to, cubic_to=cubic_to, shift=0,delta=0)
    pen.closePath()

    img = pen.image(width=width,height=height,transform=Offset(imgMargin,font['OS/2'].usWinDescent+2*imgMargin))
    return ImageOps.invert(img.getchannel('A'))

def move_to(a, ctx):
    ctx.lineTo( pt(a) )
    ctx.closePath()
    ctx.moveTo( pt(a) )
def line_to(a, ctx):
    ctx.lineTo( pt(a) )
def conic_to(a, b, ctx):
    ctx.curveTo( pt(a), pt(b), pt(b))
def cubic_to(a, b, c, ctx):
    ctx.curveTo(  pt(a), pt(b), pt(c) )
def pt(a):
    coef = 64
    return (a.x/coef, a.y/coef)

def glyph_to_font_outline(in_font, font, g, group):
    gs = in_font.getGlyphSet()
    fpen = FreeTypePen( gs )
    gs[g].draw(fpen)
    outline = ft.Outline( fpen.outline() )

    if 'glyf' in font : pen = TTGlyphPen( font.getGlyphSet() )
    if 'CFF ' in font : pen = T2CharStringPen(600, font.getGlyphSet())
    tpen = TransformPen(pen, (1, 0, 0, 1, 0, 0))

    stroker = ft.Stroker()
    stroker.set(outline_width*20, ft.FT_STROKER_LINECAP_BUTT, outline_join, outline_join_limit)
    stroker.parse_outline(outline, False)

    n_points, n_contours = stroker.get_counts()
    with utils.new_outline(n_points, n_contours) as stroked_outline:
        stroker.export(stroked_outline)
        stroked_outline.decompose(tpen, move_to=move_to,line_to=line_to,conic_to=conic_to,cubic_to=cubic_to,shift=0,delta=0)
        tpen.closePath()

    if 'glyf' in font : font['glyf'][g] = pen.glyph(dropImpliedOnCurves=False)
    if 'CFF ' in font : font['CFF '].cff.topDictIndex[0].CharStrings[g] = pen.getCharString()


def vectorization(img):
    width = float(img.size[0])*potrace_size
    wpercent = float(width)/float(img.size[0])
    height = int( float(img.size[1]) * float(wpercent) )
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
        # last = (curve.start_point.x, curve.start_point.y)
        tpen.moveTo(( curve.start_point.x , curve.start_point.y ))
        for segment in curve:
            x = segment.end_point.x
            y = segment.end_point.y
            if segment.is_corner:
                tpen.lineTo((segment.c.x, segment.c.y))
                tpen.lineTo((x, y))
            else:
                # pen.qCurveTo(  last, (segment.c1.x,segment.c1.y),last)
                # pen.qCurveTo((segment.c2.x,segment.c2.y),(x,y),  (x,y))
                tpen.curveTo( (segment.c1.x,segment.c1.y), (segment.c2.x,segment.c2.y), (x, y))
            # last = (segment.end_point.x, segment.end_point.y)

        pen.closePath()
    if 'glyf' in font : font['glyf'][glyph] = pen.glyph(dropImpliedOnCurves=True)
    if 'CFF ' in font : font['CFF '].cff.topDictIndex[0].CharStrings[glyph] = pen.getCharString()

def operator_img(img, img2, operator):
    op = {0 : ImageChops.add,
        1 : ImageChops.difference,
        2 : ImageChops.darker,
        3 : ImageChops.lighter
    }
    return op[operator]( img, img2 )

def draw_points(path, img): # draw visual beziers with PIL
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
