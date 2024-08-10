from telebot import types
from components.database import DB
from config import BOT_TOKEN 
from bson import ObjectId

# user referral
def user_referral(update, bot):
    if isinstance(update, types.Message):
        message = update
        chat_id = message.chat.id
        user_id = message.from_user.id
        send_id = user_id
    elif isinstance(update, types.CallbackQuery):
        message = update.message
        chat_id = message.chat.id
        user_id = update.from_user.id
        send_id = chat_id

    user = DB['botUsers'].find_one({"user_id": user_id})
    if not user:
        bot.reply_to(message, "User not found.")
        return
    # check which campaigns user is part of in user["campaigns"]
    try:
        listOfCampaignObjectIds = user["campaigns"]
    except Exception as e:
        bot.reply_to(message, "User has no campaigns.")
        return
    campaigns = []
    for campaignObjectId in listOfCampaignObjectIds:
        campaign = DB['campaigns'].find_one({"_id": campaignObjectId})
        if campaign:
            campaigns.append(campaign)
    print(campaigns)
    markup = types.InlineKeyboardMarkup()
    for idx in range(1, len(campaigns) + 1):
        markup.add(types.InlineKeyboardButton(campaigns[idx - 1]["name"], callback_data="handleSelectedCampaign|" + str(campaigns[idx - 1]["_id"])))
    bot.send_message(send_id, "Select a campaign to generate referral link.", reply_markup=markup)


def handleSelectedCampaign(update: types.CallbackQuery, bot):
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


        # generate referral link to the bot
    referralLink = f"https://t.me/{bot.get_me().username}?start={user_id}_{campaign_id}_userReferral"
    bot.send_message(update.message.chat.id, f"Your referral link for the campaign {campaign['name']} is {referralLink}")


def projectReferralLink(update,bot):
    """
    This function generates a referral link for a user and a campaign.

    Args:
        user_id (int): The ID of the user
        campaign_id (str): The ID of the campaign

    Returns:
        str: The referral link
    """
    if isinstance(update, types.Message):
        message = update
        chat_id = message.chat.id
        user_id = message.from_user.id
        send_id = user_id
    elif isinstance(update, types.CallbackQuery):
        message = update.message
        chat_id = message.chat.id
        user_id = update.from_user.id
        send_id = chat_id

    referralLink = f"https://t.me/{bot.get_me().username}?start={user_id}_projectReferral"
    
    bot.send_message(send_id, f"Your referral link is {referralLink}")
