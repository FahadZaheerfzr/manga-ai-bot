from telebot import types
from components.database import DB
import re

def getGroups(bot,update,message,user_id):


    groups = DB['group'].find({"owner": user_id})


    communities = []
    for group in groups:
        community_name = group["name"]
        community_id = group["_id"]
        community_info = f"{community_name} ({community_id})"
        communities.append(community_info)


    return communities

def checkIfAdmin(bot,chat_id,user_id):
    chat_member = bot.get_chat_member(chat_id, user_id)
    return chat_member.status == 'administrator' or chat_member.status == 'creator'

def escape_markdown(text):
    escape_chars = r'\*_`\['
    return re.sub(f'([{escape_chars}])', r'\\\1', text)