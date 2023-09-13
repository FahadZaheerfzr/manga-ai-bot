

def help(message, bot):
    """
    This function responds to the /help command

    Args:
        message (telebot.types.Message): The message object
        bot (telebot.TeleBot): The bot object
    
    Returns:
        None
    """
    bot.send_message(message.from_user.id, helpFormat(), parse_mode="HTML", disable_web_page_preview=True)

#format for the help command respose message
def helpFormat():
    """
    This function returns the format for the /help command response message

    Args:
        None
    """

    return """
🤖 <b>Bot Commands</b> 🤖

Here are the available commands and their descriptions:

/start - Start the bot.
/register - Register your community.
/img <i>prompt</i> - Generate an image based on the provided prompt.
/anime <i>prompt</i> - Generate an anime image based on the provided prompt.
/profile - View your profile and statistics, and generate an invite link.
/settings - Manage your community.
/help - View this help message.

<i>Usage:</i>
- For image prompts, use any text as the <i>prompt</i>.
- Use <code>/img mountain landscape</code> to generate an image of a mountain landscape.

<i>Note:</i>
- Replace <i>prompt</i> with your desired text.

Enjoy using the bot! 🚀
"""
