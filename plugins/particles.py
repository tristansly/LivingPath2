from base_plugin import Plugin
import gui_utils as gui
import utils

import random
import sys
import utils
import pymunk
import pymunk.util
from pymunk import Vec2d

from PIL import Image, ImageDraw


class Layer(Plugin):
    """Very simple example that does not depend on any third party library such
    as pygame or pyglet like the other examples.
    """
    def __init__(s):
        super(Layer, s).__init__()
        s.space = pymunk.Space()

    def gui(s, frame):
        gui.Slider(frame, max=1000, min=1, ini= 20, layer=s, name='quantity').grid(column=0, row=0, sticky='W')
        gui.Slider(frame, max=400, min=1, ini= 50, layer=s, name='size').grid(column=0, row=1, sticky='W')
        gui.Slider(frame, layer=s, min=0, max=1000, ini=100, name='time').grid(column=0, row=2, sticky='W')

        # gui.Slider(frame,layer=s,min=0.02, max=0.08, ini=0.055, format='%0.3f',name='k black').grid(column=0,row=5,sticky='W')
        # gui.Checkbutton(frame, layer=s, name='invert', ini=False).grid(column=0, row=7, sticky='W')

    def run(s, img):
        draw = ImageDraw.Draw(img)

        # s.space.gravity = (0.0, 10.0)

        ## Balls
        balls = []

        for x in range(s.quantity):
            mass = 1
            radius = 50
            inertia = pymunk.moment_for_circle(mass, 0, radius, (0, 0))
            body = pymunk.Body(mass, inertia)
            x = 100 # random.randint(115, 350)
            body.position = x,400 
            shape = pymunk.Circle(body, radius, Vec2d(0, 0))
            s.space.add(body, shape)
            balls.append(shape)

        balls_to_remove = []

        for ball in balls:
            if ball.body.position.y < 0:
                balls_to_remove.append(ball)
        for ball in balls_to_remove:
            s.space.remove(ball, ball.body)
            balls.remove(ball)


        ### Update physics
        for x in range(2):
            s.space.step(s.time/100.0)

        for ball in balls:
                v = ball.body.position
                utils.ellipse(s.size, v.x, v.y, 0, draw)
        # del draw
        return img
