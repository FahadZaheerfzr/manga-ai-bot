from telebot import types
from components.database import DB
from datetime import datetime, timedelta
from utils.functions import getGroups
from components.settings import settingFormatCommunity
from passlib.context import CryptContext
from uuid import uuid4
from bson import ObjectId



pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def get_hashed_password(password):
    return pwd_context.hash(password)


def organizeCampaign(update, bot):
    if isinstance(update, types.Message):
        message = update
        chat_id = message.chat.id
        user_id = message.from_user.id
        send_id = user_id
    elif isinstance(update, types.CallbackQuery):
        message = update.message
        chat_id = message.chat.id
        user_id = update.from_user.id
        send_id=chat_id

    communities = getGroups(bot, update, message, user_id)

    markup = types.InlineKeyboardMarkup()
    for idx in range(1, len(communities) + 1):
        markup.add(types.InlineKeyboardButton(str(communities[idx - 1]), callback_data="handleSelectedOrganize|" + str(communities[idx - 1])))

    markup.add(types.InlineKeyboardButton("cancel", callback_data="handleSelectedOrganize_cancel"))
    print(message.from_user.id, "message.from_user.id")
    bot.send_message(send_id, settingFormatCommunity(), reply_markup=markup, parse_mode="HTML")


def handleSelectedOrganize(update: types.CallbackQuery, bot):
    data = update.data.split("|")
    community_id = int(data[1].split("(")[1].split(")")[0])
    user_id = update.from_user.id

    community = DB['group'].find_one({"_id": community_id})
    if not community:
        bot.reply_to(update.message, "Community not found.")
        return

    # Check if the user is the owner of the community
    if community["owner"] != user_id:
        bot.reply_to(update.message, "You are not the owner of this community.")
        return
    # ask for start message of the new campaign

    bot.send_message(user_id, "Please enter the name for the campaign.")

    bot.register_next_step_handler(update.message, handleCampaignName, community_id, bot)


def handleCampaignName(message, community_id, bot):
    campaign_name = message.text
    bot.send_message(message.chat.id, "Please enter the description for the campaign.")
    bot.register_next_step_handler(message, handleCampaignDescription, community_id, campaign_name, bot)


def handleCampaignDescription(message, community_id, campaign_name, bot):
    campaign_description = message.text
    bot.send_message(message.chat.id, "Please enter the end date for the campaign in the format YYYY-MM-DD.")
    bot.register_next_step_handler(message, handleCampaignEndDate, community_id, campaign_name, campaign_description, bot)


def handleCampaignEndDate(message, community_id, campaign_name, campaign_description, bot):
    try:
        end_date = datetime.strptime(message.text, "%Y-%m-%d").date()
    except ValueError:
        bot.reply_to(message, "Invalid date format. Please use YYYY-MM-DD.")
        return

    if end_date < datetime.now().date():
        bot.reply_to(message, "End date must be in the future.")
        return

    DB['campaigns'].insert_one({
        "community_id": community_id,
        "name": campaign_name,
        "description": campaign_description,
        "end_date": str(end_date),
        "participants": [],})
    
    bot.send_message(message.chat.id, "Campaign created successfully. Please provide your email address for the admin panel.")

    bot.register_next_step_handler(message, handleCampaignEmail, community_id, bot)


def handleCampaignEmail(message, community_id, bot):
    email = message.text
    if DB["users"].find_one({"email": email}):
        bot.reply_to(message, "You have already registered with this email address.")

    else:
        key=str(uuid4())
        email=email
        password=get_hashed_password(str(key))
        role= "user"
        print (email, password, role, key)
        DB["users"].insert_one({
            "email": email,
            "password": password,
            "role": role,
            "id": message.from_user.id
        })

        # button to confirm and delete the message
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Confirm", callback_data="confirm_"))

        text = f"Here are your credentials for the admin panel:\n\nEmail: {email}\nPassword: {key}\n\nPlease save this information as it will not be shown again after you click confirm."

        bot.send_message(message.chat.id, text, reply_markup=markup)


def handleConfirm(update, bot):
    bot.delete_message(update.message.chat.id, update.message.message_id)
 

#  join campaign
def joinCampaign(update, bot):
    if isinstance(update, types.Message):
        message = update
        chat_id = message.chat.id
        user_id = message.from_user.id
        send_id = user_id
    elif isinstance(update, types.CallbackQuery):
        message = update.message
        chat_id = message.chat.id
        user_id = update.from_user.id
        send_id=chat_id

    allCampaigns = DB['campaigns'].find()
    campaigns = []
    for campaign in allCampaigns:
        if user_id not in campaign["participants"]:
            campaigns.append(campaign)

    markup = types.InlineKeyboardMarkup()
    for idx in range(1, len(campaigns) + 1):
        markup.add(types.InlineKeyboardButton(campaigns[idx - 1]["name"], callback_data="handleSelectedJoin|" + str(campaigns[idx - 1]["_id"])))

    markup.add(types.InlineKeyboardButton("cancel", callback_data="handleSelectedJoin_cancel"))

    bot.send_message(send_id, "Select a campaign to join.", reply_markup=markup)


def handleSelectedJoin(update: types.CallbackQuery, bot):
    campaign_id = update.data.split("|")[1]
    user_id = update.from_user.id

    try:
        campaign_object_id = ObjectId(campaign_id)
    except Exception as e:
        bot.reply_to(update.message, "Invalid campaign ID.")
        return

    campaign = DB['campaigns'].find_one({"_id": campaign_object_id})
    if not campaign:
        bot.reply_to(update.message, "Campaign not found.")
        return
    # if user already in it dont add
    if user_id in campaign["participants"]:
        bot.reply_to(update.message, "You are already in this campaign.")
        return
    DB['campaigns'].update_one({"_id": campaign_object_id}, {"$push": {"participants": user_id}})
    bot.reply_to(update.message, "You have successfully joined the campaign.")

def handleSelectedJoin_cancel(update: types.CallbackQuery, bot):
    bot.delete_message(update.message.chat.id, update.message.message_id)
    bot.send_message(update.message.chat.id, "Cancelled.")

    