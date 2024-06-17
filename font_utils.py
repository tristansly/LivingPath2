import freetype as ft # pip install freetype-py
import numpy as np
import potracer # pip install potracer
from fontTools.pens.freetypePen import FreeTypePen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Offset
from PIL import ImageDraw, Image, ImageOps, ImageFilter, ImageMath, ImageChops, ImageFont
import beziers
import uharfbuzz as hb
import types
params = types.SimpleNamespace()
import utils, path_utils
import pprint


def glyph_to_img(font, glyph): # unused
    gs = font.getGlyphSet()
    pen = FreeTypePen( gs )
    font.getGlyphSet()[glyph].draw(pen)
    img = path_utils.pen_to_img( pen, font, glyph )
    return img


def glyph_to_img_outline(glyph, in_font, group):
    gs = in_font.getGlyphSet()
    pen = FreeTypePen( gs )
    gs[glyph].draw(pen)
    l = group.layers[0]

    # mathplotlib to manip path : check Path.circle, Path.to_polygons
    path = beziers.path.BezierPath.fromFonttoolsGlyph(in_font, glyph)
    # path = path[0].dash(lineLength = 0.1, gapLength = 0.2)
    points = []
    for curve in path :
        # for step in np.linspace(0,1,dist,endpoint=True) :
        # for step in [x/l.dots_distance for x in range(int(l.dots_distance))] :

        # curve = curve.offset(beziers.point.Point(10,10), rotateVector=False)
        rest = l.dots_distance
        for seg in curve.asSegments() :
            size = seg.length
            for position in range(int(l.dots_distance-rest), int(size), l.dots_distance) :
                points.append( seg.pointAtTime(position/size) )
                lastPos = position
            rest = size - lastPos
                # print(round(step,3), int(curve.lengthAtTime(step)) )

    outline = ft.Outline( pen.outline() )
    pen = path_utils.ftoutline_contour( outline, group.layers[0], glyph )
    img = path_utils.pen_to_img( pen, in_font, glyph )

    # test vecto
    # draw = ImageDraw.Draw(img)
    # for p in points : utils.ellipse(l.dots_size, p.x, p.y, "red", draw)
    # poly = [(p.x,img.width-p.y) for p in points]
    # draw.polygon(poly, fill ="white", outline ="blue")
    # del draw
    return img

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


def vectorization(img, params=params):
    # C++ binding : pypotrace - version mac (a tester) https://github.com/flupke/pypotrace
    # full python : potracer - https://github.com/tatarize/potrace
    # Cython : pyAutoTrace - ça marche aussi - https://github.com/lemonyte/pyautotrace
    width = float(img.size[0])*params.potrace_size
    wpercent = float(width)/float(img.size[0])
    height = int( float(img.size[1]) * float(wpercent) )
    img = img.resize((int(width),int(height)), Image.Resampling.LANCZOS)
    data = np.asarray(img) #  PIL image to a numpy array
    bmp = potracer.Bitmap(data) # Create a bitmap from the array
    path = bmp.trace( alphamax=params.potrace_curves, opticurve=True, opttolerance=params.potrace_simplify, turdsize=params.potrace_min)

    return path_utils.resize_path( path, 1/params.potrace_size )


def path_to_font(path, glyph, font, path_type="potrace"):
    if not params.letter_spacing == 0 :
        font['hmtx'][glyph] = ( int(font['hmtx'][glyph][0] + params.letter_spacing) , font['hmtx'][glyph][1])
    gs = font.getGlyphSet()

    if 'glyf' in font : pen = TTGlyphPen( gs )
    if 'CFF ' in font : pen = T2CharStringPen(600, gs)
    tpen = TransformPen(pen, (1, 0, 0, -1, -utils.margin, font['OS/2'].usWinAscent))

    if path_type == "potrace": path_to_pen(path,tpen,pen)
    if path_type == "array": array_to_pen(path,tpen,pen)

    # pprint.pprint(vars(gs[glyph]))
    if 'glyf' in font : font['glyf'][glyph] = pen.glyph(dropImpliedOnCurves=True)
    if 'CFF ' in font :
        cs = pen.getCharString()
        cs.compile()
        font['CFF '].cff.topDictIndex[0].CharStrings[glyph].bytecode = cs.bytecode
def path_to_pen(path,tpen,pen):
    for curve in path:
        tpen.moveTo(( curve.start_point.x , curve.start_point.y ))
        for segment in curve:
            x = segment.end_point.x
            y = segment.end_point.y
            if segment.is_corner:
                tpen.lineTo((segment.c.x, segment.c.y))
                tpen.lineTo((x, y))
            else:
                tpen.curveTo( (segment.c1.x,segment.c1.y), (segment.c2.x,segment.c2.y), (x, y))
        pen.closePath()
