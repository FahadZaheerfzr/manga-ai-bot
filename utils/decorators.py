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

def cancelable(func):
    @wraps(func)
    def wrapper(message, *args, **kwargs):
        # Try to extract bot from kwargs first
        bot = kwargs.get('bot')
        
        if not bot:
            bot = next((arg for arg in args if hasattr(arg, 'send_message')), None)

        if message.text.lower() == "cancel" or message.text.lower() == "/cancel":
            if bot:  # Ensure bot is not None
                bot.send_message(message.chat.id, "Cancelled.")
            return
        return func(message, *args, **kwargs)
    return wrapper
