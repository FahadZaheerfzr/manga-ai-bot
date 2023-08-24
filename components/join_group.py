from components.database import DB

def join_group(message, bot):
    """
    This function responds when a user joins a group

    Args:
        message (telebot.types.Message): The message object
        bot (telebot.TeleBot): The bot object
    
    Returns:
        None
    """
    # Get the group ID
    group_id = message.chat.id

    # Check if the group is registered
    group = DB['group'].find_one({"_id": group_id})
    if group is None:
        return
    
    if group['point_system']:
        DB['user_points'].insert_one({
            "_id": message.from_user.id,
            "group_id": group_id,
            "art_points": 0,
            "referral_points": 0,
        })
        bot.send_message(message.from_user.id, "You have been registered to the point system. You can earn points by minting images and referring users. Use /profile to check your points.")

    
    