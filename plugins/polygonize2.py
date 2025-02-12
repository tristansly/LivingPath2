import gui_utils as gui
import font_utils, path_utils
from base_plugin import Plugin

from fontTools.pens.freetypePen import FreeTypePen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Offset
import beziers

from PIL import ImageFilter, Image, ImageOps, ImageDraw
import main
import utils

class Layer(Plugin):
    """polygonize letter."""

    def gui(s, frame):
        gui.Slider(frame, layer=s, min=0.01, max=2, name='accuracy', format='%0.2f' , ini=0.03).pack(anchor='w')
        setattr(s, "simplify_path", float(0.45)) # we dont need symplify control
        gui.Slider(frame, layer=s, max=1.34, name='curves_limit', format='%0.2f', ini=0.0).pack(anchor='w')


        gui.Slider(frame, layer=s, max=200, name='dots_distance', ini=100).pack(anchor='w')
        gui.Slider(frame, layer=s, max=200, name='dots_size', ini=10).pack(anchor='nw')


    def run(s, img):
        g = main.current_glyph
        if False:
            path = font_utils.vectorization(img, params=s)

            gs = main.font.getGlyphSet()
            pen = FreeTypePen( gs )
            font_utils.path_to_pen( path,pen )

            s = 1/ (main.font['head'].unitsPerEm /1000) # some main.font are more than 1000 u/em
            height = main.font['OS/2'].usWinAscent*s + main.font['OS/2'].usWinDescent*s + 2*utils.margin
            width = gs[g].width*s + 2*utils.margin
            img = pen.image(width=width,height=height,transform=(s, 0, 0, -s, 0, height) )

            img = ImageOps.invert(img.getchannel('A'))

        else :

            # mathplotlib to manip path : check Path.circle, Path.to_polygons
            path = beziers.path.BezierPath.fromFonttoolsGlyph(main.font, g)
            print(g)
            # path = path[0].dash(lineLength = 0.1, gapLength = 0.2)
            points = []
            for curve in path :
                # for step in np.linspace(0,1,dist,endpoint=True) :
                # for step in [x/s.dots_distance for x in range(int(s.dots_distance))] :

                # curve = curve.offset(beziers.point.Point(10,10), rotateVector=False)
                rest = s.dots_distance
                for seg in curve.asSegments() :
                    size = seg.length
                    for position in range(int(s.dots_distance-rest), int(size), s.dots_distance) :
                        points.append( seg.pointAtTime(position/size) )
                        lastPos = position
                    rest = size - lastPos
                        # print(round(step,3), int(curve.lengthAtTime(step)) )

            # test vecto
            # draw = ImageDraw.Draw(img)
            # for p in points : utils.ellipse(s.dots_size, p.x, p.y, "red", draw)
            poly = [(p.x,img.width-p.y) for p in points]
            # draw.polygon(poly, fill ="white", outline ="blue")
            # del draw

            shape = ImageDraw.Outline()
            for line in poly:
                # line = pymunk.autogeometry.simplify_curves(polyline, s.z)

                if len(line) : shape.move(line[0][0],line[0][1])

                for i in range(len(line) - 1):
                    p1 = line[i]
                    p2 = line[i+1]
                    shape.line(p2.x,p2.y)

            img_draw = Image.new('L', img.size, 255)
            draw = ImageDraw.Draw(img_draw)
            draw.shape(shape, outline="black")

            del draw
            return img_draw


        return img
