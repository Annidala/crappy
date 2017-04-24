# coding: utf-8
##  @addtogroup technical
# @{

##  @defgroup camerainit CameraInit
# @{

## @file _cameraInit.py
# @brief Gui to open and initialize a camera device.
#
# @author Victor Couty
# @version 0.2
# @date 04/04/2017
from __future__ import division

from PIL import ImageTk,Image
import cv2
from .cameraConfig import Camera_config

class VE_config(Camera_config):
  def __init__(self,camera,ve):
    self.select_box = (-1,-1,-1,-1)
    Camera_config.__init__(self,camera)
    self.ve = ve

  def create_window(self):
    Camera_config.create_window(self)
    self.img_label.bind('<1>', self.start_select)
    self.img_label.bind('<B1-Motion>', self.update_box)
    self.img_label.bind('<ButtonRelease-1>', self.stop_select)

  def start_select(self,event):
    self.box_origin = self.get_img_coord(event.y,event.x)

  def update_box(self,event):
    oy,ox = self.box_origin
    y,x = self.get_img_coord(event.y,event.x)
    self.select_box = (min(oy,y),min(ox,x),max(oy,y),max(ox,x))

  def stop_select(self,event):
    self.ve.detect_spots(self.img[self.select_box[0]:self.select_box[2],
                                  self.select_box[1]:self.select_box[3]],
                                  self.select_box[0],self.select_box[1])
    self.select_box = (-1,-1,-1,-1)

  def resize_img(self,sl):
    rimg = cv2.resize(self.img8[sl[1],sl[0]],tuple(reversed(self.img_shape)),
        interpolation=0)
    if self.select_box[0] > 0:
      lbox = [0]*4
      for i in range(4):
        n = self.select_box[i]-self.zoom_window[i%2]*self.img.shape[i%2]
        n /= (self.zoom_window[2+i%2]-self.zoom_window[i%2])
        lbox[i] = int(n/self.img.shape[i%2]
                      *self.img_shape[i%2])
      rimg[lbox[0],lbox[1]:lbox[3]] = 255
      rimg[lbox[2],lbox[1]:lbox[3]] = 255
      rimg[lbox[0]:lbox[2],lbox[1]] = 255
      rimg[lbox[0]:lbox[2],lbox[3]] = 255
    self.c_img = ImageTk.PhotoImage(Image.fromarray(rimg))
