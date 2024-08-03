from telebot import types
from components.database import DB
from datetime import datetime, timedelta

def get_reward_points(streak_length):
    initialPoints=10
    return initialPoints * (streak_length)

def daily_reward(message, bot):
    """
    Handles the /daily command to give a daily reward to the user.
    """
    user_id = message.from_user.id
    group_id = message.chat.id
    user = bot.get_chat_member(group_id, user_id)
    
    if user.status == "left":
        bot.reply_to(message, "You must be a member of the group to claim the daily reward.")
        return
    
    today = datetime.now().date()
    daily_reward = DB['daily_rewards'].find_one({"user_id": user_id, "group_id": group_id})
    print(daily_reward, "daily_reward")
    if daily_reward:
        last_claimed_date = daily_reward["date_claimed"]
        streak_length = daily_reward.get("streak_length", 0)
        # convert date_claimed string to date
        last_claimed_date = datetime.strptime(last_claimed_date, "%Y-%m-%d").date()
        # Check if the user skipped a day
        if last_claimed_date < today - timedelta(days=1):
            streak_length = 0  # Break the streak if a day is skipped
        
        if last_claimed_date == today:
            bot.reply_to(message, "You have already claimed the daily reward today.")
            return
        
        # Increment streak length and update points
        streak_length += 1
        reward_points = get_reward_points(streak_length)

        # Update the daily reward document
        DB['daily_rewards'].update_one(
            {"_id": daily_reward["_id"]},
            {
                "$set": {"date_claimed": str(today), "streak_length": streak_length},
                "$inc": {"points": reward_points}
            }
        )
    else:
        # Insert a new record with initial streak length
        streak_length = 1
        reward_points = get_reward_points(streak_length)
        
        DB['daily_rewards'].insert_one({
            "user_id": user_id,
            "group_id": group_id,
            "date_claimed": str(today),
            "points": reward_points,
            "streak_length": streak_length
        })

    bot.reply_to(message, f"You have claimed your daily reward of {reward_points} points!")
