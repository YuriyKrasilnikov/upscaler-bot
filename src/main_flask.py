from flask import (Flask, request, abort)

import telebot
from utils import *

app = Flask(__name__)

@app.route(f'/webhook/{API_TOKEN}', methods=['POST'])
def webhook():
    logging.warning('flask webhook starting')
    if True or request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        abort(403)

@app.route(f'/webhook/{API_TOKEN}', methods=['GET'])
def test_get():
    logging.warning('flask webhook test_get')
    return 'flask webhook test_get'

@app.route(f'/', methods=['GET'])
def root():
    logging.warning('flask webhook root')
    return 'flask webhook root'

