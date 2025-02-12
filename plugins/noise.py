import gui_utils as gui
from base_plugin import Plugin
from PIL import ImageFilter, Image
import cv2
import numpy as np
import perlin_numpy as perlin
from functools import partial
import math, utils

class Layer(Plugin):
    """Apply a blur then a threshold."""

    def gui(s, frame):


        gui.Slider(frame, max=200, ini=30, layer=s, name='affects_border').pack(anchor='w')
        gui.Slider(frame, max=20, min=1, ini=5, layer=s, name='shape_unity').pack(anchor='w')
        gui.Slider(frame, max=100, min=1, ini=3, layer=s, name='noise_size').pack(anchor='w')
        gui.Slider(frame, max=254, ini=200, layer=s, name='threshold').pack(anchor='w')



    def run(s, img):
        img_size = img.size

        img = img.filter( ImageFilter.GaussianBlur(radius = (s.affects_border,s.affects_border) ) )

        img = np.array(img)

        np.random.seed(5)
        reduced = (img_size[1]//s.noise_size, img_size[0]//s.noise_size)
        noise = np.random.normal(5, 25, reduced).astype(np.uint8)

        noise = cv2.resize(noise, img_size, interpolation=cv2.INTER_LANCZOS4)

        # noise is too slow
        # noise = perlin.generate_fractal_noise_2d((2048,2048), (8, 8), octaves=1, persistence=0.5)
        # noise = noise[0:img_size[1], 0:img_size[0]]
        # noise = noise.astype(np.uint8)

        img = cv2.add(img, noise)
        img = Image.fromarray(img, mode='L')
        img = img.filter( ImageFilter.GaussianBlur(radius = (s.shape_unity,s.shape_unity) ) )
        img = img.point( lambda p: 255 if p > s.threshold else 0 ) # threshold 128

        return img
