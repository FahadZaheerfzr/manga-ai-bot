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
    for group in groups:
        if bot.get_chat_member(group['_id'], message.from_user.id):
            user_groups.append(group)
    
    if len(user_groups) == 0:
        bot.reply_to(message, "You are not a member of any community.")
        return
    
    # Show the buttons to select the community
    keyboard = types.InlineKeyboardMarkup()
    for group in user_groups:
        keyboard.add(types.InlineKeyboardButton(group['name'], callback_data="handleSelectedGroup|" + str(group['_id'])))
    bot.send_message(message.from_user.id, "Select a group to view your profile.", reply_markup=keyboard)


def handleSelectedGroup(message: types.CallbackQuery,bot):
    data = message.data.split("|")

    selectedGroup = data[1]

    try:
        # get all the points of the user in the selected group
        images = DB['images'].find({"user_id": str(message.from_user.id), "group_id": selectedGroup})
        user_points = 0
        for image in images:
            user_points += image['points']
        print(user_points)

        formatted_text = f"""
<b>Community:</b> {DB['group'].find_one({"_id": int(selectedGroup)})['name']}
<b>Art Points:</b> {user_points}
<b>Referral Link:</b> https://t.me/{bot.get_me().username}?start={message.from_user.id}
        """
        bot.send_message(message.from_user.id, formatted_text, parse_mode="HTML")
    except ValueError:
        bot.send_message(message.from_user.id, "Invalid input. Please try again.")