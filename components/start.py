from components.database import DB
from bson import ObjectId
from components.campaign import organizeCampaign

def start(message, bot):
    """
    This function responds to the /start command

    Args:
        message (telebot.types.Message): The message object
        bot (telebot.TeleBot): The bot object
    
    Returns:
        None
    """
    # store user in db called botUsers
    # check if user already exists
    user = DB['botUsers'].find_one({"user_id": message.from_user.id})
    if not user:
        DB['botUsers'].insert_one({
            "user_id": message.from_user.id,
            "username": message.from_user.username,
            "wallet": None,
        })

    if message.text.startswith('/start'):
        query = message.text.split('_')
        if (len(query) == 3) and (query[2] == 'userReferral'):
            user_id = int(query[0].split(" ")[1])
            campaign_id = query[1]
            # check if user_id and campaign_id are valid
            user = DB['botUsers'].find_one({"user_id": int(user_id)})
            campaign = DB['campaigns'].find_one({"_id": ObjectId(campaign_id)})
            print(user_id, campaign_id)
            if not user:
                bot.reply_to(message, "Invalid user ID.")
                return
            if not campaign:
                bot.reply_to(message, "Invalid campaign ID.")
                return
            # check if user is part of the campaign
            if user_id not in campaign["participants"]:
                bot.reply_to(message, "User is not part of the campaign.")
                return
            # check if user has already referred
            referral = DB['user_referrals'].find_one({"user_id": int(user_id), "campaign_id": ObjectId(campaign_id), "referral_id": message.from_user.id})
            if referral:
                bot.reply_to(message, "You have already claimed the referral.")
                return
            # give points to user
            DB['user_referrals'].insert_one({
                "user_id": int(user_id),
                "campaign_id": ObjectId(campaign_id),
                "referral_id": message.from_user.id,
                "points": 5,
            })
            DB['campaigns'].update_one({"_id": ObjectId(campaign_id)}, {"$push": {"participants": user_id}})
            DB['botUsers'].update_one({"user_id": user_id}, {"$push": {"campaigns": ObjectId(campaign_id)}})

            bot.send_message(message.from_user.id, startFormat() + "\nYou have claimed 5 points from the referral.", parse_mode="HTML", disable_web_page_preview=True)
            bot.send_message(user_id, f"User {message.from_user.username} has claimed your referral you get 5 points!", parse_mode="HTML", disable_web_page_preview=True)
            return
        else:
            organizeCampaign(message, bot)
            return


    bot.send_message(message.from_user.id, startFormat(), parse_mode="HTML", disable_web_page_preview=True)

#format for the start command respose message
def startFormat():
    """
    This function returns the format for the /start command response message

    Args:
        None
    """

    return """
Hi! I'm <b>MangaAI Bot</b>. Let's get started: \n
 
Please note, I am in beta version, so errors, issues, and omissions are possible! \n

<code>Created by Roburna Network</code>
           """
