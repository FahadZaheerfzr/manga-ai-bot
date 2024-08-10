from telebot import types
from components.database import DB
from utils.functions import getGroups


def settings(update, bot):
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

    if not communities:
        bot.send_message(send_id, "You have not registered any communities. Please use /register to register your community.")

    markup = types.InlineKeyboardMarkup()
    if (communities):
        for idx in range(1, len(communities) + 1):
            markup.add(types.InlineKeyboardButton(str(communities[idx - 1]), callback_data="handleSelectedCommunity|" + str(communities[idx - 1])))
    else:
        return

    markup.add(types.InlineKeyboardButton("cancel", callback_data="handleSelectedCommunity_cancel"))
    print(message.from_user.id, "message.from_user.id")
    bot.send_message(send_id, settingFormatCommunity(), reply_markup=markup, parse_mode="HTML")


def handleSelectedCommunity(message: types.CallbackQuery,bot):
    # delete last bot message 
    bot.delete_message(message.from_user.id, message.message.message_id)
    data = message.data.split("|")
    print(data)
    selected_data = data[1]
    if '(' in selected_data and ')' in selected_data:
        # Extract the chat ID from within the parentheses
        chat_id = selected_data.split('(')[-1].split(')')[0]
    else:
        # Treat the data directly as chat ID
        chat_id = selected_data
    # print (selectedCommunity, "selectedCommunity",data, "data")
        
    selectedCommunity = chat_id
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
    # print(selectedCommunity, "selectedCommunity")
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
    markup.add(types.InlineKeyboardButton("Language Preferences", callback_data="lang_" + str(group_info['_id'])))
    markup.add(types.InlineKeyboardButton("Notification Settings", callback_data="notifSettings_" + str(group_info['_id'])))
    markup.add(types.InlineKeyboardButton("Default Image Generation Preferences", callback_data="defaultImage_" + str(group_info['_id'])))
    markup.add(types.InlineKeyboardButton("Back", callback_data="settings_"))

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

def notifSettings(message, bot):
    data = message.data.split("_")
    chat_id = data[1]
    #to int
    chat_id = int(chat_id)
    group_info = DB['group'].find_one({"_id": chat_id})

    bot.delete_message(message.from_user.id, message.message.message_id)


    if group_info is None:
        bot.send_message(message.from_user.id, "This community is not registered. Please use /register to register your community.")
        return

    if group_info['owner'] != message.from_user.id:
        bot.send_message(message.from_user.id, "You are not the owner of this community.")
        return
    print(chat_id, "chat_id",group_info['_id'])
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Enable Notifications", callback_data="enableNotif_" + str(group_info['_id'])))
    markup.add(types.InlineKeyboardButton("Disable Notifications", callback_data="disableNotif_" + str(group_info['_id'])))
    markup.add(types.InlineKeyboardButton("Back", callback_data=f"handleSelectedCommunity|{chat_id}"))

    bot.send_message(message.from_user.id, notifSettingFormat(), reply_markup=markup, parse_mode="HTML")

def notifSettingFormat():
    return """
           <b> Please select the notification setting:</b>
           """

def enableNotif(message, bot):
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

    DB['group'].update_one(
        {"_id": int(chat_id)},
        {"$set": {"notif": True}},
        upsert=True
    )    
    bot.send_message(message.from_user.id, "Notification enabled successfully", reply_markup=types.ReplyKeyboardRemove())

def disableNotif(message, bot):
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

    DB['group'].update_one(
        {"_id": int(chat_id)},
        {"$set": {"notif": False}},
        upsert=True
    )    
    bot.send_message(message.from_user.id, "Notification disabled successfully", reply_markup=types.ReplyKeyboardRemove())

def defaultImage(message, bot):
    data = message.data.split("_")
    chat_id = data[1]
    #to int
    chat_id = int(chat_id)
    group_info = DB['group'].find_one({"_id": chat_id})
    bot.delete_message(message.from_user.id, message.message.message_id)

    if group_info is None:
        bot.send_message(message.from_user.id, "This community is not registered. Please use /register to register your community.")
        return

    if group_info['owner'] != message.from_user.id:
        bot.send_message(message.from_user.id, "You are not the owner of this community.")
        return

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Anime", callback_data="setDefaultImageAnime_" + str(group_info['_id'])))
    markup.add(types.InlineKeyboardButton("Image", callback_data="setDefaultImageNormal_" + str(group_info['_id'])))
    markup.add(types.InlineKeyboardButton("Back", callback_data=f"handleSelectedCommunity|{chat_id}"))

    bot.send_message(message.from_user.id, defaultImageFormat(), reply_markup=markup, parse_mode="HTML")

def defaultImageFormat():
    return """
           <b> Please select the default image generation preference:</b>
           """

def setDefaultImageNormal(message, bot):
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
    print(chat_id)
    DB['group'].update_one(
        {"_id": int(chat_id)},
        {"$set": {"default_image": "normal"}},
        upsert=True
    )  
    bot.send_message(message.from_user.id, "Default image generation preference set to 'Image' successfully", reply_markup=types.ReplyKeyboardRemove())

def setDefaultImageAnime(message, bot):
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

    DB['group'].update_one(
        {"_id": int(chat_id)},
        {"$set": {"default_image": "anime"}},
        upsert=True
    )    
    bot.send_message(message.from_user.id, "Default image generation preference set to 'Anime' successfully", reply_markup=types.ReplyKeyboardRemove())


