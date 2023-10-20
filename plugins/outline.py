from base_plugin import Plugin
import gui_utils as gui

import cairo
from io import BytesIO
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

        # # Define the control points for the Bezier curve
        # control_points = [(0, 0), (100, 100), (200, -100), (300, 0)]
        #
        # # Create a PNG surface
        # surface = cairo.ImageSurface(cairo.FORMAT_A8, 400, 300)
        # context = cairo.Context(surface)
        #
        # # Set line width and cap style
        # context.set_line_width(2)
        # context.set_line_cap(cairo.LINE_CAP_ROUND)
        # context.set_source_rgb(0, 0, 1)  # RGB values for blue
        #
        # context.move_to(*control_points[0])
        # context.curve_to(*control_points[1], *control_points[2], *control_points[3])
        #
        # # Stroke the path
        # context.stroke()
        #
        # # Convert to PIL image
        # buffer = BytesIO()
        # surface.write_to_png(buffer)
        # buffer.seek(0)
        # img = Image.open(buffer)

        return img

    # def initiate(s, g):
    #     shape = g
    #     return shape
