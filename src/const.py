import os
import logging

API_TOKEN = os.environ.get("API_TOKEN")

SCALE = int(os.environ.get("SCALE", 2))
MAX_SIZE = int(os.environ.get("MAX_SIZE", 1080))

MODEL_NAME = os.environ.get("MODEL_NAME", "RealESRGAN_x2plus")

SELF_PATH = os.path.dirname(os.path.realpath(__file__))

MODEL_PATH = SELF_PATH+r"/weights"
MODEL_FILE = MODEL_PATH + r"/"+MODEL_NAME+".pth"

logging.basicConfig(level=logging.INFO)