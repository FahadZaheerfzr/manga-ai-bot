from telebot import types
from components.database import DB
from web3 import Web3
from components.poll import get_user_points
import re

def get_user_groups(bot, user_id):
    """
    Fetches the groups where the point system is enabled and checks if the user is a member.
    """
    groups = DB['group'].find({"point_system": True})
    user_groups = []
    try:
        for group in groups:
            try:
                result = bot.get_chat_member(group['_id'], user_id)
                if result.status != "left":
                    user_groups.append(group)
            except Exception as e:
                print(e,"abacd")
                continue
    except Exception as e:
        print(e)
        raise

    return user_groups



def check_points_in_group(user_id, group_id):
    """
    This function checks the points of a user in a group.
    """
    images = DB['images'].find({"user_id": str(user_id), "group_id": group_id})
    user_points = 0
    for image in images:
        user_points += image['points']
    return user_points

def handle_points_command(update, bot):
    """
    Handles the /points command to respond with points information.
    """
    if isinstance(update, types.Message):
        message = update
        chat_id = message.chat.id
        user_id = message.from_user.id
    elif isinstance(update, types.CallbackQuery):
        message = update.message
        chat_id = message.chat.id
        user_id = update.from_user.id
    print("abcd")
    # user_id = message.from_user.id
    print(message.chat.type)
                # return user_points, image_points, referral_points, project_referralPoints, rewardPoints -- get_user_points(user_id)
    user_points, image_points, referral_points, project_referral_points, reward_points = get_user_points(user_id,sendAll=True)
    
    formatted_text = f"""
<b>Total Points:</b> {user_points}
<b>Image Points:</b> {image_points}
<b>User Referral Points:</b> {referral_points}
<b>Project Referral Points:</b> {project_referral_points}
<b>Reward Points:</b> {reward_points}
    """
    bot.send_message(user_id, formatted_text, parse_mode="HTML")



def profile(message, bot):
    """
    Responds to the /profile command and displays the user's profile.
    """
    try:
        user_groups = get_user_groups(bot, message.from_user.id)

        # if len(user_groups) == 0:
        #     bot.reply_to(message, "You are not a member of any community.")
        #     return
        
        # get botUsers
        botUsers = DB['botUsers'].find_one({"user_id": message.from_user.id})
        if not botUsers:
            DB['botUsers'].insert_one({
                "user_id": message.from_user.id,
                "username": message.from_user.username,
                "wallet": None,
            })
        
        keyboard = types.InlineKeyboardMarkup()
        if len(user_groups) >0:
            for group in user_groups:
                keyboard.add(types.InlineKeyboardButton(group['name'], callback_data="handleSelectedGroup|" + str(group['_id'])))

        if botUsers['wallet']:
            keyboard.add(types.InlineKeyboardButton("Update Wallet 💳", callback_data="setWallet_"))
            keyboard.add(types.InlineKeyboardButton("View Wallet 💳", callback_data="viewWallet_"))
        else:
            keyboard.add(types.InlineKeyboardButton("Set Wallet 💳", callback_data="setWallet_"))
        # view points
        keyboard.add(types.InlineKeyboardButton("Points Balance", callback_data="viewPoints_"))
        try:
            if botUsers['email']: 
                keyboard.add(types.InlineKeyboardButton("Update Email 📧", callback_data="setEmail_"))
                keyboard.add(types.InlineKeyboardButton("View Email 📧", callback_data="viewEmail_"))
        except:
            keyboard.add(types.InlineKeyboardButton("Set Email 📧", callback_data="setEmail_"))

        try:
            if botUsers['twitter']:
                keyboard.add(types.InlineKeyboardButton("Update Twitter 🐦", callback_data="setTwitter_"))
                keyboard.add(types.InlineKeyboardButton("View Twitter 🐦", callback_data="viewTwitter_"))
        except:
            keyboard.add(types.InlineKeyboardButton("Set Twitter 🐦", callback_data="setTwitter_"))

        keyboard.add(types.InlineKeyboardButton("Cancel", callback_data="cancel_"))
            

        
        bot.send_message(message.from_user.id, "Select a group to view your profile.", reply_markup=keyboard)
    except Exception as e:
        print(e)
        bot.reply_to(message, "An error occurred. Please try again later.")

