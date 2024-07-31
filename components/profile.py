from telebot import types
from components.database import DB

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
    if message.chat.type == 'private':  # DM case
        total_points = get_points(bot,user_id)
        bot.send_message(user_id, f"Your total points across all groups: {total_points}")
    else:  # Group case
        user_groups = get_user_groups(bot, user_id)
        if user_groups:
            group_id = message.chat.id
            if group_id in [group['_id'] for group in user_groups]:
                print("group_id",group_id)
                points = get_points(bot,user_id, group_id)
                bot.send_message(user_id, f"Your points in this group: {points}")
            else:
                bot.send_message(user_id, "You are not a member of this group or the group point system is not enabled.")
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
        
        keyboard = types.InlineKeyboardMarkup()
        for group in user_groups:
            keyboard.add(types.InlineKeyboardButton(group['name'], callback_data="handleSelectedGroup|" + str(group['_id'])))
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
