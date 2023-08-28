from components.database import DB
from telebot import types


def profile(message, bot):
    """
    This function responds to the /profile command and displays
    the user's points and referral link
    """

    # Get all the groups where point system is enabled
    groups = DB['group'].find({"point_system": True})

    # Check if the user is member of any of the groups
    user_groups = []
    try:
        for group in groups:
            try:
                result = bot.get_chat_member(group['_id'], message.from_user.id)
                if result.status != "left":
                    user_groups.append(group)
            except Exception as e:
                print(e)
                continue
        
        print(user_groups)

        if len(user_groups) == 0:
            bot.reply_to(message, "You are not a member of any community.")
            return
        
        # Show the buttons to select the community
        keyboard = types.InlineKeyboardMarkup()
        for group in user_groups:
            keyboard.add(types.InlineKeyboardButton(group['name'], callback_data="handleSelectedGroup|" + str(group['_id'])))
        bot.send_message(message.from_user.id, "Select a group to view your profile.", reply_markup=keyboard)
    except Exception as e:
        print(e)
        bot.reply_to(message, "An error occured. Please try again later.")


def handleSelectedGroup(message: types.CallbackQuery,bot):
    data = message.data.split("|")

    selectedGroup = data[1]

    try:
        # get all the points of the user in the selected group
        images = DB['images'].find({"user_id": str(message.from_user.id), "group_id": selectedGroup})
        referrals = DB['referral'].find({"user_id": str(message.from_user.id), "chat_id": selectedGroup})
        referal_points = len(referrals)
        user_points = 0
        for image in images:
            user_points += image['points']
        chat_details = bot.get_chat(selectedGroup)
        if chat_details.invite_link is not None:
            formatted_text = f"""
<b>Community:</b> {DB['group'].find_one({"_id": int(selectedGroup)})['name']}
<b>Art Points:</b> {user_points}
<b>Referral Points:</b> {referal_points}
<b>Referral Code:</b> {message.from_user.id} \n
Send this invite {chat_details.invite_link} to your friends along with your referral code to earn more points.
            """
        else:
            formatted_text = f"""
<b>Community:</b> {DB['group'].find_one({"_id": int(selectedGroup)})['name']}
<b>Art Points:</b> {user_points}
            """
        bot.send_message(message.from_user.id, formatted_text, parse_mode="HTML")
    except ValueError:
        bot.send_message(message.from_user.id, "Invalid input. Please try again.")