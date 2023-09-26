from telebot import types
from components.database import DB
import requests
from config import BACKEND_URL


# Dictionary to store user data temporarily
user_data_dict = {}
vote_initiators = {}
messages = {}
# Command handler for '/vote'
def vote(message: types.CallbackQuery,bot):
    # Create a unique identifier for this vote process
    # print (message.message.caption)
    vote_process_id = f"vote_{message.message.chat.id}"
    
    # Initialize user data for the vote process
    user_data_dict[vote_process_id] = {}
    vote_initiators[vote_process_id] = message.from_user.id
    originalMessage = message.message
    messages[message.from_user.id] = message.message
    
    # Reply to the user and instruct them to forward an image to dm
    # bot.send_message(message.from_user.id, "Please forward the image you want to vote for to me.")
    # bot.reply_to(originalMessage, "Please forward the image you want to vote for to me.")
    return handle_forwarded_image(message.message,message.from_user.id, message.from_user.username, vote_process_id, bot,originalMessage)
    # bot.register_next_step_handler(message.message, handle_forwarded_image, message.from_user.id, vote_process_id, bot,originalMessage)


def handle_vote_reply_message(message,bot,image_id):
    # Check if the received message is a reply to the specific message
        # get image id from the message
    # bot.register_next_step_handler(message, handle_twitter_link, message.reply_to_message.chat.id, bot,message.from_user.id)
    return handle_twitter_link(message, message.chat.id, bot,message.from_user.id, image_id)


def handle_twitter_link(message, vote_process_id, bot,fromUserId,image_id):
    # Extract the Twitter link from the user's message
    try:
        twitter_link = message.text
        # get message from messages dict
        originalMessage = messages[fromUserId]

        # get image and check if voted by user
        image=DB['images'].find_one({"id": image_id})
        #if the user has already voted, then return
        if fromUserId in image["votedBy"]:
            bot.reply_to(message, "You have already voted for this image.")
            return
            
        # validate link
        if twitter_link.startswith("https://twitter.com/") == False and twitter_link.startswith("https://x.com/") == False:
            # bot.reply_to(message, "Sorry, that doesn't look like a Twitter link. Please try again.")
            bot.send_message(fromUserId, "Sorry, that doesn't look like a Twitter link. Please try again.")
            return

        
        # Save the vote in the backend (you will need to implement this)
        success = add_vote_to_backend(image_id, twitter_link,fromUserId)
        group_chat_id = image["group_id"]
        if success:
            bot.reply_to(message, f'The vote has been recorded successfully!')
            bot.reply_to(originalMessage, f'{twitter_link}')
        else:
            bot.reply_to(message, "Sorry, there was an issue recording your vote. Please try again later.")
        
        # Clear user data for this vote process
        # del user_data_dict[vote_process_id]
        del messages[fromUserId]
    except Exception as e:
        print(e)
        bot.reply_to(message, "Please try clicking vote again as it's a one-time process.")
        return

def add_vote_to_backend(image_id, twitter_link,user_id):
    # Remove spaces before or after image_id
    
    # Add code here to save the vote in your backend
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




def handle_forwarded_image(message,fromUserId,username, vote_process_id, bot,originalMessage):
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
    bot.send_message(originalMessage.chat.id, f"Kindly check your dm to proceed with voting @{username}")
    bot.send_message(fromUserId, f"To continue voting, please upload the image to Twitter using the hashtag #Manga and mention @mangaaiofficial. Then, send the Twitter link as a response to this message.")
    # Save the image ID for later use
    user_data_dict[vote_process_id]['current_image_id'] = image_id
    # bot.register_next_step_handler(message, handle_vote_reply_message, bot, image_id)
    # Set the next step to handle the Twitter link if the same user sends another message
    # handle_twitter_link(message, vote_process_id, bot,fromUserId,originalMessage)
    bot.register_next_step_handler_by_chat_id(fromUserId, handle_twitter_link, vote_process_id, bot,fromUserId,image_id)
