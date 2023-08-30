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
            user_id = update.invite_link.name
            print(update)
            # Check if the user has already referred
            referral = DB['referral'].find_one({"referral_id": user_id, user_id:update.from_user.id })
            print(referral)
            if referral is None:
                # Confirm if the sender is the member of the group
                try:
                    result = bot.get_chat_member(update.chat.id, update.from_user.id)
                    if result.status != "left":
                        # Add the referral
                        DB['referral'].insert_one({"referral_id": user_id, "user_id": update.from_user.id})
                except Exception as e:
                    print(e)
                    pass
    except Exception as e:
        print(e)
        pass



    
    