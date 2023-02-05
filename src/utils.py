import numpy as np
import cv2
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer

#get_img
def get_img(file_img):
    img = cv2.imdecode(
          np.frombuffer(file_img.getbuffer(), np.uint8),
          cv2.IMREAD_UNCHANGED
      )
      
    extension = '.jpg'

    if len(img.shape) == 3 and img.shape[2] == 4:
        img_mode = 'RGBA'
    else:
        img_mode = None

    if img_mode == 'RGBA':  # RGBA images should be saved in png format
        extension = '.png'

    return img, extension

#resize_img
def resize_img(img, size :int, interpolation=cv2.INTER_AREA):
  h, w = img.shape[:2]
  if h > size or w > size:
    if h == w: 
      return cv2.resize(src=img, dsize=(size, size), interpolation=interpolation)
    scale = h/size if h > w else w/size
    return cv2.resize(src=img, dsize=(int(w/scale), int(h/scale)), interpolation=interpolation)
  return img

#get_tile
def get_tile(img, max_size):
    #tile=0
    tile = max_size if img.shape[0] > max_size or img.shape[1] > max_size else 0
    tile_pad = int(tile/8)
    pre_pad = int(tile/8)

    return tile, tile_pad, pre_pad

#image_scaller
def image_scaller(model_path, img, extension, scale, tile, tile_pad, pre_pad, ):

    model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=2)
    netscale = 2
    
    # restorer
    upsampler = RealESRGANer(
        scale=netscale,
        model_path=model_path,
        dni_weight=None,
        model=model,
        tile=tile,
        tile_pad=tile_pad,
        pre_pad=pre_pad,
        half=False,
        device=None,
        gpu_id=None,
    )

    output, _ = upsampler.enhance(img, outscale=scale)

    file_output = cv2.imencode(extension, output)[1].tobytes()

    return file_output