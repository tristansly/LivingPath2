import gui_utils as gui
import utils
from base_plugin import Plugin
import numpy as np
from PIL import Image
import PIL
import seam_carving
import time
import cv2
interpo = [cv2.INTER_AREA, cv2.INTER_BITS, cv2.INTER_BITS2, cv2.INTER_CUBIC, cv2.INTER_LANCZOS4, cv2.INTER_LINEAR, cv2.INTER_LINEAR_EXACT, cv2.INTER_NEAREST]
kernel = np.array([ [0, -1, 0], [-1, 5, -1], [0, -1, 0] ])


class Layer(Plugin):
    """Apply a blur then a threshold."""

    def gui(s, frame):

        gui.Slider(frame, max=100, ini=70, layer=s, name='stretch width').grid(column=0, row=0, sticky='ew')
        gui.Slider(frame, max=100, ini=50, layer=s, name='stretch height').grid(column=0, row=1, sticky='ew')
        gui.Slider(frame, min=1, max=100, ini=30, layer=s, name='resolution', slow=True).grid(column=0, row=2, sticky='ew')

        gui.Checkbutton(frame, layer=s, name='preserve_shape', ini=False).grid(column=0, row=3, sticky='W')
        gui.Checkbutton(frame, layer=s, name='reverse_gravity', ini=False).grid(column=0, row=4, sticky='W')

        gui.Slider(frame, min=1, max=5, ini=1.8, layer=s, format='%0.2f', name='zoom').grid(column=0, row=5, sticky='ew')
        gui.Slider(frame, min=-1, max=1, ini=-0.5, layer=s, format='%0.2f', name='correct_ratio').grid(column=0, row=6, sticky='ew')


    def run(s, img):
        if not s.reverse_gravity : img = img.transpose(Image.Transpose.ROTATE_180)

        w,h = img.size[0], img.size[1]
        img = img.resize((int(utils.mapping(s.resolution,1,100,1,w/5)),
                          int(utils.mapping(s.resolution,1,100,1,h/5)) ))
        imgA = np.array(img.convert('L'))


        resize = (int(utils.mapping(s.stretch_width,0,100,img.width,2)),
                  int(utils.mapping(s.stretch_height,0,100,img.height,2)))

        imgA = seam_carving.resize( imgA, size=resize,
            energy_mode="forward", order="width-first"
        )

        resize = (int(1.5*resize[0]+s.correct_ratio*resize[0]),
                  int(1.5*resize[1]-s.correct_ratio*resize[1]))
        imgA = cv2.resize(imgA,resize, interpolation=cv2.INTER_CUBIC)

        # for i in range(s.sharpen): imgA = cv2.filter2D(imgA, -1, kernel)


        imgA = seam_carving.resize( imgA, size = img.size,
            energy_mode="forward" if s.preserve_shape else 'backward', order="width-first"
        )


        img = Image.fromarray(imgA)
        zoom = s.zoom #max( s.correct_width, s.correct_height )
        img2 = Image.new('L',(int(img.width*zoom), int(img.height*zoom)),255)
        img2.paste(img, ((img2.width-img.width)//2, (img2.height-img.height)//2 ) )

        img = img2.resize((w,h))
        img = img.point( lambda p: 255 if p > 127 else 0 ) # threshold 128
        if not s.reverse_gravity : img = img.transpose(Image.Transpose.ROTATE_180)
        return img
