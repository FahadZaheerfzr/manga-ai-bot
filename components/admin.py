from components.database import DB
from utils.decorators import admin_only
from config import BOT_TOKEN 
import telebot 
mint_bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None) # create a bot object with the bot token we have


# disqualify an image /disqualify image_id
@admin_only(bot=mint_bot)
def disqualify(message, bot):
    """
    Disqualifies an image from the voting process.
    """
    try:
        image_id = message.text.split(" ")[1]
        print (image_id)
    except (ValueError, IndexError):
        print (message.text)
        bot.reply_to(message, "Invalid input. Please use the format: /disqualify image_id")
        return

    image = DB['images'].find_one({"id": image_id})
    if not image:
        bot.reply_to(message, "Image not found.")
        return

    # add disqualified field to the image
    DB['images'].update_one({"id": image_id}, {"$set": {"disqualified": True}})
    bot.reply_to(message, "Image disqualified successfully.")
    return


