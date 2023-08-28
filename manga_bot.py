from config import BOT_TOKEN 
import telebot # pip install pyTelegramBotAPI
from components.start import start #import the start function from the start.py file
from components.generate import generate, generate_image #import the generate function from the generate.py file
from components.register import register #import the register function from the register.py file
from components.database import DB
from components.profile import profile, handleSelectedGroup
from components.join_group import join_group
from components.settings import settings, handleSelectedCommunity, removeCommunity, cancel
from components.referral import referral
mint_bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None) # create a bot object with the bot token we have

#mint_bot.register_message_handler(join_group, content_types=["new_chat_members"], pass_bot=True)  
mint_bot.register_message_handler(start, pass_bot=True, commands=['start'])
mint_bot.register_message_handler(register, pass_bot=True, commands=['register'])
mint_bot.register_message_handler(referral, pass_bot=True, commands=['referral'])
mint_bot.register_message_handler(generate_image, pass_bot=True, commands=['img'])
mint_bot.register_message_handler(generate, pass_bot=True, commands=['anime'])
mint_bot.register_message_handler(settings, pass_bot=True, commands=['settings'])
mint_bot.register_message_handler(profile, pass_bot=True, commands=['profile'])
mint_bot.register_callback_query_handler(handleSelectedCommunity, pass_bot=True, func=lambda call: call.data.startswith('handleSelectedCommunity|'))
mint_bot.register_callback_query_handler(removeCommunity, pass_bot=True, func=lambda call: call.data.startswith('removeCommunity_'))
mint_bot.register_message_handler(cancel, pass_bot=True, commands=['cancel'])
mint_bot.register_callback_query_handler(handleSelectedGroup, pass_bot=True, func=lambda call: call.data.startswith('handleSelectedGroup|'))
mint_bot.register_chat_member_handler(join_group, pass_bot=True)

me = mint_bot.get_me() #get the bot information
print(me.username) #print the bot username


allowed_updates = ["chat_member", "message", "callback_query"] #the allowed updates

mint_bot.polling(allowed_updates=allowed_updates) #start the bot
