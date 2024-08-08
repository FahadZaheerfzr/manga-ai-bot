from telebot import types
from components.database import DB
from web3 import Web3

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

def get_points(bot,user_id, group_id=None):
    """
    Fetches the points for a user either for a specific group or across all groups.
    """
    if group_id:
        return check_points_in_group(user_id, group_id)
    else:
        total_points = 0
        user_groups = get_user_groups(bot, user_id)
        for group in user_groups:
            total_points += check_points_in_group(user_id, group['_id'])
        return total_points

def check_points_in_group(user_id, group_id):
    """
    This function checks the points of a user in a group.
    """
    images = DB['images'].find({"user_id": str(user_id), "group_id": group_id})
    user_points = 0
    for image in images:
        user_points += image['points']
    return user_points

def handle_points_command(message, bot):
    """
    Handles the /points command to respond with points information.
    """
    print("abcd")
    user_id = message.from_user.id
    print(message.chat.type)
    total_points = 0
    if message.chat.type == 'private':  # DM case
        total_points = get_points(bot,user_id)
        # check daily rewards
        daily_reward = DB['daily_rewards'].find_one({"user_id": int(user_id)})
        if daily_reward:
            total_points += daily_reward["points"]
        bot.send_message(user_id, f"Your total points across all groups: {total_points}")
    else:  # Group case
        user_groups = get_user_groups(bot, user_id)
        if user_groups:
            group_id = message.chat.id
            if group_id in [group['_id'] for group in user_groups]:
                print("group_id",group_id)
                points = get_points(bot,user_id, group_id)
                daily_reward = DB['daily_rewards'].find_one({"user_id": int(user_id)})
                if daily_reward:
                    total_points += daily_reward["points"]
                bot.reply_to(message, f"Your points in this group: {points}")
            else:
                bot.reply_to(message, "You are not a member of this group or the group point system is not enabled.")
        else:
            bot.send_message(user_id, "You are not a member of any community.")

def profile(message, bot):
    """
    Responds to the /profile command and displays the user's profile.
    """
    try:
        user_groups = get_user_groups(bot, message.from_user.id)

        if len(user_groups) == 0:
            bot.reply_to(message, "You are not a member of any community.")
            return
        
        # get botUsers
        botUsers = DB['botUsers'].find_one({"user_id": message.from_user.id})
        if not botUsers:
            DB['botUsers'].insert_one({
                "user_id": message.from_user.id,
                "username": message.from_user.username,
                "wallet": None,
            })
        
        keyboard = types.InlineKeyboardMarkup()
        for group in user_groups:
            keyboard.add(types.InlineKeyboardButton(group['name'], callback_data="handleSelectedGroup|" + str(group['_id'])))

        if botUsers['wallet']:
            keyboard.add(types.InlineKeyboardButton("Update Wallet 💳", callback_data="setWallet_"))
            keyboard.add(types.InlineKeyboardButton("View Wallet 💳", callback_data="viewWallet_"))
        else:
            keyboard.add(types.InlineKeyboardButton("Set Wallet 💳", callback_data="setWallet_"))

        
        bot.send_message(message.from_user.id, "Select a group to view your profile.", reply_markup=keyboard)
    except Exception as e:
        print(e)
        bot.reply_to(message, "An error occurred. Please try again later.")

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
    bot.send_message(user_id, "Wallet address updated successfully.")


def viewWallet(message, bot):
        """
        Handles the viewing of the wallet address for the user.
        """
        user_id = message.from_user.id
        botUsers = DB['botUsers'].find_one({"user_id": user_id})
        wallet_address = botUsers['wallet']
        if wallet_address:
            bot.send_message(user_id, f"Your wallet address: {wallet_address}")
        else:
            bot.send_message(user_id, "You have not set a wallet address yet.")