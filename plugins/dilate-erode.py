from base_plugin import Plugin
import gui_utils as gui

import cv2
import numpy as np
from PIL import Image

class Layer(Plugin):
    """outline font layer"""

    def __init__(s):
        super(Layer, s).__init__()

        s.contour_val = 100
        s.kernel_size = 5

    def gui(s, frame):
        gui.Slider(frame, max=200, layer=s, name='contour_val').grid(column=1, row=1, sticky='W')
        gui.Slider(frame, max=20, layer=s, name='kernel_size').grid(column=1, row=2, sticky='W')

    def run(s, img):

        # cv_img = np.array(img)
        #
        # # kernel = np.ones((s.kernel_size,s.kernel_size),np.uint8)
        # kernel =  cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(s.kernel_size,s.kernel_size))
        # if s.contour_val < 100 :
        #     erosion = cv2.dilate(cv_img,kernel,iterations = 100-s.contour_val )
        # else :
        #     erosion = cv2.erode(cv_img,kernel,iterations = s.contour_val-100 )
        #
        #
        #
        # img = Image.fromarray(erosion)

        return img

    # def initiate(s, g):
    #     shape = g
    #     return shape
