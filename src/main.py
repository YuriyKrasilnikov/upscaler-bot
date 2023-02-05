#!/usr/bin/python3
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.utils.callback_data import CallbackData

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from const import API_TOKEN, MODEL_FILE, logging
from utils import *

class upscalerBot:
    class Form(StatesGroup):
        msg=State()

    def __init__(self, token, model_file, upscaled_sizes=(2,7)):
        self.model_file = model_file

        self.bot = Bot(token=token)
        self.dp = Dispatcher(self.bot, storage=MemoryStorage())

        self.cldata_get_size = CallbackData('get_size','value')
        self.markup_get_size = self.init_markup_get_size(sizes=upscaled_sizes, callback_data=self.cldata_get_size)
        self.setup_handlers(self.dp)
        self.task = {}

    def init_markup_get_size(self, sizes, callback_data, row_width=3):
        keyboard_markup = types.InlineKeyboardMarkup(row_width=row_width)
        btns = (
          types.InlineKeyboardButton(
            text=f"x{num}",
            callback_data=callback_data.new(value=num)
          ) for num in range(*sizes)
        )
        keyboard_markup.row(*btns)
        return keyboard_markup

    def setup_handlers(self, dispatcher: Dispatcher):
        # This example has only one messages handler
        dispatcher.register_message_handler(callback=self.send_welcome, commands=['start', 'help'])
        dispatcher.register_message_handler(callback=self.send_welcome)
        dispatcher.register_message_handler(callback=self.set_upscaler, content_types=['photo', "document"])
        dispatcher.register_callback_query_handler(self.get_size, self.cldata_get_size .filter())

    async def send_welcome(self, message, state: FSMContext):
        logging.warning(f'get message from {message.from_user.first_name}')
        await message.reply(f"Этот бот увеличивает картинки\nПросто пришлите картинку которую хотите увеличить")
        return True
    
    async def get_size(self, query: types.CallbackQuery, callback_data: dict, state: FSMContext):
        size = int(callback_data.get('value'))
        logging.warning(f'get_size {size}')
        await query.message.delete_reply_markup()
        msg = (await state.get_data())["msg"]
        await self.upscale_img(message=msg, size=size)
        await state.finish()
        return True

    async def set_upscaler(self, message, state: FSMContext):
        logging.warning(f'get photo {message.from_user.first_name}')
        await state.update_data(msg=message)
        await message.reply("Выберете на сколько увеличить картинку", reply_markup=self.markup_get_size)
        return True
          
    async def upscale_img(self, message, size):
        if message.photo:
          file_info = await self.bot.get_file(message.photo[-1].file_id)
          file_img = await self.bot.download_file(file_info.file_path)
        else:
          file_info = await self.bot.get_file(message.document.file_id)
          file_img = await self.bot.download_file(file_info.file_path)

        img, extension = get_img(file_img=file_img)

        tile, tile_pad, pre_pad = get_tile(img=img, max_size=512)

        await self.bot.send_message(chat_id=message.chat.id, text=f"Увеличиваю картинку размером {img.shape[0]} x {img.shape[1]} на {size}")

        file_output = image_scaller(model_path=self.model_file, img=img, extension=extension, scale=size, tile=tile, tile_pad=tile_pad, pre_pad=pre_pad)

        await self.bot.send_document(
          chat_id=message.chat.id,
          document=('scaled_img'+extension, file_output),
          thumb=cv2.imencode('.jpeg', resize_img(img, 320))[1].tobytes(),
          caption=f"Картинка размером {img.shape[0] * size} x {img.shape[1] * size} на {size}"
          )
        return True
        

bot = upscalerBot(token=API_TOKEN, model_file=MODEL_FILE)

executor.start_polling(bot.dp, skip_updates=True)