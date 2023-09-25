from telebot import types
from components.database import DB

def settings(message, bot):
    chat_id = message.chat.id
    groups = DB['group'].find({"owner": message.from_user.id})

    if len(list(groups.clone())) == 0:
        bot.reply_to(message, "You are not the owner of any community.")
        return

    communities = []
    for group in groups:
        community_name = group["name"]
        community_id = group["_id"]
        community_info = f"{community_name} ({community_id})"
        communities.append(community_info)
        

    reply_text = "List of owned communities:\n\n"
    for idx, community in enumerate(communities, 1):
        reply_text += f"{idx}. {community}\n"

    reply_text += "\nPlease select a community by entering its corresponding number or type 'cancel' to exit."
    markup = types.InlineKeyboardMarkup()
    for idx in range(1, len(communities) + 1):
        markup.add(types.InlineKeyboardButton(str(communities[idx - 1]), callback_data="handleSelectedCommunity|" + str(communities[idx - 1])))


    markup.add(types.InlineKeyboardButton("cancel", callback_data="handleSelectedCommunity_cancel"))

    bot.send_message(message.from_user.id, settingFormatCommunity(), reply_markup=markup, parse_mode="HTML")

def handleSelectedCommunity(message: types.CallbackQuery,bot):
    data = message.data.split("|")
    selectedCommunity = data[1].split(" ")[-1][1:-1]
    if selectedCommunity == 'ance':
        bot.send_message(message.from_user.id, "Action canceled.")
        return 

    try:
        manageCommunity(message, bot, selectedCommunity)

    except ValueError:
        bot.send_message(message.from_user.id, "Invalid input. Please try again.")


def settingFormatCommunity():
    return """
            <b> Please select the community you wish to set up the manga bot:</b>
           """


def manageCommunity(message, bot,selectedCommunity):
    chat_id = message.from_user.id
    # selectedCommunity = selectedCommunity.split(" ")[-1][1:-1]
    selectedCommunity=float(selectedCommunity)
    group_info = DB['group'].find_one({"_id": int(selectedCommunity)})

    if group_info is None:
        bot.reply_to(message, "This community is not registered. Please use /register to register your community.")
        return

    if group_info['owner'] != message.from_user.id:
        bot.reply_to(message, "You are not the owner of this community.")
        return


    # Create the inline keyboard for settings selection
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Remove this community", callback_data="removeCommunity_" + str(group_info['_id'])))

    bot.send_message(message.from_user.id, settingFormat(), reply_markup=markup, parse_mode="HTML")


def settingFormat():
    return """
           <b> Please select the option you wish to change:</b>
           """

def removeCommunity(message, bot):
    data = message.data.split("_")
    chat_id = data[1]
    #to int
    chat_id = int(chat_id)
    group_info = DB['group'].find_one({"_id": chat_id})

    if group_info is None:
        bot.send_message(message.from_user.id, "This community is not registered. Please use /register to register your community.")
        return

    if group_info['owner'] != message.from_user.id:
        bot.send_message(message.from_user.id, "You are not the owner of this community.")
        return

    DB['group'].delete_one({"_id": chat_id})
    bot.send_message(message.from_user.id, "Community removed successfully", reply_markup=types.ReplyKeyboardRemove())

def cancel(message, bot):
    bot.send_message(message.from_user.id, "Action canceled.")
    return