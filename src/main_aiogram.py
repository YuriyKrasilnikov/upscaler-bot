import asyncio

from aiogram import Bot, Dispatcher, executor, types

from utils import *

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

async def repeat(message):
    bot.send_message(message.chat.id, message.text)

# Handle '/start' and '/help'
@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message):
    logging.warning('get help or start')
    await message.reply("hello upscale aiogram bot")

# Handle all other messages
@dp.message_handler()
async def echo_all(message):
    logging.warning('get text')
    await message.reply("Пришел текст")
    await repeat(message)

@dp.message_handler(content_types=['photo', "document"])
async def get_user_pics(message):
    logging.warning('get photo')
    await message.reply("Открываю картинку")
    #logging.warning('close sesion')
    #await bot.close_session()
    if message.photo:
      file_info = await bot.get_file(message.photo[-1].file_id)
      file_img = await bot.download_file(file_info.file_path)
    else:
      file_info = await bot.get_file(message.document.file_id)
      file_img = await bot.download_file(file_info.file_path)

    img, extension = get_img(file_img=file_img)

    tile, tile_pad, pre_pad = get_tile(img=img, max_size=512)

    await bot.send_message(chat_id=message.chat.id, text=f"Увеличиваю картинку на {SCALE}")

    file_output = image_scaller(img=img, extension=extension, scale=SCALE, tile=tile, tile_pad=tile_pad, pre_pad=pre_pad)

    await bot.send_document(
      chat_id=message.chat.id,
      document=file_output,
      thumb=cv2.imencode('.jpeg', resize_img(img, 320))[1].tobytes()
      )

def get_tile(img, max_size):
    #tile=0
    tile = max_size if img.shape[0] > max_size or img.shape[1] > max_size else 0
    tile_pad = int(tile/8)
    pre_pad = int(tile/8)

    return tile, tile_pad, pre_pad

executor.start_polling(dp, skip_updates=True)