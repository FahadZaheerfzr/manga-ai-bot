from components.database import DB


def referral(message, bot):
    if message.chat.type == "private":
        bot.reply_to(message, "This command is only available in groups.")
        return
    try:
      referral_id = message.text.split(" ", 1)[1]
    except:
      bot.reply_to(message, "Seems like you are using command in an incorrect way. Please try /referral <code>.")
      return
    
    # Check if the user has already used a referral code
    referral = DB['referral'].find_one({"user_id": message.from_user.id})
    if referral is not None:
        bot.reply_to(message, "You have already used this referral code.")
        return
    
    # Check if the referral code is valid
    try:
        result = bot.get_chat_member(message.chat.id, referral_id)
        if result.status == "left":
          bot.reply_to(message, "Invalid referral code.")
          return
        DB['referral'].insert_one({
            "user_id": message.from_user.id,
            "referral_id": referral_id,
            "chat_id": message.chat.id,
        })
        bot.reply_to(message, "Referral code added successfully.")
    except Exception as e:
        print(e)
        bot.reply_to(message, "Invalid referral code.")
