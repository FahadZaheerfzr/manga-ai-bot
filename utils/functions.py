from telebot import types
from components.database import DB
import re

def getGroups(bot, update, message, user_id):
    groups = DB['group'].find()

    communities = []
    for group in groups:
        group_id = group["_id"]

        try:
            # Check if the user is an admin in the group
            chat_member = bot.get_chat_member(chat_id=group_id, user_id=user_id)
            if chat_member.status in ['administrator', 'creator']:
                community_name = group["name"]
                community_info = f"{community_name} ({group_id})"
                communities.append(community_info)
        except Exception as e:
            # Handle cases where the bot might not be in the group or another error occurs
            continue

    return communities


def checkIfAdmin(bot,chat_id,user_id):
    chat_member = bot.get_chat_member(chat_id, user_id)
    return chat_member.status == 'administrator' or chat_member.status == 'creator'

def escape_markdown(text):
    escape_chars = r'\*_`\['
    return re.sub(f'([{escape_chars}])', r'\\\1', text)