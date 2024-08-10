from config import BOT_TOKEN
import telebot  # pip install pyTelegramBotAPI
from telebot import types
from components.start import start  # import the start function from the start.py file
from components.generate import generate, generate_image, generateDefault  # import the generate function from the generate.py file
from components.register import register  # import the register function from the register.py file
from components.database import DB
from components.profile import (profile, handleSelectedGroup, handle_points_command, setWallet, viewWallet, setEmail,setTwitter,viewEmail,viewTwitter)
from components.join_group import join_group
from components.settings import (settings, handleSelectedCommunity, removeCommunity, cancel, enableNotif, disableNotif, notifSettings, defaultImage, setDefaultImageNormal, setDefaultImageAnime)
from components.vote import vote, handle_vote_reply_message
from components.help import help
from components.leaderboard import handle_leaderboard_command
from components.admin import disqualify
from components.daily import daily_reward
from components.campaign import (organizeCampaign, handleSelectedOrganize, handleConfirm, joinCampaign, handleSelectedJoin, handleSelectedJoin_cancel,campaign_details,handleSelectedCampaignDetails)
from components.referral import user_referral, handleSelectedCampaign, projectReferralLink
from components.poll import create_poll, handle_poll
from datetime import datetime
import threading
import time

# Create a bot object with the bot token
mint_bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)

# Register message handlers
mint_bot.register_message_handler(start,pass_bot=True, commands=['start'])
mint_bot.register_message_handler(register,pass_bot=True, commands=['register'])
mint_bot.register_message_handler(generate_image,pass_bot=True, commands=['normal'])
mint_bot.register_message_handler(generate,pass_bot=True, commands=['anime'])
mint_bot.register_message_handler(generateDefault, pass_bot=True,commands=['img'])
mint_bot.register_message_handler(settings,pass_bot=True, commands=['settings'])
mint_bot.register_message_handler(profile,pass_bot=True, commands=['profile'])
mint_bot.register_message_handler(help,pass_bot=True, commands=['help'])
mint_bot.register_message_handler(handle_points_command,pass_bot=True, commands=['points'])
mint_bot.register_message_handler(handle_leaderboard_command,pass_bot=True, commands=['leaderboard'])
mint_bot.register_message_handler(disqualify,pass_bot=True, commands=['disqualify'])
mint_bot.register_message_handler(daily_reward,pass_bot=True, commands=['daily'])
mint_bot.register_message_handler(organizeCampaign,pass_bot=True, commands=['organize_campaign'])
mint_bot.register_message_handler(joinCampaign,pass_bot=True, commands=['join_campaign'])
mint_bot.register_message_handler(user_referral,pass_bot=True, commands=['user_referral'])
mint_bot.register_message_handler(projectReferralLink,pass_bot=True, commands=['project_referral'])
mint_bot.register_message_handler(create_poll,pass_bot=True, commands=['vote'])
mint_bot.register_message_handler(campaign_details,pass_bot=True, commands=['campaign_details'])

# Register the handler for poll answers
@mint_bot.poll_answer_handler()
def handle_poll_answer(poll_answer,required_points=100):
    print("Poll answer received")
    handle_poll(poll_answer, mint_bot, required_points)

