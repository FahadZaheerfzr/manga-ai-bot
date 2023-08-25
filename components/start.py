

def start(message, bot):
    """
    This function responds to the /start command

    Args:
        message (telebot.types.Message): The message object
        bot (telebot.TeleBot): The bot object
    
    Returns:
        None
    """
    bot.send_message(message.from_user.id, startFormat(), parse_mode="HTML", disable_web_page_preview=True)

#format for the start command respose message
def startFormat():
    """
    This function returns the format for the /start command response message

    Args:
        None
    """

    return """
Hi! I'm <b>MangaAI Bot</b>. Let's get started: \n
 
Please note, I am in beta version, so errors, issues, and omissions are possible! \n

<code>Created by Roburna Network</code>
           """
