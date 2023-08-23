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

    print(group_id)
    # Check if the group is already in the database
    
    