def array_to_pen(arr,tpen,pen):
    for cur in arr:
        tpen.moveTo(( cur[0][2] , cur[0][3] ))
        for seg in cur:
            x = seg[0]
            y = seg[1]
            if len(seg) == 4:
                tpen.lineTo((seg[2], seg[3]))
                tpen.lineTo((x, y))
            else:
                tpen.curveTo( (seg[2],seg[3]), (seg[4],seg[5]), (x, y))
        pen.closePath()

# -------------------------------------------------------------------------------------------
def text_to_img_PIL(txt):
    img = Image.new("RGB", (1000, 1000))
    d = ImageDraw.Draw(img)
    new_font = ImageFont.truetype(utils.path("out.otf"), size=148) # layout_engine=ImageFont.Layout.BASIC
    d.text((0, 200), txt, font=new_font, fill="#fff")
    return img

def text_to_img_HB(text, ttfont, hbfont):
    s = 5
    # text = 'とは、主に兄妹姉以上継続'
    # takes metrics from inputed font with HB  & draw from TTFont object
    # base from https://fonttools.readthedocs.io/en/latest/pens/freetypePen.html
    # en1, en2, ar, ja = 'VA Typesetting', 'Jeff', 'صف الحروف', 'たいぷせっと'
    # (ar,  'files/1.ttf',     'rtl', 1374, -738, None, None, False, {"kern": True, "liga": True}),
    # (ja,  'files/1.otf',     'ltr', 880,  -120, 500,  -500, False, {"palt": True, "kern": True}),
    # (ja,  'files/1.otf',     'ttb', 880,  -120, 500,  -500, False, {"vert": True, "vpal": True, "vkrn": True})
    typo_ascender, typo_descender = ttfont['OS/2'].usWinAscent, ttfont['OS/2'].usWinDescent
    if 'hhea' in ttfont: h_ascender,h_descender = ttfont["hhea"].ascent,ttfont["hhea"].descent
    if 'vhea' in ttfont: v_ascender,v_descender = ttfont["vhea"].ascent,ttfont["vhea"].descent
    contain = False
    direction = 'ltr'
    features = {"kern": True, "liga": True}

    buf = hb.Buffer()
    buf.add_str(text)
    # buf.direction = direction
    buf.replacement_codepoint =ttfont.getGlyphID('space')
    buf.not_found_glyph = ttfont.getGlyphID('space')
    buf.guess_segment_properties()
    # try:
    hb.shape(hbfont, buf, features)
    # except Exception as e: print(e)

    x, y = 0, 0
    pen = FreeTypePen( ttfont.getGlyphSet() )
    if buf.glyph_positions != None :
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            gid = info.codepoint
            transformed = TransformPen(pen, (1,0,0,1, x+pos.x_offset, y+pos.y_offset ))
            # g = ttfont.getBestCmap()[ord(' ')]
            # try: g = ttfont.getBestCmap()[ord(char)]
            # except Exception as e:
            #     print("(utils.py) Char to glyph error : '"+char+"'")
            # ttfont.getGlyphSet()[ g ].draw( transformed )

            ttfont.getGlyphSet()[ ttfont.getGlyphName(gid) ].draw( transformed )
            # hbfont.draw_glyph_with_pen(gid, transformed)

            x += pos.x_advance + params.letter_spacing
            y += pos.y_advance

        offset, width, height = None, None, None
        if direction in ('ltr', 'rtl'):
            offset = (0, -h_descender//s)
            width  = x
            height = h_ascender - h_descender
        else:
            offset = (-v_descender//s, -y//s)
            width  = v_ascender - v_descender
            height = -y

        # img = pen.image(width=width/s, height=height/s, transform=Offset(*offset))
        # try:
        img = pen.image(width=width//s, height=height//s, transform=(1/s,0,0,1/s,*offset), contain=contain)
        # except Exception as e:
        #     print("harfbuzz error : ", e)
        #     img = Image.new('ARGB', (1, 1))
        img = ImageOps.invert(img.getchannel('A'))
    else: img = Image.new('L', (1, 1))
    return img

# -------------------------------------------------------------------------------------------
def operator_img(img, img2, op):
    if op==0 : img = ImageChops.darker( img, img2 )
    elif op==1 : img = ImageChops.add( ImageOps.invert(img), img2 )
    elif op==2 : img = ImageChops.add( img, ImageOps.invert(img2) )
    elif op==3 : img = ImageChops.lighter( img, img2 )
    elif op==4 : img = ImageOps.invert( ImageChops.difference(img, img2) )
    return img

def draw_points(path, img): # draw visual beziers with PIL
    if params.display_points :
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
def rename_font(font, new_name):
    for record in in_font['name'].names:
        if record.nameID in [1, 4, 6]:  # Family name, Full name, PostScript name
            record.string = new_name.encode(record.getEncoding())
        # if record.nameID == 9:  # Authors names
        #     record.string = new_name.encode(record.getEncoding())
        # if record.nameID == 12:  # Autors URLs Links
        #     record.string = new_name.encode(record.getEncoding())
    return font
