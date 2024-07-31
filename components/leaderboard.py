from telebot import types
from components.database import DB

def get_group_users_points(group_id):
    """
    Fetches and returns a dictionary of user IDs and their points for a specific group.
    """
    users_points = {}
    images = DB['images'].find({"group_id": group_id})
    
    for image in images:
        user_id = image['user_id']
        if user_id not in users_points:
            users_points[user_id] = 0
        users_points[user_id] += image['points']
    
    return users_points

def get_leaderboard(group_id, top_n=5):
    """
    Fetches the top N users with the highest points in a specific group.
    """
    users_points = get_group_users_points(group_id)
    sorted_users = sorted(users_points.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return sorted_users

def handle_leaderboard_command(message, bot):
    """
    Handles the /leaderboard command and displays the top users with the highest points in the group.
    """
    if message.chat.type != 'supergroup' and message.chat.type != 'group':
        bot.reply_to(message, "This command can only be used in a group.")
        return
    
    group_id = message.chat.id
    top_users = get_leaderboard(group_id)
    
    if not top_users:
        bot.send_message(group_id, "No points data available.")
        return
    
    leaderboard_text = "🏆 *Leaderboard:* 🏆\n\n"
    for index, (user_id, points) in enumerate(top_users):
        user = bot.get_chat_member(group_id, user_id)
        username = user.user.username if user.user.username else f"User {user.user.id}"
        leaderboard_text += f"{index + 1}. {username} - {points} points\n"
    
    bot.send_message(group_id, leaderboard_text, parse_mode="Markdown")
