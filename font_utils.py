import freetype as ft # pip install freetype-py
import numpy as np
import potrace # pip install potracer
from fontTools.pens.freetypePen import FreeTypePen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Offset
from PIL import ImageDraw, Image, ImageOps, ImageFilter, ImageMath, ImageChops, ImageFont
import beziers
from beziers.path import BezierPath

import utils
import pprint

imgMargin = 200

def glyph_to_img(font, glyph): # unused
    gs = font.getGlyphSet()
    pen = FreeTypePen( gs )
    font.getGlyphSet()[glyph].draw(pen)
    height = font['OS/2'].usWinAscent + font['OS/2'].usWinDescent + 2*imgMargin
    width = gs[glyph].width + 2*imgMargin
    img = pen.image(width=width,height=height,transform=Offset(imgMargin,font['OS/2'].usWinDescent+2*imgMargin))
    return ImageOps.invert(img.getchannel('A'))


def glyph_to_img_outline(g, in_font, group):
    gs = in_font.getGlyphSet()
    pen = FreeTypePen( gs )
    gs[g].draw(pen)
    outline = ft.Outline( pen.outline() )
    pen = FreeTypePen( gs )
    l = group.layers[0]

    # mathplotlib to manip path : check Path.circle, Path.to_polygons
    path = beziers.path.BezierPath.fromFonttoolsGlyph(in_font, g)
    points = []
    for curve in path :
        # for step in np.linspace(0,1,dist,endpoint=True) :
        for step in np.arange(0.0, 1.0, l.dots_distance/200) :
            points.append( curve.pointAtTime(step) )

    stroker = ft.Stroker()
    width, linecap, join, limit =  l.outline_width, ft.FT_STROKER_LINECAP_BUTT, l.outline_join, l.outline_join_limit
    coef = 70
    stroker.set(width*coef, linecap, join, limit)
    if not l.outline and width>100 :  stroker.set( (width-100)*coef, linecap, join, limit)
    if not l.outline and width<=100 : stroker.set( (100-width)*coef, linecap, join, limit)
    stroker.parse_outline(outline, False)

    n_points, n_contours = stroker.get_counts()
    with utils.new_outline(n_points, n_contours) as stroked_outline:
        if l.outline     : stroker.export(stroked_outline)
        if not l.outline and l.outline_width>100: stroker.export_border(outline.get_outside_border(),stroked_outline)
        if not l.outline and l.outline_width<=100: stroker.export_border(outline.get_inside_border(),stroked_outline)
        pen.moveTo( (0,0) )
        stroked_outline.decompose(pen, move_to=move_to_reverse,line_to=line_to,conic_to=conic_to,cubic_to=cubic_to,shift=0,delta=0)
        pen.closePath()

    height = in_font['OS/2'].usWinAscent + in_font['OS/2'].usWinDescent + 2*imgMargin
    width = gs[g].width + 2*imgMargin
    img = pen.image(width=width,height=height,transform=Offset(imgMargin,in_font['OS/2'].usWinDescent+2*imgMargin))

    draw = ImageDraw.Draw(img)
    # for p in points :
    #     utils.ellipse(9, p.x, img.width-p.y, "red", draw)
    del draw
    return ImageOps.invert(img.getchannel('A'))

def move_to_reverse(a, ctx):
    ctx.moveTo( pt(a) )
    ctx.closePath()
    ctx.moveTo( pt(a) )
    ctx.lineTo( pt(a) )
def move_to(a, ctx):
    ctx.lineTo( pt(a) )
    ctx.closePath()
    ctx.moveTo( pt(a) )
