import os
import asyncio

from aiohttp import web, ClientSession

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

bot = AsyncTeleBot(API_TOKEN, parse_mode='html', offset=10)
app = web.Application()

loop = asyncio.get_event_loop()

# Process webhook calls
async def handle(request):
    print('start')
    session = ClientSession()
    if True or request.match_info.get('token') == bot.token:
        print('token done')
        request_body_dict = await request.json()
        update = telebot.types.Update.de_json(request_body_dict)
        print(update)
        await bot.process_new_updates([update])
        return web.Response(status=200)
    else:
        print('Error 403')
        return web.Response(status=403)


app.router.add_post('/', handle)


async def repeat(message):
    await bot.send_message(message.chat.id, message.text)

# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
    print('get help or start')
    await bot.reply_to(message, "hello upscale bot")


# Handle all other messages
@bot.message_handler(func=lambda message: True, content_types=['text'])
async def echo_all(message):
    print('get text')
    await bot.reply_to(message, "Пришел текст")
    await repeat(message)

@bot.message_handler(content_types=['photo'])
async def get_user_pics(message):
    print('get photo')
    await bot.reply_to(message, "Открываю картинку")
    #print('close sesion')
    #await bot.close_session()

    file_info = await bot.get_file(message.photo[-1].file_id)
    file_img = await bot.download_file(file_info.file_path)

    img, extension = get_img(file_img=file_img)

    if img.shape[0] > MAX_SIZE or img.shape[1] > MAX_SIZE:
      await bot.send_message(chat_id=message.chat.id, text=f"Картика размером {img.shape[0]}x{img.shape[1]}. Это больше максимального размера в {MAX_SIZE}, уменьшаю её...")
      #resize to max 512
      img = resize_img(img, MAX_SIZE)

    tile, tile_pad, pre_pad = get_tile(img=img, max_size=MAX_SIZE)

    await bot.send_message(chat_id=message.chat.id, text=f"Увеличиваю картинку на {SCALE}")

    file_output = image_scaller(img=img, extension=extension, scale=SCALE, tile=tile, tile_pad=tile_pad, pre_pad=pre_pad)

    await bot.send_photo(chat_id=message.chat.id, photo=file_output)


#get_img
def get_img(file_img):
    img = cv2.imdecode(
          np.frombuffer(file_img, np.uint8),
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

async def shutdown(app):
    print("on_shutdown")

app.on_shutdown.append(shutdown)

web.run_app(app)
