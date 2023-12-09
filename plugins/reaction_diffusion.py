from base_plugin import Plugin
import gui_utils as gui
import utils

import numpy as np
from PIL import Image, ImageOps
from numba import jit , njit
from time import time

@njit
def draw(U, V, nextImgA, nextImgB, fk, w,h ):

    for x in range (w):
        for y in range (h):
            u = U[x,y]
            v = V[x,y]
            uvv = u*v*v
            laplace_a = (U[x-1,y-1]+U[x+1,y+1]+U[x-1,y+1]+U[x+1,y-1])*0.05+(U[x,y-1]+U[x,y+1]+U[x-1,y]+U[x+1,y])*0.2-u
            laplace_b =((V[x-1,y-1]+V[x+1,y+1]+V[x-1,y+1]+V[x+1,y-1])*0.05+(V[x,y-1]+V[x,y+1]+V[x-1,y]+V[x+1,y])*0.2-v)*0.5
            nextImgA[x,y] = min(1,max(0, u + laplace_a - uvv + (fk[x,y,0]*(1 - u))         )) # *1.38
            nextImgB[x,y] = min(1,max(0, v + laplace_b + uvv - ((fk[x,y,1] + fk[x,y,0])*v) )) # *0.43
    return nextImgA, nextImgB, U, V


class Layer(Plugin):
    """Reaction diffusion algorithm, GreyScott implementation"""

    def __init__(s):
        super(Layer, s).__init__()
        # noiseImg = Image.open( utils.path('files/noise.png') ).convert('L')
        # s.noise = np.array(noiseImg.getdata(), dtype=np.float32)
        # s.noise = np.reshape(s.noise/255, ( -1, noiseImg.width))

    def gui(s, frame):
        gui.Slider(frame, max=0.5, min=0.01, ini= 0.1,format='%0.2f', layer=s, name='size').grid(column=1, row=0, sticky='W')
        gui.Slider(frame, max=200, ini=90, layer=s, name='threshold').grid(column=0, row=1, sticky='W')

        gui.Slider(frame,layer=s,min=0.02, max=0.08, ini=0.052, format='%0.3f',name='f white').grid(column=0,row=2,sticky='W')
        gui.Slider(frame,layer=s,min=0.02, max=0.08, ini=0.035, format='%0.3f',name='f black').grid(column=0,row=3,sticky='W')
        gui.Slider(frame,layer=s,min=0.02, max=0.08, ini=0.062, format='%0.3f',name='k white').grid(column=0,row=4,sticky='W')
        gui.Slider(frame,layer=s,min=0.02, max=0.08, ini=0.055, format='%0.3f',name='k black').grid(column=0,row=5,sticky='W')
        gui.Slider(frame, layer=s, min=0, max=3000, ini=1000, name='growing time').grid(column=0, row=6, sticky='W')
        gui.Checkbutton(frame, layer=s, name='invert', ini=False).grid(column=0, row=7, sticky='W')

    def run(s, img):
        originSize = img.size
        img = img.resize( (int(img.width*s.size), int(img.height*s.size)), Image.NEAREST)

        m = 0
        if img.width  < 200 : m = 100-img.width//2
        if img.height < 200 : m = 100-img.height//2
        if m > 0 : img = ImageOps.expand(img, border=m, fill=(255))
        w = img.height
        h = img.width
        arr = np.array(img.getdata())
        img = np.reshape(arr/255, ( -1, img.width))

        np.random.seed(42)
        U = np.random.normal(0.8, 0.2, size=(w, h))
        V = np.random.normal(0.2, 0.2, size=(w, h))
        nextImgA = np.ones ( (w, h) )
        nextImgB = np.zeros( (w, h) )

        t = time()
        fkbw = np.array([s.f_black,s.f_white,s.k_black,s.k_white])

        fk = np.ones( (w,h,2) )
        for x in range (w):
            for y in range (h):
                fk[x,y,0] = utils.mapping(img[x,y], fkbw[0], fkbw[1] )
                fk[x,y,1] = utils.mapping(img[x,y], fkbw[2], fkbw[3] )

        for i in range (s.growing_time):
            U, V, nextImgA, nextImgB = draw( U, V, nextImgA, nextImgB, fk ,w,h )
            # U = np.clip(U, 0.0, 1.0)
            # V = np.clip(V, 0.0, 1.0)
        print("R&D - Time Elapsed : " + str(time() - t) )

        img = np.clip((U - V) * 255, 0, 255)
        img = Image.fromarray(np.uint8(img))
        if m > 0 : img = img.crop((m, m, img.width-m, img.height-m))
        if s.invert : img = ImageOps.invert(img)
        img = img.resize(originSize, 1)
        img = img.point( lambda p: 255 if p > s.threshold else 0 )
        return img
