import os
import logging

import numpy as np
import cv2
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer

import telebot
from telebot.async_telebot import AsyncTeleBot

SCALE = int(os.environ.get("SCALE", 2))
MAX_SIZE = int(os.environ.get("MAX_SIZE", 1080))

MODEL_NAME = os.environ.get("MODEL_NAME", "RealESRGAN_x2plus")

MODEL_PATH = r"weights"
MODEL_FILE = MODEL_PATH + r"/"+MODEL_NAME+".pth"

API_TOKEN = os.environ["API_TOKEN"]

logging.basicConfig(level=logging.INFO)

bot = telebot.TeleBot(API_TOKEN, threaded=False)

def repeat(message):
    bot.send_message(message.chat.id, message.text)

# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    logging.warning('get help or start')
    bot.reply_to(message, "hello upscale bot")


# Handle all other messages
@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_all(message):
    logging.warning('get text')
    bot.reply_to(message, "Пришел текст")
    repeat(message)

@bot.message_handler(content_types=['photo'])
def get_user_pics(message):
    logging.warning('get photo')
    bot.reply_to(message, "Открываю картинку")
    #logging.warning('close sesion')
    #await bot.close_session()

    file_info = bot.get_file(message.photo[-1].file_id)
    file_img = bot.download_file(file_info.file_path)

    img, extension = get_img(file_img=file_img)

    if img.shape[0] > MAX_SIZE or img.shape[1] > MAX_SIZE:
        bot.send_message(chat_id=message.chat.id, text=f"Картика размером {img.shape[0]}x{img.shape[1]}. Это больше максимального размера в {MAX_SIZE}, уменьшаю её...")
        #resize to max 512
        img = resize_img(img, MAX_SIZE)
        tile, tile_pad, pre_pad = get_tile(img=img, max_size=MAX_SIZE)
    else:
        tile, tile_pad, pre_pad = 0,0,0

    bot.send_message(chat_id=message.chat.id, text=f"Увеличиваю картинку на {SCALE}")

    file_output = image_scaller(img=img, extension=extension, scale=SCALE, tile=tile, tile_pad=tile_pad, pre_pad=pre_pad)

    bot.send_photo(chat_id=message.chat.id, photo=file_output)

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
    tile = 0
    #tile = MAX_SIZE if img.shape[0] > MAX_SIZE or img.shape[1] > MAX_SIZE else 0
    tile_pad = int(tile/8)
    pre_pad = int(tile/8)

    return tile, tile_pad, pre_pad


#image_scaller
def image_scaller(img, extension, scale, tile, tile_pad, pre_pad):

    model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=2)
    netscale = 2
    
    # restorer
    upsampler = RealESRGANer(
        scale=netscale,
        model_path=MODEL_FILE,
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