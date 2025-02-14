import gui_utils as gui
from base_plugin import Plugin
import numpy as np
from PIL import Image
import cv2


class Layer(Plugin):
    """Apply a blur then a threshold."""

    def gui(s, frame):

        gui.LockSliders( frame, True,
            dict(max=200, min=1, ini=30, layer=s, name='resolution_width'),
            dict(max=200, min=1, ini=30, layer=s, name='resolution_height')
        ).pack(anchor='nw')

        gui.Slider(frame, min=0, max=4, ini=1, layer=s, name='interpolation').pack(anchor='nw')
        gui.Slider(frame, min=0, max=10, ini=3, layer=s, name='sharpen').pack(anchor='nw', pady=(20,0))
        gui.Slider(frame, min=0, max=255, ini=127, layer=s, name='threshold').pack(anchor='nw')

    def run(s, img):
        size = img.size
        interpo = [cv2.INTER_AREA, cv2.INTER_BITS, cv2.INTER_BITS2, cv2.INTER_CUBIC, cv2.INTER_LANCZOS4 ]

        img = np.array(img)

        img = cv2.resize(img, (1+int(size[0]*s.resolution_width/1000),1+int(size[1]*s.resolution_height/1000)), interpolation = cv2.INTER_AREA)


        kernel = np.array([ [0, -1, 0], [-1, 5, -1], [0, -1, 0]      ])
        for i in range(s.sharpen):
            img = cv2.filter2D(img, -1, kernel)



        img = cv2.resize(img, size, interpolation = interpo[s.interpolation])
        #img = np.where(img > 127, 255, 0) # fast threshold

        img = Image.fromarray(img, mode="L")
        img = img.point( lambda p: 255 if p > s.threshold else 0 ) # threshold 128

        # img = img.resize((size))
        return img
