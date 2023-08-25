from components.database import DB

def join_group(update, bot):
    """
    This function responds when a user joins a group

    Args:
        message (telebot.types.Message): The message object
        bot (telebot.TeleBot): The bot object
    
    Returns:
        None
    """
    # Get the group ID
    try:
        if update.invite_link is not None:
            print(update.invite_link.creator.first_name)
    except Exception as e:
        print(e)



    
    