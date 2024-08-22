from telebot import types
from components.database import DB
from datetime import datetime
from bson import ObjectId
from utils.functions import checkIfAdmin
def get_active_campaign(community_id):
    """
    Retrieve the active campaign for a given community.
    
    Parameters:
        community_id (int): The ID of the community.
        
    Returns:
        dict: The active campaign document if found, otherwise None.
    """
    campaigns = DB['campaigns'].find({"community_id": int(community_id)})
    for campaign in campaigns:
        ended = campaign.get("ended", False)
        end_date = datetime.strptime(campaign["end_date"], "%Y-%m-%d").date()
        if end_date > datetime.now().date() and not ended:
            return campaign
    return None

def create_poll(update, bot):
    """
    Create a poll with all images of the currently active campaign.
    """
    try:
        if isinstance(update, types.Message):
            message = update
            chat_id = message.chat.id
            user_id = message.from_user.id
        elif isinstance(update, types.CallbackQuery):
            message = update.message
            chat_id = message.chat.id
            user_id = update.from_user.id

        # can only be used in group
        if message.chat.type == 'private':
            bot.reply_to(message, "This command can only be used in a group.")
            return

        # get the active campaign
        active_campaign = get_active_campaign(chat_id)
        if not active_campaign:
            bot.reply_to(message, "No active campaign found in this community.")
            return
        if not checkIfAdmin(bot, chat_id, user_id):
            bot.reply_to(message, "You must be an admin to create a poll.")
            return
        # if poll already exists, do not create a new one
        poll_data = DB['polls'].find_one({"campaign_id": active_campaign["_id"], "community_id": chat_id})
        if poll_data:
            bot.reply_to(message, "A poll is already active for this campaign.")
            return
        
        images = DB['images'].find({
            "campaign_id": str(active_campaign["_id"]),
            "$or": [
                {"disqualified": {"$exists": False}},
                {"disqualified": False}
            ]
        })
                
        
        # create the poll
        poll = bot.send_poll(chat_id, "Cast your vote for the images", [image["id"] for image in images], is_anonymous=False, allows_multiple_answers=False)
        # save the poll ID in the database
        images = list(DB['images'].find({"campaign_id": str(active_campaign["_id"])}))
        if not images:
            bot.reply_to(message, "No images found for this campaign.")
            return
        if len(images) < 2:
            bot.reply_to(message, "At least 2 images are required to create a poll.")
            return
        pollOptions = []
        for image in images:
            print (image["id"])
            pollOptions.append({"id": image["id"]} )
        DB['polls'].insert_one({"_id": poll.poll.id, "campaign_id": active_campaign["_id"], "user_id": user_id, "community_id": chat_id,"poll_message_id": poll.message_id, "poll_options": pollOptions})
    except Exception as e:
        print(e)
        bot.reply_to(message, "Make sure there are atleast two images in the campaign to create a poll.")

from datetime import datetime, timedelta

def handle_poll(poll_answer, bot, required_points=100):
    """
    Handles poll answers and stores the result in the database.
    """
    user_id = poll_answer.user.id
    poll_id = poll_answer.poll_id
    option_ids = poll_answer.option_ids  # List of selected option indices

    # Check if the user has the required points
    user_points = get_user_points(user_id)
    if user_points < required_points:
        bot.send_message(user_id, f"You need at least {required_points} points to participate in this poll. You currently have {user_points} points.")
        return

    # Find the corresponding poll in the database
    poll_data = DB['polls'].find_one({"_id": poll_id})
    if poll_data:
        # Check if the user has already voted today
        today = datetime.now().date()
        last_vote = DB['user_votes'].find_one({"user_id": user_id, "poll_id": poll_id})

        if last_vote:
            last_vote_date = last_vote.get("date")
            last_vote_date = datetime.strptime(last_vote_date, "%Y-%m-%d").date()
            if last_vote_date == today:
                bot.send_message(user_id, "You have already voted today. Please come back tomorrow.")
                return

        # Update the poll results
        for option_id in option_ids:
            image_id = poll_data["poll_options"][option_id]["id"]
            image = DB['images'].find_one({"id": image_id})
            if image:
                DB['images'].update_one({"id": image_id}, {"$inc": {"points": 5, "votes": 1}})
        
        # Record the user's vote
        DB['user_votes'].insert_one({"user_id": user_id, "poll_id": poll_id, "date": str(today)})


def get_user_points(user_id,sendAll=False,group_id=None):
    # we need to check all images of user , referrals in user_referral, project_referral and also daily rewards

    print(user_id)
    user_points = 0
    user = DB['botUsers'].find_one({"user_id": int(user_id)})
    rewardPoints=0
    if user:
        user_points = user.get("points", 0)
    # check images
    image_points = 0
    if group_id:
        images = DB['images'].find({
            "user_id": str(user_id),
            "group_id": str(group_id),
            "$or": [
                {"disqualified": {"$exists": False}},
                {"disqualified": False}
            ]
        })
    else:
        images = DB['images'].find({
        "user_id": str(user_id),
        "$or": [
            {"disqualified": {"$exists": False}},
            {"disqualified": False}
        ]
    })
    for image in images:
        user_points += image['points']
        image_points += image['points']

    # check user_referrals
    referral_points = 0
    user_referrals = DB['user_referrals'].find({
        "$or": [
            {"user_id": int(user_id)},
            {"referral_id": int(user_id)}
        ]
    })
    for referral in user_referrals:
        user_points += referral['points']
        referral_points += referral['points']

    # check project_referrals
    project_referralPoints = 0
    project_referrals = DB['project_referral'].find({
        "$or": [
            {"referrer_id": int(user_id)},
            {"user_id": int(user_id)}
        ]
    })
    for referral in project_referrals:
        user_points += referral['points']
        project_referralPoints += referral['points']

    # check daily_rewards
    daily_reward = DB['daily_rewards'].find_one({"user_id": int(user_id)})
    if daily_reward:
        user_points += daily_reward['points']
        rewardPoints=daily_reward['points']

    if sendAll:
        return user_points, image_points, referral_points, project_referralPoints, rewardPoints
    return user_points
        