def line_to(a, ctx):        ctx.lineTo( pt(a) )
def conic_to(a, b, ctx):    ctx.curveTo( pt(a), pt(b), pt(b))
def cubic_to(a, b, c, ctx): ctx.curveTo(  pt(a), pt(b), pt(c) )
def pt(a):
    coef = 64
    return (a.x//coef, a.y//coef)  # not sure about // : int or float

def glyph_to_font_outline(g, in_font, font, group):
    l = group.layers[0]
    gs = in_font.getGlyphSet()
    fpen = FreeTypePen( gs )
    gs[g].draw(fpen)
    outline = ft.Outline( fpen.outline() )

    if 'glyf' in font : pen = TTGlyphPen( font.getGlyphSet() )
    if 'CFF ' in font : pen = T2CharStringPen(600, font.getGlyphSet())
    tpen = TransformPen(pen, (1, 0, 0, 1, 0, 0))

    stroker = ft.Stroker()
    width, linecap, join, limit =  l.outline_width, ft.FT_STROKER_LINECAP_BUTT, l.outline_join, l.outline_join_limit
    stroker.set(width*20, linecap, join, limit)
    if not l.outline and width>100 :  stroker.set( (width-100)*20, linecap, join, limit)
    if not l.outline and width<=100 : stroker.set( (100-width)*20, linecap, join, limit)
    stroker.parse_outline(outline, False)

    n_points, n_contours = stroker.get_counts()
    with utils.new_outline(n_points, n_contours) as stroked_outline:
        if l.outline     : stroker.export(stroked_outline)
        if not l.outline and l.outline_width>100: stroker.export_border(outline.get_outside_border(),stroked_outline)
        if not l.outline and l.outline_width<=100: stroker.export_border(outline.get_inside_border(),stroked_outline)
        stroked_outline.decompose(tpen, move_to=move_to,line_to=line_to,conic_to=conic_to,cubic_to=cubic_to,shift=0,delta=0)
        tpen.closePath()

    if 'glyf' in font : font['glyf'][g] = pen.glyph(dropImpliedOnCurves=False)
    if 'CFF ' in font : font['CFF '].cff.topDictIndex[0].CharStrings[g] = pen.getCharString()


def vectorization(img):
    # C++ binding : pypotrace - version mac (a tester) https://github.com/flupke/pypotrace
    # full python : potracer - https://github.com/tatarize/potrace
    # Cython : pyAutoTrace - ça marche aussi - https://github.com/lemonyte/pyautotrace
    width = float(img.size[0])*potrace_size
    wpercent = float(width)/float(img.size[0])
    height = int( float(img.size[1]) * float(wpercent) )
    img = img.resize((int(width),int(height)), Image.Resampling.LANCZOS)
    data = np.asarray(img) #  PIL image to a numpy array
    bmp = potrace.Bitmap(data) # Create a bitmap from the array
    path = bmp.trace( alphamax=potrace_curves, opticurve=potrace_simple, opttolerance=potrace_simplify, turdsize=potrace_min)

    return resize_path( path, 1/potrace_size )


def path_to_font(path, glyph, font):
    if not letter_spacing == 0 :
        font['hmtx'][glyph] = ( int(font['hmtx'][glyph][0] + letter_spacing) , font['hmtx'][glyph][1])
    gs = font.getGlyphSet()

    if 'glyf' in font : pen = TTGlyphPen( gs )
    if 'CFF ' in font : pen = T2CharStringPen(600, gs)
    tpen = TransformPen(pen, (1, 0, 0, -1, -imgMargin, font['OS/2'].usWinAscent))

    pprint.pprint(path)
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
    # pprint.pprint(vars(gs[glyph]))
    if 'glyf' in font : font['glyf'][glyph] = pen.glyph(dropImpliedOnCurves=True)
    if 'CFF ' in font :
        cs = pen.getCharString()
        cs.compile()
        font['CFF '].cff.topDictIndex[0].CharStrings[glyph].bytecode = cs.bytecode
# -------------------------------------------------------------------------------------------
def text_to_img_PIL(txt):
    img = Image.new("RGB", (1000, 1000))
    d = ImageDraw.Draw(img)
    new_font = ImageFont.truetype(utils.path("out.otf"), size=148) # layout_engine=ImageFont.Layout.BASIC
    d.text((0, 200), txt, font=new_font, fill="#fff")
    return img

def text_to_img_HB(text, ttfont, hbfont):
    # takes metrics from inputed font with HB  & draw from TTFont object
    # base from https://fonttools.readthedocs.io/en/latest/pens/freetypePen.html
    import uharfbuzz as hb
    # en1, en2, ar, ja = 'VA Typesetting', 'Jeff', 'صف الحروف', 'たいぷせっと'
    # (ar,  'files/1.ttf',     'rtl', 1374, -738, None, None, False, {"kern": True, "liga": True}),
    # (ja,  'files/1.otf',     'ltr', 880,  -120, 500,  -500, False, {"palt": True, "kern": True}),
    # (ja,  'files/1.otf',     'ttb', 880,  -120, 500,  -500, False, {"vert": True, "vpal": True, "vkrn": True})
    direction, typo_ascender, typo_descender, vhea_ascender, vhea_descender, contain, features = 'ltr', ttfont['OS/2'].usWinAscent, ttfont['OS/2'].usWinDescent, ttfont["hhea"].ascent, ttfont["hhea"].descent, True,  {"kern": True, "liga": True}

    buf = hb.Buffer()
    buf.direction = direction
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hbfont, buf, features)

    x, y = 0, 0
    pen = FreeTypePen( ttfont.getGlyphSet() )
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        gid = info.codepoint
        transformed = TransformPen(pen, (1,0,0,1, x+pos.x_offset, y+pos.y_offset ))
        ttfont.getGlyphSet()[ hbfont.glyph_to_string(gid) ].draw( transformed )
        x += pos.x_advance + letter_spacing
        y += pos.y_advance

    offset, width, height = None, None, None
    if direction in ('ltr', 'rtl'):
        offset = (0, -typo_descender)
        width  = x
        height = typo_ascender - typo_descender
    else:
        offset = (-vhea_descender, -y)
        width  = vhea_ascender - vhea_descender
        height = -y

    img = pen.image(width=width, height=height, transform=Offset(*offset), contain=contain)
    img = ImageOps.invert(img.getchannel('A'))
    background = Image.new('L', (1500, 1500), (240))
    img.thumbnail((background.size), Image.Resampling.LANCZOS)
    img_w, img_h = img.size
    bg_w, bg_h = background.size
    background.paste(img, (0, bg_h//2) )

    return background

# -------------------------------------------------------------------------------------------
def operator_img(img, img2, op):
    if op==0 : img = ImageChops.darker( img, img2 )
    elif op==1 : img = ImageChops.add( ImageOps.invert(img), img2 )
    elif op==2 : img = ImageChops.add( img, ImageOps.invert(img2) )
    elif op==3 : img = ImageChops.lighter( img, img2 )
    elif op==4 : img = ImageOps.invert( ImageChops.difference(img, img2) )
    return img

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
                    utils.ellipse(4,segment.c1.x,segment.c1.y, bleu2, draw)
                    utils.ellipse(4,segment.c2.x,segment.c2.y, bleu2, draw)
                last = segment.end_point

        for curve in path: # then draw points
            for segment in curve:
                x = segment.end_point.x
                y = segment.end_point.y
                utils.ellipse( 7, x, y, bleu, draw)
                # rectangle(5, x, y, bleu, draw)
                if segment.is_corner:
                    utils.rectangle(5,segment.c.x,segment.c.y, bleu, draw)
            utils.ellipse(11,curve.start_point.x,curve.start_point.y, bleu, draw)
            utils.ellipse(7, curve.start_point.x,curve.start_point.y, "white", draw)
        del draw
    return img

# -------------------------------------------------------------------------------------------
def resize_path( path, s ):
    for curve in path:
        for segment in curve:
            segment.end_point.x *= s
            segment.end_point.y *= s
            if segment.is_corner:
                segment.c.x *= s
                segment.c.y *= s
            else:
                segment.c1.x *= s
                segment.c1.y *= s
                segment.c2.x *= s
                segment.c2.y *= s
    return path
