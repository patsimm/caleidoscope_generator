#!/usr/bin/python3
import sys
from PIL import Image
from PIL import ImageChops
from PIL import ImageEnhance
from PIL import ImageDraw
from PIL import ImageFilter

class Caleidoscope(object):

    _im = None

    def __init__(self, image):
        image = image.convert("RGBA");
        size = min(image.size)
        
        # allow 1920 * 1200 pictures at maximum
        if image.size[0] * image.size[1] > 2304000:
            raise ImageTooBigException("Your image is too big")
        
        # get a quadratic image
        old_width, old_height = image.size
        left = (old_width - size) / 2
        upper = (old_height - size) / 2
        right = (old_width - size) / 2 + size
        bottom = (old_height - size) / 2 + size
        self._im = image.crop((left, upper, right, bottom))
        
    def generate(self, rotations=4, mask_size_factor=0.7, mask_blur=100, 
            mask_strength=0.3):
        caleidoscope_image = self._caleidoscope(rotations=5)
        enh = ImageEnhance.Brightness(caleidoscope_image)
        caleidoscope_image = enh.enhance(5)
        return self._apply_rad_mask(caleidoscope_image,
            mask_size_factor, mask_blur, mask_strength)
        
    def _caleidoscope(self, rotations=4):
        enh = ImageEnhance.Brightness(self._im)
        im_new = enh.enhance(2)
        for i in range(1,rotations):
            im_rot = self._im.rotate(360/rotations*i);
            enh = ImageEnhance.Brightness(im_rot)
            im_rot = enh.enhance(2)
            im_new = ImageChops.multiply(im_new, im_rot)
        return im_new
        
    def _apply_rad_mask(self, caleidoscope_image, mask_size_factor, mask_blur, 
            mask_strength):
        """Generate and apply the 
        """
        # generate mask and fill white
        filter = Image.new(caleidoscope_image.mode, caleidoscope_image.size)
        draw = ImageDraw.Draw(filter)
        draw.rectangle([(0, 0), caleidoscope_image.size], 
            fill=(255, 255, 255, 255))
        
        # draw filled circle
        f_size = (1 - mask_size_factor) / 2
        size = min(caleidoscope_image.size)
        low = size * f_size
        high = size - (size * f_size)
        grey_val = int((1 - mask_strength) * 255)
        grey_col = (grey_val, grey_val, grey_val, 255)
        draw.pieslice([(low, low), (high, high)], 0, 360, fill=grey_col)
        
        # blur, apply and return
        filter = filter.filter(ImageFilter.GaussianBlur(radius=mask_blur))
        enh = ImageEnhance.Contrast(caleidoscope_image)
        im_contrast = enh.enhance(0.7)
        return ImageChops.darker(im_contrast, caleidoscope_image)

class ImageTooBigException(Exception):
    pass