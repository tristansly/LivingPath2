
import cv2
import numpy as np
import potrace
from PIL import ImageDraw, Image, ImageOps, ImageFilter

def cv_vecto() :
    img = cv2.imread('shape.png', cv2.IMREAD_UNCHANGED)

    #convert img to grey
    img = cv2.cvtColor(img,cv2.COLOR_GRAY2RGB)
    img_grey = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
    # img_grey = img
    #set a thresh
    thresh = 100
    #get threshold image
    ret,thresh_img = cv2.threshold(img_grey, thresh, 255, cv2.THRESH_BINARY)
    cv2.imwrite('cont.png',thresh_img)
    #find contours
    contours, hierarchy = cv2.findContours(thresh_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_KCOS)

    #create an empty image for contours
    img_contours = np.zeros(img.shape)
    print(contours)
    # draw the contours on the empty image
    cv2.drawContours(img_contours, contours, -1, (0,255,0), 3)
    contours = contours[1].reshape(-1,2)
    c = 0
    for (x, y) in contours:
        cv2.circle(img_contours, (x, y), 1, (255, 0, 0), 3)
        c += 1
    print('TOTAL', c)
    #save image
    cv2.imwrite('contours.png',img_contours)


import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD

root = TkinterDnD.Tk()  # notice - use this instead of tk.Tk()

lb = tk.Listbox(root)
lb.insert(1, "drag files to here")

# register the listbox as a drop target
lb.drop_target_register(DND_FILES)
lb.dnd_bind('<<Drop>>', lambda e: lb.insert(tk.END, e.data))

lb.pack()
root.mainloop()
