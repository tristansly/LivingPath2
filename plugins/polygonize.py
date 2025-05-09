from base_plugin import Plugin
import gui_utils as gui
import utils

import pymunk
import pymunk.autogeometry
from pymunk import Vec2d
from PIL import Image, ImageDraw

class Layer(Plugin):
    """attraction repultion particles field
    """
    def __init__(s):
        super(Layer, s).__init__()
        s.ini_space = pymunk.Space()

    def gui(s, frame):

        l = gui.LockSliders( frame, True,
            dict(max=500, ini=200, min=1, layer=s, name='resolution_width'),
            dict(max=500, ini=200, min=1, layer=s, name='resolution_height') )
        l.pack(anchor='nw')
        gui.Slider(frame, max=150, min=0, ini= 30, layer=s, name='simplify').pack(anchor='nw')

    def run(s, img):

        def sample_func(point):
            try:
                p = int(point[0]), int(point[1])
                color = img.getpixel(p)
                return color
            except Exception as e:
                print(e)
                return 0

        line_set = pymunk.autogeometry.march_soft(
            pymunk.BB(0, 0, img.size[0]-1, img.size[1]-1), s.resolution_width, s.resolution_height, 127, sample_func
        )

        # detector = cv2.SimpleBlobDetector() # bug with cv2
        # line_set = detector.detect()

        shape = ImageDraw.Outline()
        for polyline in line_set:
            line = pymunk.autogeometry.simplify_curves(polyline, s.simplify)

            if len(line) : shape.move(line[0].x,line[0].y)

            for i in range(len(line) - 1):
                p1 = line[i]
                p2 = line[i+1]
                shape.line(p2.x,p2.y)

        img_draw = Image.new('L', img.size, 255)
        draw = ImageDraw.Draw(img_draw)
        draw.shape(shape, outline="black")

        del draw
        return img_draw
