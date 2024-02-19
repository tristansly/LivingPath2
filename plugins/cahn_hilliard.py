from base_plugin import Plugin
import gui_utils as gui
import utils

import numpy as np
from PIL import Image, ImageOps
# from numba import jit , njit
from scipy.fft import fft2, ifft2
from time import time


class Layer(Plugin):
    """
     Cahn-Hilliard equation using an implicit pseudospectral algorithm
     https://github.com/elvissoares/PyCahnHilliard/blob/master/cahnhilliard.py
    """

    def __init__(s):
        super(Layer, s).__init__()
        # noiseImg = Image.open( utils.path('files/noise.png') ).convert('L')
        # s.noise = np.array(noiseImg.getdata(), dtype=np.float32)
        # s.noise = np.reshape(s.noise/255, ( -1, noiseImg.width))

    def gui(s, frame):
        gui.Slider(frame, max=0.5, min=0.01, ini= 0.1,format='%0.2f', layer=s, name='size').grid(column=1, row=0, sticky='W')
        gui.Slider(frame, min=30, max=230, ini=127, layer=s, name='threshold').grid(column=0, row=1, sticky='W')

        gui.Slider(frame,layer=s,min=0.5, max=2, ini=1.0, format='%0.3f',name='depth').grid(column=0,row=2,sticky='W')
        gui.Slider(frame,layer=s,min=0., max=0.5, ini=.1, format='%0.3f',name='noise').grid(column=0,row=3,sticky='W')
        gui.Slider(frame, layer=s, min=1, max=1000, ini=50, name='growing time').grid(column=0, row=6, sticky='W')
        # gui.Checkbutton(frame, layer=s, name='invert', ini=False).grid(column=0, row=7, sticky='W')

    def run(s, img):
        originSize = img.size
        img = img.resize( (int(img.width*s.size), int(img.height*s.size)), Image.NEAREST)

        w = img.height
        h = img.width
        t = time()

        Nsteps =s.growing_time
        dt = 0.1
        N = 256
        c_hat = np.empty((w,h), dtype=np.complex64)
        dfdc_hat = np.empty((w,h), dtype=np.complex64)
        c = np.empty((Nsteps,w,h), dtype=np.float32)

        dx = 1.0
        noise = s.noise
        c0 = 0.5
        rng = np.random.default_rng(12345)
        arr = np.array(img.getdata())
        c[0] = np.reshape( (s.depth-arr/255)/2, ( -1, img.width))
        c[0] = c[0] + noise*rng.standard_normal(c[0].shape)

        W = 2.0
        M = 1.0 # mobility
        kappa = 0.5 #gradient coeficient

        kx = np.fft.fftfreq(w, d=dx)*2*np.pi
        ky =  np.fft.fftfreq(h, d=dx)*2*np.pi
        K = np.array(np.meshgrid(kx , ky ,indexing ='ij'), dtype=np.float32)
        K2 = np.sum(K*K,axis=0, dtype=np.float32)

        # The anti-aliasing factor
        kmax_dealias = kx.max()*2.0/3.0 # The Nyquist mode
        dealias = np.array((np.abs(K[0]) < kmax_dealias )*(np.abs(K[1]) < kmax_dealias ),dtype =bool)

        def finterf(c_hat): return kappa*ifft2(K2*c_hat**2).real # The interfacial free energy density f(c) = Wc^2(1-c)^2 """
        def fbulk(c): return W*c**2*(1-c)*c**2                   # The bulk free energy density f(c) = Wc^2(1-c)^2 """
        def dfdc(c): return 2*W*(c*(1-c)**2-(1-c)*c**2)          # The derivative of bulk free energy density f(c) = Wc^2(1-c)^2 """

        c_hat[:] = fft2(c[0])
        for i in range(0,Nsteps):
            dfdc_hat[:] = fft2(dfdc(c[i-1])) # the FT of the derivative
            dfdc_hat *= dealias # dealising
            c_hat[:] = (c_hat-dt*K2*M*dfdc_hat)/(1+dt*M*kappa*K2**2) # updating in time
            c[i] = ifft2(c_hat).real # inverse fourier transform

        print("R&D - Time Elapsed : " + str(time() - t) )

        img = np.clip( c[-1] * 255, 0, 255 )
        img = Image.fromarray(np.uint8(img))
        img = ImageOps.invert(img)
        img = img.resize(originSize, 1)
        img = img.point( lambda p: 255 if p > s.threshold else 0 )
        return img