def handleCancel (message, bot):
    try:
        bot.delete_message(message.message.chat.id, message.message.message_id)
    except Exception as e:
        print(e)
    bot.send_message(message.from_user.id, "Cancelled")

def handleSelectedGroup(message: types.CallbackQuery, bot):
    """
    Handles the selection of a group and sends the user's points for that group.
    """
    data = message.data.split("|")
    selectedGroup = int(data[1])
    user_id = message.from_user.id

    try:
        invite_link = DB['invite_link'].find_one({"user_id": str(user_id), "group_id": selectedGroup})
        if invite_link is None:
            invite_link = bot.create_chat_invite_link(selectedGroup, name=user_id)
            invite_link = invite_link.invite_link
            DB['invite_link'].update_one(
                {"user_id": str(user_id), "group_id": selectedGroup},
                {"$set": {"invite_link": invite_link, "used": []}},
                upsert=True
            )
        else:
            invite_link = invite_link['invite_link']

        user_points = check_points_in_group(user_id, selectedGroup)
        referrals = DB['referral'].count_documents({"referral_id": str(user_id)})
        referal_points = referrals * 10
        
        chat_details = bot.get_chat(selectedGroup)
        if chat_details.invite_link:
            formatted_text = f"""
<b>Community:</b> {DB['group'].find_one({"_id": selectedGroup})['name']}
<b>Art Points for the selected community:</b> {user_points}
<b>Referral Points on Manga AI group:</b> {referal_points}
Send this invite {invite_link} to your friends to earn more points.
            """
        else:
            formatted_text = f"""
<b>Community:</b> {DB['group'].find_one({"_id": selectedGroup})['name']}
<b>Art Points:</b> {user_points}
            """
        bot.send_message(user_id, formatted_text, parse_mode="HTML")
    except ValueError:
        bot.send_message(user_id, "Invalid input. Please try again.")
    except Exception as e:
        print(e)
        bot.send_message(user_id, "An error occurred. Please try again later.")


# wallet

def setWallet(message: types.CallbackQuery, bot):
    """
    Handles the setting of a wallet address for the user.
    """
        # delete last bot message 
    # try:
    #     bot.delete_message(message.chat.id, message.message_id)
    # except Exception as e:
    #     print(e)
    #     pass


    user_id = message.from_user.id
    bot.send_message(user_id, "Please enter your wallet address.")
    bot.register_next_step_handler(message.message, handleWalletInput,bot)

def handleWalletInput(message, bot):
    """
    Handles the input of the wallet address and updates the database.
    """
    if message.text == "cancel":
        bot.send_message(message.from_user.id, "Cancelled")
        return
    print("abcd",message.from_user.id)
    user_id = message.from_user.id
    wallet_address = message.text

    if not Web3.is_address(wallet_address):
        bot.send_message(user_id, "Invalid wallet address. Please try again.")
        bot.register_next_step_handler(message, handleWalletInput,bot)
        return

    DB['botUsers'].update_one(
        {"user_id": user_id},
        {"$set": {"wallet": wallet_address}},
        upsert=True
    )
    # check if user has setup all the required fields
    if checkProfileComplete(user_id):
        bot.send_message(user_id, "Wallet address updated successfully. Your profile is now complete. you get 10 points for completing your profile.")
        DB['botUsers'].update_one(
            {"user_id": user_id},
            {"$inc": {"points": 10}}
        )
        return
        

    bot.send_message(user_id, "Wallet address updated successfully.")


