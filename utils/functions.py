from telebot import types
from components.database import DB

def getGroups(bot,update,message,user_id):


    groups = DB['group'].find({"owner": user_id})

    if len(list(groups.clone())) == 0:
        bot.reply_to(message, "You are not the owner of any community.")
        return

    communities = []
    for group in groups:
        community_name = group["name"]
        community_id = group["_id"]
        community_info = f"{community_name} ({community_id})"
        communities.append(community_info)


    return communities