# Register callback query handlers
mint_bot.register_callback_query_handler(vote, pass_bot=True, func=lambda call: call.data.startswith('vote_'))
mint_bot.register_callback_query_handler(handleSelectedCommunity, pass_bot=True, func=lambda call: call.data.startswith('handleSelectedCommunity|'))
mint_bot.register_callback_query_handler(removeCommunity, pass_bot=True, func=lambda call: call.data.startswith('removeCommunity_'))
mint_bot.register_message_handler(cancel, pass_bot=True, commands=['cancel'])
mint_bot.register_callback_query_handler(handleSelectedGroup, pass_bot=True, func=lambda call: call.data.startswith('handleSelectedGroup|'))
mint_bot.register_chat_member_handler(join_group, pass_bot=True)
mint_bot.register_callback_query_handler(enableNotif, pass_bot=True, func=lambda call: call.data.startswith('enableNotif_'))
mint_bot.register_callback_query_handler(disableNotif, pass_bot=True, func=lambda call: call.data.startswith('disableNotif_'))
mint_bot.register_callback_query_handler(notifSettings, pass_bot=True, func=lambda call: call.data.startswith('notifSettings_'))
mint_bot.register_callback_query_handler(defaultImage, pass_bot=True, func=lambda call: call.data.startswith('defaultImage_'))
mint_bot.register_callback_query_handler(setDefaultImageNormal, pass_bot=True, func=lambda call: call.data.startswith('setDefaultImageNormal_'))
mint_bot.register_callback_query_handler(setDefaultImageAnime, pass_bot=True, func=lambda call: call.data.startswith('setDefaultImageAnime_'))
mint_bot.register_callback_query_handler(settings, pass_bot=True, func=lambda call: call.data.startswith('settings_'))
mint_bot.register_callback_query_handler(setWallet, pass_bot=True, func=lambda call: call.data.startswith('setWallet_'))
mint_bot.register_callback_query_handler(viewWallet, pass_bot=True, func=lambda call: call.data.startswith('viewWallet_'))
mint_bot.register_callback_query_handler(handleSelectedOrganize, pass_bot=True, func=lambda call: call.data.startswith('handleSelectedOrganize|'))
mint_bot.register_callback_query_handler(handleConfirm, pass_bot=True, func=lambda call: call.data.startswith('confirm_'))
mint_bot.register_callback_query_handler(handleSelectedJoin, pass_bot=True, func=lambda call: call.data.startswith('handleSelectedJoin|'))
mint_bot.register_callback_query_handler(handleSelectedJoin_cancel, pass_bot=True, func=lambda call: call.data.startswith('handleSelectedJoin_cancel'))
mint_bot.register_callback_query_handler(handleSelectedCampaign, pass_bot=True, func=lambda call: call.data.startswith('handleSelectedCampaign|'))
mint_bot.register_callback_query_handler(handle_points_command, pass_bot=True, func=lambda call: call.data.startswith('viewPoints_'))
mint_bot.register_callback_query_handler(setEmail, pass_bot=True, func=lambda call: call.data.startswith('setEmail_'))
mint_bot.register_callback_query_handler(setTwitter, pass_bot=True, func=lambda call: call.data.startswith('setTwitter_'))
mint_bot.register_callback_query_handler(viewEmail, pass_bot=True, func=lambda call: call.data.startswith('viewEmail_'))
mint_bot.register_callback_query_handler(viewTwitter, pass_bot=True, func=lambda call: call.data.startswith('viewTwitter_'))
mint_bot.register_callback_query_handler(handleSelectedCampaignDetails, pass_bot=True, func=lambda call: call.data.startswith('handleSelectedCampaignDetails|'))


me = mint_bot.get_me()  # Get the bot information
print(me.username)  # Print the bot username

commands = [
    types.BotCommand(command='/start', description='Start the bot'),
    types.BotCommand(command='/register', description='Register a new user'),
    types.BotCommand(command='/normal', description='Generate a normal image'),
    types.BotCommand(command='/anime', description='Generate an anime image'),
    types.BotCommand(command='/img', description='Generate a default image'),
    types.BotCommand(command='/settings', description='Update settings'),
    types.BotCommand(command='/profile', description='View your profile'),
    types.BotCommand(command='/help', description='Get help with commands'),
    types.BotCommand(command='/leaderboard', description='Show the top 5 users with the highest points in this group'),
    types.BotCommand(command='/points', description='Show your points'),
    types.BotCommand(command='/disqualify', description='Disqualify a user from the daily reward'),
    types.BotCommand(command='/daily', description='Claim the daily reward'),
    types.BotCommand(command='/organize_campaign', description='Organize a campaign'),
    types.BotCommand(command='/join_campaign', description='Join a campaign'),
    types.BotCommand(command='/user_referral', description='Get your referral link'),
    types.BotCommand(command='/project_referral', description='Get your project referral link'),
    types.BotCommand(command='/campaign_details', description='View campaign details')
]
mint_bot.set_my_commands(commands)

allowed_updates = ["chat_member", "message", "callback_query", "poll_answer"]

def check_campaign_end():
    print("Checking campaign end...")
    while True:
        campaigns = DB['campaigns'].find()
        for campaign in campaigns:
            end_date = datetime.strptime(campaign['end_date'], "%Y-%m-%d")
            if end_date < datetime.now():
                for participant in campaign['participants']:
                    images = list(DB['images'].find({"campaign_id": campaign['_id'], "user_id": participant}))
                    if not images:
                        return
                    if not images.count() == 0:
                        return
                    else:
                        DB['botUsers'].update_one(
                            {"user_id": participant},
                            {"$inc": {"points": 100}}
                        )
        time.sleep(60)

# Start the campaign end checker in a new thread
threading.Thread(target=check_campaign_end).start()

# Start the bot
mint_bot.polling(allowed_updates=allowed_updates)
