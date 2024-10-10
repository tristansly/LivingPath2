from base_plugin import Plugin
import gui_utils as gui
import utils, path_utils

import numpy as np
from PIL import Image, ImageOps, ImageMath, ImageDraw
# from numba import jit , njit
from autotrace import Bitmap
import main
import cv2


class Layer(Plugin):
    """
    Center-line made with AutoTrace lib
     https://github.com/lemonyte/pyautotrace
     https://github.com/autotrace/autotrace
    """

    def __init__(s):
        super(Layer, s).__init__()

    def gui(s, frame):
        s.outline = True
        s.outline_join_limit = 160000
        gui.Slider(frame, layer=s, min=1, max=200, name='outline_width', ini=40 ).pack(anchor='w')
        gui.Slider(frame, layer=s, max=3, name='outline_join',    ini=2  ).pack(anchor='w')
        gui.Optionbutton(frame, layer=s, nbr=3, ini=2, pos='inline', name='outline_cap', img_name='end').pack(anchor='w')


        gui.Slider(frame, layer=s, max=1, min=0.01, ini= 0.2,format='%0.2f', name='algo_resolution', slow=True).pack(anchor='w', pady=(25,0))
        gui.Slider(frame, layer=s, max=20, min=0, ini=1,format='%0.1f', name='smooth' ).pack(anchor='w')
        gui.Slider(frame, layer=s, max=20, min=0, ini=1,format='%0.1f', name='smooth2' ).pack(anchor='w')
        gui.Slider(frame, layer=s, max=15, min=0, ini=0.0,format='%0.1f', name='line_threshold' ).pack(anchor='w')
        gui.Slider(frame, layer=s, max=180,  name='corner_threshold', ini=100).pack(anchor='w')

        gui.Slider(frame, layer=s, max=100,  name='i_dot', ini=50).pack(anchor='w', pady=(25,0))
        gui.Slider(frame, layer=s, max=180,  name='angle', ini=0).pack(anchor='w')


    def run(s, img):
        originSize = img.size

        img = np.asarray(img).astype(np.uint8)
        img = s.detect_points(img);
        img = Image.fromarray(img)

        img = img.resize( (int(img.width*s.algo_resolution), int(img.height*s.algo_resolution)), Image.NEAREST)
        w = img.width
        h = img.height


        img = np.asarray(img.convert("RGB"))

        bitmap = Bitmap(img)
        vector = bitmap.trace(
            centerline = True,
            line_threshold=s.line_threshold,
            width_weight_factor = 1,
            line_reversion_threshold = s.line_threshold*2,
            preserve_width = True,
            remove_adjacent_corners = True,
            filter_iterations = s.smooth2,
            error_threshold = s.smooth,
            color_count = 2,
            corner_surround = 40*s.algo_resolution,
            corner_threshold = s.corner_threshold,
            despeckle_level = 0 )


        img = Image.fromarray(img)
        img = img.resize(originSize, 1)

        outline = path_utils.autotrace_to_ftoutline(vector,
        (1/s.algo_resolution,0,0,1/s.algo_resolution,-utils.margin, -main.font['OS/2'].usWinDescent -2*utils.margin))
        pen = path_utils.ftoutline_contour(outline, s, main.font.getGlyphSet(), opened=True )
        img = path_utils.pen_to_img(pen, main.font, main.current_glyph)


        return img

    def detect_points(s,img):

        circles = cv2.HoughCircles(img,cv2.HOUGH_GRADIENT,1,40, param1=50,param2=50,minRadius=40,maxRadius=100)


        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0,:]:
                cv2.circle(img,(i[0],i[1]),i[2]+5,255,-1) # cache white circle
                cv2.ellipse(img,(i[0],i[1]), (i[2]-s.i_dot, i[2]), s.angle,0,360,0,-1)
                print("circle diticted")
        return img
