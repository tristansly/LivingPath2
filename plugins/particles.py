from base_plugin import Plugin
import gui_utils as gui
import utils

import random
import sys
import utils
import pymunk
import pymunk.util
import pymunk.autogeometry
from pymunk import Vec2d
import math
from PIL import Image, ImageDraw


class Layer(Plugin):
    """Very simple example that does not depend on any third party library such
    as pygame or pyglet like the other examples.
    """
    def __init__(s):
        super(Layer, s).__init__()

    def gui(s, frame):
        gui.Slider(frame, max=100, min=1, ini= 20, layer=s, name='quantity').grid(column=0, row=0, sticky='W')
        gui.Slider(frame, max=400, min=1, ini= 50, layer=s, name='size')     .grid(column=0, row=1, sticky='W')
        gui.Slider(frame, max=400, min=1, ini= 50, layer=s, name='repultion').grid(column=0, row=2, sticky='W')
        gui.Slider(frame, layer=s, min=0, max=1000, ini=100, name='time')    .grid(column=0, row=3, sticky='W')

        # gui.Slider(frame,layer=s,min=0.02, max=0.08, ini=0.055, format='%0.3f',name='k black').grid(column=0,row=5,sticky='W')
        gui.Slider(frame, max=100, min=1, ini= 1, layer=s, name='outline_width').grid(column=0, row=5, sticky='W')
        gui.Checkbutton(frame, layer=s, name='over', ini=True).grid(column=0, row=6, sticky='W')
        gui.Checkbutton(frame, layer=s, name='outline', ini=False).grid(column=0, row=7, sticky='W')

        gui.Slider(frame, max=200, min=1, ini= 200, layer=s, name='x').grid(column=0, row=8, sticky='W')
        gui.Slider(frame, max=200, min=1, ini= 50, layer=s, name='y').grid(column=0, row=9, sticky='W')
        gui.Slider(frame, max=200, min=1, ini= 60, layer=s, name='z').grid(column=0, row=10, sticky='W')
        gui.Slider(frame, max=2, min=0, ini= 0, format='%0.2f', layer=s, name='a').grid(column=0, row=11, sticky='W')
        gui.Slider(frame, max=2, min=0, ini= 0.01, format='%0.2f', layer=s, name='b').grid(column=0, row=12, sticky='W')
        gui.Slider(frame, max=2, min=0, ini= 0.01, format='%0.2f', layer=s, name='c').grid(column=0, row=13, sticky='W')
        gui.Slider(frame, max=2, min=0, ini= 0, format='%0.2f', layer=s, name='d').grid(column=0, row=14, sticky='W')
        gui.Slider(frame, max=2, min=0, ini= 0, format='%0.2f', layer=s, name='e').grid(column=0, row=15, sticky='W')


    def run(s, img):
        img_draw = Image.new(img.mode, img.size, 255)
        s.space = pymunk.Space()
        draw = ImageDraw.Draw(img_draw)

        s.space.gravity = (0.0, s.a)
        s.space.collision_bias = s.b
        s.space.collision_slop = s.c*10

        ## Balls
        balls = []

        w, h = img.size[0], img.size[1]
        q =  120-s.quantity
        for x in range(w//q):
            for y in range(h//q):
                mass = 1
                radius = s.repultion
                inertia = pymunk.moment_for_circle(mass, 0, radius, (0, 0))
                body = pymunk.Body(mass, inertia)
                # x = 100 # random.randint(115, 350)
                body.position = x*q, y*q
                shape = pymunk.Circle(body, radius, Vec2d(0, 0))
                # shape.elasticity = s.b
                # shape.friction = s.c
                s.space.add(body, shape)
                balls.append(shape)

        s.generate_geometry(img, s.space, draw)


        ### Update physics
        for x in range(s.time):
            s.space.step(1)

            ### remove
            balls_to_remove = []
            for ball in balls:
                if not utils.is_over(ball.body.position,(0,0,w-1,h-1)) or s.over and img.getpixel(ball.body.position) > 127 :
                    balls_to_remove.append(ball)
            for ball in balls_to_remove:
                s.space.remove(ball, ball.body)
                balls.remove(ball)

        for ball in balls:
                v = ball.body.position
                utils.ellipse(s.size, v.x, v.y, 0, draw)

        del draw
        del s.space
        return img_draw

    def generate_geometry(s, img, space, draw):
        def sample_func(point):
            try:
                p = int(point[0]), int(point[1])
                color = img.getpixel(p)
                return color
            except Exception as e:
                print(e)
                return 0

        line_set = pymunk.autogeometry.march_soft(
            pymunk.BB(0, 0, img.size[0]-1, img.size[1]-1), s.x, s.x, s.y, sample_func
        )


        for polyline in line_set:
            line = pymunk.autogeometry.simplify_curves(polyline, s.z/10)

            for i in range(len(line) - 1):
                p1 = line[i]
                p2 = line[i+1]
                shape = pymunk.Segment(space.static_body, p1, p2, s.outline_width)
                shape.friction = s.d
                shape.elasticity = s.e
                space.add(shape)
            if s.outline : draw.line( line, fill=100, width=s.outline_width, joint="curve" )
            if s.outline : utils.ellipse(s.outline_width, line[0][0], line[0][1], 100, draw) # close draw.line
