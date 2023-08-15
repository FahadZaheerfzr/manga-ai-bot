from telebot import types
from ai.stability import generate_text_to_image

def generate(message,bot):
    """
    This function responds to the /generate command

    Args:
        message (telebot.types.Message): The message object
        bot (telebot.TeleBot): The bot object
    
    Returns:
        None
    """
    bot.send_message(message.from_user.id, "Generating image...")

    generate_text_to_image()

    bot.send_message(message.from_user.id, "Image generated! Check your DMs!")

    bot.send_photo(message.from_user.id, open('v1_txt2img_0.png', 'rb'))
