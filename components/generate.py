from telebot import types
from components.ai.stability import generate_text_to_image
from config import BACKEND_URL
import requests
from PIL import Image

def generate(message,bot):
    """
    This function responds to the /generate command

    Args:
        message (telebot.types.Message): The message object
        bot (telebot.TeleBot): The bot object
    
    Returns:
        None
    """ 
    prompt = message.text.split(" ", 1)[1]
    print(prompt)
    params = {
        "prompt": prompt,
        "name":message.from_user.username,
        "user_id": message.from_user.id,
        "group_id": message.chat.id,
    }
    image_file_path = "v1_txt2img_0.png"
    generate_text_to_image(prompt)
    with open(image_file_path, "rb") as image_file:
        files = {
            "image_file": (image_file_path, image_file, "image/png")
        }
        response = requests.post(BACKEND_URL+"/images", params=params, files=files)
    image = Image.open(image_file_path)
    watermark = Image.open("image/watermark.png")
    image.paste(watermark, (0, 0), watermark)
    image.save(image_file_path)
    bot.send_photo(message.chat.id, open('v1_txt2img_0.png', 'rb'))
