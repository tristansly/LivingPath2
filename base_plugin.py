import gui_utils as gui

import cairo
from io import BytesIO
from PIL import Image

class plugin():
    """Base plugin."""

    def __init__(s):
        print('base')

        # base_plugin is useless for now
        # and only implemented with outline plugin
