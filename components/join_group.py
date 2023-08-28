
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
            bot.send_message(update.chat.id, "Welcome to the group! Looks like you were invited by someone. Please enter the referral code of the person who invited you using <b>/referral: {code}</b> to help them earn more points.", parse_mode="HTML")
    except Exception as e:
        print(e)



    
    