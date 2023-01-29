import os
import asyncio
import logging

from aiohttp import web

import telebot
from .utils import *

app = web.Application()

# Process webhook calls
async def handle(request):
    logging.warning('aiohttp handle starting')
    if True or request.match_info.get('token') == bot.token:
        logging.warning('Token done')
        request_body_dict = await request.json()
        update = telebot.types.Update.de_json(request_body_dict)
        bot.process_new_updates([update])
        return web.Response(status=200)
    else:
        logging.warning('Error 403')
        return web.Response(status=403)

app.router.add_post(f'/webhook/{API_TOKEN}', handle)

web.run_app(app)
