#!/usr/bin/python3
import sys
from PIL import Image
from PIL import ImageChops
from PIL import ImageEnhance
from PIL import ImageDraw
from PIL import ImageFilter

class Caleidoscope(object):

    _im = None
    rotations = 4
    mask_size_factor = 0.7
    mask_blur = 100
    mask_strength = 0.3
    brightness = 1.3

    def __init__(self, image):
        image = image.convert("RGBA");
        
        # allow 1920 * 1200 pictures at maximum
        w, h = image.size
        if image.size[0] * image.size[1] > 2304000:
            ratio = min(1920./w, 1920./h)
            w = int(w * ratio)
            h = int(h * ratio)
            image.thumbnail((w, h), Image.ANTIALIAS)
        
        # get a quadratic image
        size = min(w, h)
        left = (w - size) / 2
        upper = (h - size) / 2
        right = (w - size) / 2 + size
        bottom = (h - size) / 2 + size
        self._im = image.crop((left, upper, right, bottom))
        
    def generate(self):
        caleidoscope_image = self._caleidoscope()
        enh = ImageEnhance.Brightness(caleidoscope_image)
        caleidoscope_image = enh.enhance(self.brightness)
        return self._apply_rad_mask(caleidoscope_image)
        
    def _caleidoscope(self):
        rotations = self.rotations
        assert rotations <= 20

        enh = ImageEnhance.Brightness(self._im)
        im_new = enh.enhance(self.brightness)
        for i in range(1,rotations):
            im_rot = self._im.rotate(360/rotations*i);
            enh = ImageEnhance.Brightness(im_rot)
            im_rot = enh.enhance(self.brightness)
            im_new = ImageChops.multiply(im_new, im_rot)
        return im_new
        
    def _apply_rad_mask(self, caleidoscope_image):
        msf = self.mask_size_factor
        mbl = self.mask_blur
        mstr = self.mask_strength
        
        # generate mask and fill white
        filter = Image.new(caleidoscope_image.mode, caleidoscope_image.size)
        draw = ImageDraw.Draw(filter)
        draw.rectangle([(0, 0), caleidoscope_image.size], 
            fill=(255, 255, 255, 255))
        
        # draw filled circle
        f_size = (1 - msf) / 2
        size = min(caleidoscope_image.size)
        low = size * f_size
        high = size - (size * f_size)
        grey_val = int((1 - mstr) * 255)
        grey_col = (grey_val, grey_val, grey_val, 255)
        draw.pieslice([(low, low), (high, high)], 0, 360, fill=grey_col)
        
        # blur, apply and return
        filter = filter.filter(ImageFilter.GaussianBlur(radius=mbl))
        enh = ImageEnhance.Contrast(caleidoscope_image)
        im_contrast = enh.enhance(0.7)
        return ImageChops.darker(im_contrast, caleidoscope_image)