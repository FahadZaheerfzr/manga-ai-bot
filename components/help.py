

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
/img <i>prompt</i> - Generate an image based on the provided prompt (default depending on settings).
/anime <i>prompt</i> - Generate an anime image based on the provided prompt.
/normal <i>prompt</i> - Generate an image based on the provided prompt (non-anime).
/profile - View your profile and statistics, and generate an invite link.
/settings - Manage your community.
/help - View this help message.

<b>Image Generation</b>
/img <i>prompt</i> - Generate an image based on the provided prompt.
- <i>Example:</i> <code>/img mountain landscape</code> to generate an image of a mountain landscape.
/anime <i>prompt</i> - Generate an anime image based on the provided prompt.
- <i>Example:</i> <code>/anime sunset over a city</code> to generate an anime-style image of a sunset over a city.
/normal <i>prompt</i> - Generate an image based on the provided prompt (non-anime).

<b>Leaderboard</b>
/leaderboard - View the top 5 users with the highest points in this group.

<b>Points and Leaderboard</b>
/points - Check your points in the current group or across all groups.

<b>Guide</b>
1. <b>Starting the Bot</b>
- Use the /start command to initiate interaction with the bot.
- Follow the instructions to register your community if you haven't already.

2. <b>Registering Your Community</b>
- Use the /register command to register your community.
- Make sure your community is set to enable the point system.

3. <b>Generating Images</b>
- Use the /img or /anime commands followed by your prompt to generate images.
- Experiment with different prompts to get the best results.

4. <b>Managing Your Profile and Settings</b>
- Use the /profile command to view your profile and statistics.
- Use the /settings command to manage community settings like enabling the point system.

5. <b>Viewing the Leaderboard</b>
- Use the /leaderboard command to see the top 5 users with the highest points in the current group.
- This command only works inside a group where the point system is enabled.

6. <b>Earning Points through user referrals</b>
- Use the /user_referral command to get your referral link.
- Share your referral link with others to earn points when they register.

7. <b>Earning Points through project referrals</b>
- Use the /project_referral command to get your project referral link.
- Share your project referral link with others to earn points when they register their project with their community.

<i>Tips and Best Practices:</i>
- Be specific with your image prompts for better results.
- Engage with your community and earn points by participating and contributing.
- Use the invite link generated in your profile to invite friends and earn referral points.

Enjoy using the bot and make the most out of its features! 🚀
"""
