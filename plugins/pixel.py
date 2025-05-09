import gui_utils as gui
from base_plugin import Plugin

from PIL import Image

class Layer(Plugin):
    """Pixelize letter."""

    def gui(s, frame):
        gui.Slider(frame, max=300, min=1, ini= 20, layer=s, name='resolution').grid(column=1, row=1, sticky='W')
        gui.Slider(frame, max=100,ini= 0, layer=s, name='horizontal_position').grid(column=1, row=2, sticky='W')
        gui.Slider(frame, max=100,ini= 0, layer=s, name='vertical_position').grid(column=1, row=3, sticky='W')

        # recoder l'algo pour ces options ?
        # gui.Slider(frame, max=50, min=-50, ini= 0, layer=s, name='size').grid(column=1, row=1, sticky='W')
        # gui.Checkbutton(frame, layer=s, name='ellipse', ini=True).grid(column=0, row=6, sticky='W')

    def run(s, img):
        width = img.size[0]
        height = img.size[1]
        px = s.resolution

        top = int((s.vertical_position /100) * px)
        left = int((s.horizontal_position /100) * px)

        img = add_margin(img, left, top, px-left, px-top, 'white' )

        img = img.resize( size=((width) // px, (height) // px), resample=0)
        img = img.point( lambda p: 255 if p > 127 else 0 )
        img = img.resize((width+px,height+px), Image.NEAREST)

        img = img.crop((left, top, width+left, height+top))


        return img

def add_margin(pil_img, left, top, right, bottom,  color):
    width, height = pil_img.size
    new_width = width + right + left
    new_height = height + top + bottom
    result = Image.new(pil_img.mode, (new_width, new_height), color)
    result.paste(pil_img, (left, top))
    return result
