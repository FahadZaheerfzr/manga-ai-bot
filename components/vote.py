from telebot import types
from components.database import DB
import requests
from config import BACKEND_URL


# Dictionary to store user data temporarily
user_data_dict = {}
vote_initiators = {}
# Command handler for '/vote'
def vote(message: types.CallbackQuery,bot):
    # Create a unique identifier for this vote process
    # print (message.message.caption)
    vote_process_id = f"vote_{message.message.chat.id}"
    
    # Initialize user data for the vote process
    user_data_dict[vote_process_id] = {}
    vote_initiators[vote_process_id] = message.from_user.id
    originalMessage = message.message
    # Reply to the user and instruct them to forward an image to dm
    # bot.send_message(message.from_user.id, "Please forward the image you want to vote for to me.")
    print(vote_process_id,"the vote process id")
    handle_forwarded_image(message.message,message.from_user.id, vote_process_id, bot,originalMessage)
    # bot.register_next_step_handler(message.message, handle_forwarded_image, message.from_user.id, vote_process_id, bot,originalMessage)


def handle_forwarded_image(message,fromUserId, vote_process_id, bot,originalMessage):
    # Extract the image ID from the forwarded message
    #print the text after Image ID: in the caption
    image_id = message.caption.split("Image ID: ")[1]
    #now remove everything after the image id
    image_id = image_id.split("\n")[0]
    image_id = image_id.strip()

    #check votedBy and see if the user has already voted
    image=DB['images'].find_one({"id": image_id})
    #if the user has already voted, then return

    #check if the group of the image has voting enabled
    groupID= int (image["group_id"])
    group = DB['group'].find_one({"_id": groupID})
    print (group)

    if group is None:
        bot.reply_to(message, "This image wasn't part of any group")
        return
    
    if group["voting_system"] == False:
        bot.reply_to(message, "Voting is not enabled for this group.")
        return
    
    if fromUserId in image["votedBy"]:
        bot.reply_to(message, "You have already voted for this image.")
        return
    
    # Ask the user to provide the Twitter link
    # bot.reply_to(message, "Great! Now, please send the Twitter link of the post associated with this image.")
    bot.send_message(fromUserId, f"Great! Now, please reply to this message with the Twitter link of the post associated with the image: {image_id}")
    # Save the image ID for later use
    user_data_dict[vote_process_id]['current_image_id'] = image_id
    
    return
    # Set the next step to handle the Twitter link if the same user sends another message
    # handle_twitter_link(message, vote_process_id, bot,fromUserId,originalMessage)
    # bot.register_next_step_handler(message, handle_twitter_link, vote_process_id, bot,fromUserId,originalMessage)


def handle_vote_reply_message(message,bot):
    # Check if the received message is a reply to the specific message
    if (
        message.reply_to_message is not None
        and message.reply_to_message.text.startswith("Great! Now, please reply to this message with the Twitter link of the post associated with the image:")
    ):
        # get image id from the message
        image_id = message.reply_to_message.text.split("image: ")[1]
        # bot.register_next_step_handler(message, handle_twitter_link, message.reply_to_message.chat.id, bot,message.from_user.id)
        handle_twitter_link(message, message.reply_to_message.chat.id, bot,message.from_user.id,image_id)
    else:
        pass

def handle_twitter_link(message, vote_process_id, bot,fromUserId,image_id):
    # Extract the Twitter link from the user's message
    print ("here")
    twitter_link = message.text

    # get image and check if voted by user
    image=DB['images'].find_one({"id": image_id})
    #if the user has already voted, then return
    if fromUserId in image["votedBy"]:
        bot.reply_to(message, "You have already voted for this image.")
        return
        
    # validate link
    if twitter_link.startswith("https://twitter.com/") == False:
        # bot.reply_to(message, "Sorry, that doesn't look like a Twitter link. Please try again.")
        bot.send_message(fromUserId, "Sorry, that doesn't look like a Twitter link. Please try again.")
        return

    
    # Save the vote in the backend (you will need to implement this)
    success = add_vote_to_backend(image_id, twitter_link,fromUserId)
    group_chat_id = image["group_id"]
    if success:
        bot.send_message(group_chat_id, "Your vote has been recorded successfully!")
    else:
        bot.reply_to(message, "Sorry, there was an issue recording your vote. Please try again later.")
    
    # Clear user data for this vote process
    # del user_data_dict[vote_process_id]

def add_vote_to_backend(image_id, twitter_link,user_id):
    # Remove spaces before or after image_id
    
    # Add code here to save the vote in your backend
    print(image_id, twitter_link)
    #we will do it directly to db
    #get the image from db
    try:
        images = DB['images'].find_one({"id": image_id})
        #get the votes
        votes = images["votes"]
        #add the new vote
        votes+=1
        #update the db with votes and userid append to list votedBy
        DB['images'].update_one({"id": image_id}, {"$set": {"votes": votes}, "$push": {"votedBy": user_id}})

        return True
    except Exception as e:
        print(e)
        return False

