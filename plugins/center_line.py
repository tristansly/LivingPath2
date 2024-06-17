from base_plugin import Plugin
import gui_utils as gui
import utils, path_utils

import numpy as np
from PIL import Image, ImageOps, ImageMath, ImageDraw
# from numba import jit , njit
from scipy.fft import fft2, ifft2
from time import time


class Layer(Plugin):
    """
    Center-line made with AutoTrace lib
     https://github.com/lemonyte/pyautotrace
     https://github.com/autotrace/autotrace
    """

    def __init__(s):
        super(Layer, s).__init__()
        # noiseImg = Image.open( utils.path('files/noise.png') ).convert('L')
        # s.noise = np.array(noiseImg.getdata(), dtype=np.float32)
        # s.noise = np.reshape(s.noise/255, ( -1, noiseImg.width))

    def gui(s, frame):
        s.outline = True
        s.outline_join_limit = 160000
        gui.Slider(frame, layer=s, max=200, name='outline_width', ini=40 ).grid(column=0, row=1, sticky='ew')
        gui.Slider(frame, layer=s, max=3, name='outline_join',    ini=2  ).grid(column=0, row=2, sticky='ew')
        gui.Slider(frame, layer=s, max=3, name='outline_cap',     ini=1  ).grid(column=0, row=3, pady=(0,50), sticky='ew')

        gui.Slider(frame, layer=s, max=1, min=0.01, ini= 0.2,format='%0.2f', name='algo_resolution', slow=True).grid(column=0, row=5, sticky='W')

        gui.Slider(frame, layer=s, max=20, min=0, ini=1,format='%0.1f', name='smooth' ).grid(column=0, row=6, sticky='ew')
        gui.Slider(frame, layer=s, max=15, min=0, ini=0.0,format='%0.1f', name='line_threshold' ).grid(column=0, row=7, sticky='ew')
        gui.Slider(frame, layer=s, max=180,  name='corner_threshold', ini=100).grid(column=0, row=8, sticky='ew')



    def run(s, img):
        originSize = img.size
        img = img.resize( (int(img.width*s.algo_resolution), int(img.height*s.algo_resolution)), Image.NEAREST)
        w = img.width
        h = img.height
        t = time()

        from autotrace import Bitmap
        image = np.asarray(img.convert("RGB"))
        bitmap = Bitmap(image)
        vector = bitmap.trace( centerline = True, line_threshold=s.line_threshold,  width_weight_factor = 1, line_reversion_threshold = s.line_threshold*2, preserve_width = True, remove_adjacent_corners = True, filter_iterations = s.smooth*4, error_threshold = 1+s.smooth, color_count = 2, corner_surround = 40*s.algo_resolution, corner_threshold = s.corner_threshold, despeckle_level = 0 )

        import main

        outline = path_utils.autotrace_to_ftoutline(vector, (1/s.algo_resolution,0,0,1/s.algo_resolution,-utils.margin, -main.font['OS/2'].usWinDescent -2*utils.margin),)

        pen = path_utils.ftoutline_contour(outline, s, main.font.getGlyphSet(), opened=True )

        img = path_utils.pen_to_img(pen, main.font, main.current_glyph)



        # img = img.resize(originSize, 1)
        print("centerline - Time Elapsed : " + str(time() - t) )
        return img

        # -------------------------------------------------------------------------------------------
