from functools import wraps
import telebot
from components.database import DB

def admin_only(bot):
    def decorator(func):
        @wraps(func)
        def wrapper(message, *args, **kwargs):
            try:
                # Get chat administrators
                admins = bot.get_chat_administrators(message.chat.id)
                admin_ids = [admin.user.id for admin in admins]

                # Check if the user is an admin
                if message.from_user.id not in admin_ids:
                    bot.reply_to(message, "You don't have permission to use this command.")
                    return

                # Call the original function if the user is an admin
                return func(message, *args, **kwargs)
            except Exception as e:
                bot.reply_to(message, f"Failed to check admin status: {e}")
                return
        return wrapper
    return decorator

def cancelable(func):
    @wraps(func)
    def wrapper(message, *args, **kwargs):
        # Try to extract bot from kwargs first
        bot = kwargs.get('bot')
        
        if not bot:
            bot = next((arg for arg in args if hasattr(arg, 'send_message')), None)

        if not message.photo:
            if message.text.lower() == "cancel" or message.text.lower() == "/cancel":
                if bot:  # Ensure bot is not None
                    bot.send_message(message.chat.id, "Cancelled.")
                return
        return func(message, *args, **kwargs)
    return wrapper


def profile_complete(func):
    @wraps(func)
    def wrapper(message, bot, *args, **kwargs):
        user = DB['botUsers'].find_one({"user_id": message.from_user.id})
        if user:
            # Check that all required fields exist and are not empty
            required_fields = ["wallet", "email", "twitter"]
            for field in required_fields:
                if field not in user or not user[field]:
                    bot.reply_to(message, f"Your {field} is missing or empty. Please complete your profile by sending /profile")
                    return
        else:
            bot.reply_to(message, "User not found.")
            return
        return func(message, bot, *args, **kwargs)
    return wrapper