def viewWallet(message, bot):
        """
        Handles the viewing of the wallet address for the user.
        """
        if message.text == "cancel":
            bot.send_message(message.from_user.id, "Cancelled")
            return
        user_id = message.from_user.id
        botUsers = DB['botUsers'].find_one({"user_id": user_id})
        wallet_address = botUsers['wallet']
        if wallet_address:
            bot.send_message(user_id, f"Your wallet address: {wallet_address}")
        else:
            bot.send_message(user_id, "You have not set a wallet address yet.")


    # email
            
def setEmail(message: types.CallbackQuery, bot):
    """
    Handles the setting of an email address for the user.
    """
    user_id = message.from_user.id
    bot.send_message(user_id, "Please enter your email address.")
    bot.register_next_step_handler(message.message, handleEmailInput,bot)

def handleEmailInput(message, bot):
    """
    Handles the input of the email address and updates the database.
    """
    user_id = message.from_user.id
    email = message.text
    if message.text == "cancel":
        bot.send_message(message.from_user.id, "Cancelled")
        return

    if not "@" in email or not "." in email:
        bot.send_message(user_id, "Invalid email address. Please try again.")
        bot.register_next_step_handler(message, handleEmailInput,bot)
        return

    DB['botUsers'].update_one(
        {"user_id": user_id},
        {"$set": {"email": email}},
        upsert=True
    )
    if checkProfileComplete(user_id):
        bot.send_message(user_id, "Email updated successfully. Your profile is now complete. you get 10 points for completing your profile.")
        DB['botUsers'].update_one(
            {"user_id": user_id},
            {"$inc": {"points": 10}}
        )
        return
    bot.send_message(user_id, "Email address updated successfully.")

def viewEmail(message, bot):
    """
    Handles the viewing of the email address for the user.
    """
    user_id = message.from_user.id
    botUsers = DB['botUsers'].find_one({"user_id": user_id})
    email = botUsers['email']
    if email:
        bot.send_message(user_id, f"Your email address: {email}")
    else:
        bot.send_message(user_id, "You have not set an email address yet.")

    # twitter
        
def setTwitter(message: types.CallbackQuery, bot):
    """
    Handles the setting of a twitter username for the user.
    """
    user_id = message.from_user.id
    bot.send_message(user_id, "Please enter your twitter link.")
    bot.register_next_step_handler(message.message, handleTwitterInput,bot)

def handleTwitterInput(message, bot):
    """
    Handles the input of the twitter username and updates the database.
    """
    if message.text == "cancel":
        bot.send_message(message.from_user.id, "Cancelled")
        return
    user_id = message.from_user.id
    twitter = message.text
    if not re.match(r'^https?:\/\/(www\.)?(twitter\.com|x\.com)\/[a-zA-Z0-9_]+$', twitter):
        bot.send_message(user_id, "Invalid twitter link. Please try again.")
        bot.register_next_step_handler(message, handleTwitterInput,bot)
        return

    DB['botUsers'].update_one(
        {"user_id": user_id},
        {"$set": {"twitter": twitter}},
        upsert=True
    )
    if checkProfileComplete(user_id):
        bot.send_message(user_id, "Twitter updated successfully. Your profile is now complete. you get 10 points for completing your profile.")
        DB['botUsers'].update_one(
            {"user_id": user_id},
            {"$inc": {"points": 10}}
        )
        return
    bot.send_message(user_id, "Twitter username updated successfully.")

def viewTwitter(message, bot):
    """
    Handles the viewing of the twitter username for the user.
    """
    user_id = message.from_user.id
    botUsers = DB['botUsers'].find_one({"user_id": user_id})
    twitter = botUsers['twitter']
    if twitter:
        bot.send_message(user_id, f"Your twitter link: {twitter}")
    else:
        bot.send_message(user_id, "You have not set a twitter link yet.")

        

def checkProfileComplete(user_id):
    user = DB['botUsers'].find_one({"user_id": user_id})
    if "wallet" in user and "email" in user and "twitter" in user:
        DB['botUsers'].update_one(
            {"user_id": user_id},
            {"$set": {"profile_complete": True}}
        )
        return True
    return False