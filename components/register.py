from telebot import TeleBot
from telebot import types
from components.database import DB

def register(message: types.Message, bot: TeleBot):
    if message.chat.type == "private":
        bot.reply_to(message, "Please use this command in a group.")
        return
    try:
        DB['group'].insert_one({
            "_id": message.chat.id,
            "owner": message.from_user.id,
            "name": message.chat.title,
            "common_ads": [{"name":"Roburna Blockchain", "link":"https://t.me/Roburna"}],
            "sponsored_ads": [],
            "point_system": False,
            "voting_system": False
        })
        bot.reply_to(message, "Group registered, use the command /settings in my dm to manage your manga bot")
    except Exception as e:
        bot.reply_to(message, "This community is already registered. Please use /settings in my dm to configure your community.")
    