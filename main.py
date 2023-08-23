from config import BOT_TOKEN 
import telebot # pip install pyTelegramBotAPI
from components.start import start #import the start function from the start.py file
from components.generate import generate #import the generate function from the generate.py file
from components.register import register #import the register function from the register.py file
from components.database import DB
from components.join_group import join_group
from components.settings import settings, handleSelectedCommunity, removeCommunity, cancel
mint_bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None) # create a bot object with the bot token we have


mint_bot.register_message_handler(join_group, content_types=["new_chat_members"], pass_bot=True)  
mint_bot.register_message_handler(start, pass_bot=True, commands=['start'])
mint_bot.register_message_handler(register, pass_bot=True, commands=['register'])
mint_bot.register_message_handler(generate, pass_bot=True, commands=['img'])
mint_bot.register_message_handler(settings, pass_bot=True, commands=['settings'])

mint_bot.register_callback_query_handler(handleSelectedCommunity, pass_bot=True, func=lambda call: call.data.startswith('handleSelectedCommunity|'))
mint_bot.register_callback_query_handler(removeCommunity, pass_bot=True, func=lambda call: call.data.startswith('removeCommunity_'))
mint_bot.register_message_handler(cancel, pass_bot=True, commands=['cancel'])

me = mint_bot.get_me() #get the bot information
print(me.username) #print the bot username
mint_bot.polling() #start the bot
