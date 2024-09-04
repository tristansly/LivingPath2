import gui_utils as gui
from base_plugin import Plugin
import seam_carving
import numpy as np
from PIL import Image
from lib.edi import EDI_predict
import cv2


class Layer(Plugin):
    """Apply a blur then a threshold."""

    def gui(s, frame):
        gui.Slider(frame, min=0.0001, max=0.2, ini=0.03, format='%0.3f', layer=s, name='width').grid(column=0, row=1, sticky='ew')
        gui.Slider(frame, min=0.0001, max=0.2, ini=0.03, format='%0.3f', layer=s, name='height').grid(column=0, row=2, sticky='ew')

        gui.Slider(frame, min=0, max=7, ini=0, layer=s, name='interpolation1').grid(column=0, row=3, sticky='ew')
        gui.Slider(frame, min=0, max=7, ini=1, layer=s, name='interpolation2').grid(column=0, row=4, sticky='ew')
        gui.Slider(frame, min=0, max=20, ini=3, layer=s, name='sharpen').grid(column=0, row=5, sticky='ew')


    def run(s, img):
        size = img.size
        interpo = [cv2.INTER_AREA, cv2.INTER_BITS, cv2.INTER_BITS2, cv2.INTER_CUBIC, cv2.INTER_LANCZOS4, cv2.INTER_LINEAR, cv2.INTER_LINEAR_EXACT, cv2.INTER_NEAREST]


        img = np.array(img)
        # img = EDI_predict(img, s.sampling_size, s.scale) # pas ouf ...

        img = cv2.resize(img, (1+int(size[0]*s.width),1+int(size[1]*s.height)), interpolation = interpo[s.interpolation1])


        kernel = np.array([ [0, -1, 0], [-1, 5, -1], [0, -1, 0]      ])
        for i in range(s.sharpen):
            img = cv2.filter2D(img, -1, kernel)



        img = cv2.resize(img, size, interpolation = interpo[s.interpolation2])
        img = np.where(img > 127, 255, 0) # fast threshold

        img = Image.fromarray(img)
        img = img.convert('L')

        # img = img.resize((size))
        return img
