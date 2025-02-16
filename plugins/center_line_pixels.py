from base_plugin import Plugin
import gui_utils as gui
import utils, path_utils

import numpy as np
from PIL import Image, ImageOps, ImageMath, ImageDraw

import cv2
from skimage.morphology import medial_axis, skeletonize  # pip install scikit-image

import main

class Layer(Plugin):
    """
    Center-line made with cv2 lib
    """

    def __init__(s):
        super(Layer, s).__init__()

    def gui(s, frame):
        s.outline = True
        s.outline_join_limit = 160000

        gui.Slider(frame, min=1, max=200, ini=60, layer=s, name='size').pack(anchor='w')

        skel = gui.LockSliders( frame, False,
            dict(layer=s, min=1, max=50, ini=1, name='distortion_width'),
            dict(layer=s, min=1, max=50, ini=1, name='distortion_height' )
        )
        skel.switch()
        opt = gui.Optionbutton(frame, layer=s, nbr=6, pos='inline', name='mode', img_name='op' )
        opt.callback = lambda : skel.switch( opt.var in (4,5) )

        opt.pack(anchor='w')
        skel.pack(anchor='w', pady=(20,0))

        ### unused : dilate ###
        # gui.LockSliders( frame, True,
        # dict(layer=s, min=1, max=50, ini=1, name='brush_width'),
        # dict(layer=s, min=1, max=50, ini=1, name='brush_height' )
        # ).pack(anchor='w')
        # gui.Optionbutton(frame, layer=s, nbr=3, pos='inline', name='brush' ).pack(anchor='w')
        ### unused : fonttools vecto drawn ###
        # gui.Slider(frame, layer=s, max=1, min=0.01, ini= 0.2,format='%0.2f', name='algo_resolution', slow=True).pack(anchor='w')
        # gui.Slider(frame, layer=s, min=1, max=200, name='outline_width', ini=40 ).pack(anchor='w')
        # gui.Slider(frame, layer=s, max=3, name='outline_join',    ini=2  ).pack(anchor='w')
        # gui.Optionbutton(frame, layer=s, nbr=3, ini=2, pos='inline', name='outline_cap', img_name='end').pack(anchor='w')
        ### unused : cv2 approxPoly ###
        # gui.Slider(frame, layer=s, max=1000, min=0, ini= 10,format='%0.2f', name='precision', slow=True).pack(anchor='w')

    def options(s):
            s.skel.switch( s.opt.var in (4,5) )

    def run(s, img):

        img = np.asarray(img).astype('uint8')
        _, img = cv2.threshold(img,127,255,cv2.THRESH_BINARY_INV)

        if s.mode in (0,3) : img = img.astype(np.bool_)

        if s.mode == 0 : img = skeletonize(img, method='lee') # 0.23 minimalist
        # if s.mode == 0 : img = skeletonize(img, method='zhang') # 0.12 fastest
        if s.mode == 1 : img = cv2.ximgproc.thinning(img, thinningType=cv2.ximgproc.THINNING_ZHANGSUEN) # 0.15 ressemble au lee
        if s.mode == 2 : img = cv2.ximgproc.thinning(img, thinningType=cv2.ximgproc.THINNING_GUOHALL) # 0.2
        if s.mode == 3 : img = medial_axis(img) # 0.15 calld topological skeleton
        if s.mode == 4 : img = s.cv_custo_skeleton(img,0)
        if s.mode == 5 : img = s.cv_custo_skeleton(img,1)

        if s.mode in (0,3) : img = img.astype(np.uint8) * 255

        img = s.vecto(img)

        ### dilate (cap options but irregular...)
        # img = cv2.bitwise_not(img)
        # k = [ cv2.MORPH_RECT, cv2.MORPH_CROSS, cv2.MORPH_ELLIPSE ]
        # kernel = cv2.getStructuringElement(k[s.brush],(s.brush_width,s.brush_height))
        # img = cv2.erode(img,kernel,iterations = s.size )

        img = Image.fromarray(img)
        return img

        # -------------------------------------------------------------------------------------------
    def cv_custo_skeleton(s, img, mode) :
        k = [ cv2.MORPH_RECT, cv2.MORPH_CROSS, cv2.MORPH_ELLIPSE ] # ellipse == cross

        size = np.size(img)
        skel = np.zeros(img.shape,np.uint8)
        ret,img = cv2.threshold(img,127,255,0)
        element = cv2.getStructuringElement(k[mode],(s.distortion_width*2+1,s.distortion_height*2+1) )
        done = False
        while(not done):
            eroded = cv2.erode(img,element)
            temp = cv2.dilate(eroded,element)
            temp = cv2.subtract(img,temp)
            skel = cv2.bitwise_or(skel,temp)
            img = eroded.copy()
            zeros = size - cv2.countNonZero(img)
            if zeros==size : done = True
        img = skel
        return img

    def vecto(s, img):
        _, img = cv2.threshold(img,127,255,0)

        contours = cv2.findContours(img, cv2.RETR_EXTERNAL  , cv2.CHAIN_APPROX_SIMPLE)[0] # cv2.RETR_LIST
        # contours = [cv2.approxPolyDP(p, 0.02 * s.precision, False) for p in contours]

        img = np.ones(img.shape, np.uint8) * 255
        cv2.drawContours(img, contours, -1, 0, s.size)


        ### draw contours with fonttools ( irregular cap options since contours are closed )

        # outline = path_utils.cv2_to_ftoutline(contours, (1/s.algo_resolution,0,0,-1/s.algo_resolution,-utils.margin,
        # main.font['OS/2'].usWinDescent + main.font['OS/2'].usWinAscent - utils.margin ),)
        # pen = path_utils.ftoutline_contour(outline, s, main.font.getGlyphSet(), opened=True )
        # img = path_utils.pen_to_img(pen, main.font, main.current_glyph)
        # img = np.asarray(img).astype('uint8')

        return img
