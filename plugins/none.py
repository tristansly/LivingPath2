from base_plugin import plugin
import gui_utils as gui

import cairo
from io import BytesIO
from PIL import Image

class Layer(plugin):
    """outline font layer"""

    def __init__(s):
        super(Layer, s).__init__()

        s.contour_val = 100
        # s.kernel_shape = 0

    def gui(s, frame):
        gui.Slider(frame, max=200, layer=s, name='contour_val').grid(column=1, row=1, sticky='W')

    def run(s, img):


        return img

    # def initiate(s, g):
    #     shape = g
    #     return shape
