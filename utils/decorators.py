from functools import wraps
import telebot

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