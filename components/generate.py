from telebot import types
from components.ai.stability import generate_text_to_image, non_anime_image
from config import BACKEND_URL
import datetime
import requests
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
from components.database import DB
from utils.logger import setup_logger

def generate(message,bot):
    """
    This function responds to the /generate command

    Args:
        message (telebot.types.Message): The message object
        bot (telebot.TeleBot): The bot object
    
    Returns:
        None
    """ 
    try:
        image_generation_logger=setup_logger("image_generation")
        image_generation_logger.info(f"User {message.from_user.id} requested to generate an image.")
        group = DB['group'].find_one({"_id": message.chat.id})
        if group is None and message.chat.type != "private":
            image_generation_logger.info(f"User {message.from_user.id} is not in a group.")
            bot.reply_to(message, "This group is not registered.")
            return
        image_generation_logger.info(f"User {message.from_user.id} is in group {message.chat.id}.")
        image_responses = requests.get(BACKEND_URL+"/image/user/"+str(message.from_user.id))
        image_generation_logger.info(f"User {message.from_user.id} has generated {len(image_responses.json())} images today.")
        # Get the number of images generated by the user where created_at is today
        image_count = 0
        for image in image_responses.json():
            if image["created_at"].split(" ")[0] == str(datetime.date.today()):
                image_count += 1
        # calculate time left until the end of the day
        time_left = datetime.datetime.combine(datetime.date.today(), datetime.time.max) - datetime.datetime.now()

        limit = 3
        try:
          if DB['members'].find_one({"username": message.from_user.username}) is not None:
                limit = 10
        except:
            pass

        if image_count >= limit:
            bot.reply_to(message, "You have reached the maximum number of images you can generate for today. Please try again in " + (str(time_left).split(".")[0]).split(":")[0] + " hours and " + (str(time_left).split(".")[0]).split(":")[1] + " minutes.")
            return
        try:
            prompt = message.text.split(" ", 1)[1]
            print(prompt)
        except:
            bot.reply_to(message, "The structure of the command is incorrect. Please try /img <prompt>.")
            return
        if message.from_user.username is None:
            username = message.from_user.first_name + " " + message.from_user.last_name
        else:
            username = message.from_user.username

        params = {
            "prompt": prompt,
            "name":username,
            "user_id": message.from_user.id,
            "group_id": message.chat.id,
        }
        image_file_path = "v1_txt2img_0.png"
        try:
            bot.reply_to(message, "Generating image...")
            generate_text_to_image(prompt)
        except Exception as e:
            print(e)
            image_generation_logger.error(f"User {message.from_user.id} encountered an error while generating an image, {e}")
            bot.reply_to(message, "You have entered an invalid prompt. Please try again.")
            return
        with open(image_file_path, "rb") as image_file:
            files = {
                "image_file": (image_file_path, image_file, "image/png")
            }
            response = requests.post(BACKEND_URL+"/images", params=params, files=files)
        image = Image.open(image_file_path)
        watermark = Image.open("image/watermark.png")
        image.paste(watermark, (0, 0), watermark)
        image.save(image_file_path)
        ads_string = """"""
        sponsored_ads = """"""
        if group is None:
            ads_string = "<a href='https://t.me/Roburna'>Roburna Blockchain</a>"
            sponsored_ads = """"""

        if group is not None:
            if group["common_ads"] is []:
                ads_string = "<a href='https://t.me/Roburna'>Roburna Blockchain</a>"

            if group["sponsored_ads"] is []:
                sponsored_ads = ""

            for ad in group["common_ads"]:
                ads_string += f'<a href="{ad["link"]}">{ad["name"]}</a> | '
        
            for ad in group["sponsored_ads"]:
                sponsored_ads += f'<a href="{ad["link"]}">{ad["name"]}</a> | '
        


        caption = f"""
Image ID: {response.json()["id"]} \n
Image generated by <code>{username}</code>: (prompt used) <code>{prompt}</code> \n
Ad: {ads_string} \n
Sponsored Ad: {sponsored_ads}\n
&gt; <a href='https://t.me/mangaaiofficial'>Join MangaAI</a> | <a href='https://mangaai.org/'>Website</a> &lt;
        """
        reply2_keyboard = [
            [types.InlineKeyboardButton("Vote", callback_data="vote_")],
        ]

# Create the inline keyboard markup
        markup1 = types.InlineKeyboardMarkup(reply2_keyboard)

        #check db to check if voting is enabled in group
        group = DB['group'].find_one({"_id": message.chat.id})
        if group is not None:
            if group["voting_system"] is True:
                bot.send_photo(
                    message.chat.id,
                    photo=open('v1_txt2img_0.png', 'rb'),
                    caption=caption,
                    parse_mode='HTML',
                    reply_markup=markup1
                )
                return
            else:
                bot.send_photo(message.chat.id, photo=open('v1_txt2img_0.png', 'rb'), caption=caption, parse_mode='HTML')
                return
        else:
            bot.send_photo(message.chat.id, photo=open('v1_txt2img_0.png', 'rb'), caption=caption, parse_mode='HTML')
            return
    except Exception as e:
        image_generation_logger.error(f"User {message.from_user.id} encountered an error while generating an image, {e}")
        bot.reply_to(message, "An error occurred while generating the image. Please try again.")
        return
    
def generate_image(message,bot):
    """
    This function responds to the /generate command

    Args:
        message (telebot.types.Message): The message object
        bot (telebot.TeleBot): The bot object
    
    Returns:
        None
    """ 
    try:
        image_generation_logger=setup_logger("image_generation")
        image_generation_logger.info(f"User {message.from_user.id} requested to generate an image.")
        group = DB['group'].find_one({"_id": message.chat.id})
        if group is None and message.chat.type != "private":
            image_generation_logger.info(f"User {message.from_user.id} is not in a group.")
            bot.reply_to(message, "This group is not registered.")
            return
        image_generation_logger.info(f"User {message.from_user.id} is in group {message.chat.id}.")
        image_responses = requests.get(BACKEND_URL+"/image/user/"+str(message.from_user.id))
        image_generation_logger.info(f"User {message.from_user.id} has generated {len(image_responses.json())} images today.")
        # Get the number of images generated by the user where created_at is today
        image_count = 0
        for image in image_responses.json():
            if image["created_at"].split(" ")[0] == str(datetime.date.today()):
                image_count += 1
        # calculate time left until the end of the day
        time_left = datetime.datetime.combine(datetime.date.today(), datetime.time.max) - datetime.datetime.now()
        # check username with members table in db
        # if user is member, then allow to generate 5 images
        # if user is not member, then allow to generate 3 images

        limit = 3
        try:
          if DB['members'].find_one({"username": message.from_user.username}) is not None:
                limit = 10
        except:
            pass

        if image_count >= limit:
            bot.reply_to(message, "You have reached the maximum number of images you can generate for today. Please try again in " + (str(time_left).split(".")[0]).split(":")[0] + " hours and " + (str(time_left).split(".")[0]).split(":")[1] + " minutes.")
            return
        try:
            prompt = message.text.split(" ", 1)[1]
            print(prompt)
        except:
            bot.reply_to(message, "The structure of the command is incorrect. Please try /img <prompt>.")
            return
        
        if message.from_user.username is None:
            username = message.from_user.first_name + " " + message.from_user.last_name
        else:
            username = message.from_user.username
        params = {
            "prompt": prompt,
            "name":username,
            "user_id": message.from_user.id,
            "group_id": message.chat.id,
        }
        image_file_path = "v1_txt2img_0.png"
        try:
            bot.reply_to(message, "Generating image...")
            non_anime_image(prompt + ". The image should not include any anime characters.")
        except Exception as e:
            print(e)
            image_generation_logger.error(f"User {message.from_user.id} encountered an error while generating an image, {e}")
            bot.reply_to(message, "You have entered an invalid prompt. Please try again.")
            return
        with open(image_file_path, "rb") as image_file:
            files = {
                "image_file": (image_file_path, image_file, "image/png")
            }
            response = requests.post(BACKEND_URL+"/images", params=params, files=files)
            print(response.json())
        image = Image.open(image_file_path)
        watermark = Image.open("image/watermark.png")
        image.paste(watermark, (0, 0), watermark)
        image.save(image_file_path)
        ads_string = """"""
        sponsored_ads = """"""
        if group is None:
            ads_string = "<a href='https://t.me/Roburna'>Roburna Blockchain</a>"
            sponsored_ads = """"""

        if group is not None:
            if group["common_ads"] is []:
                ads_string = "<a href='https://t.me/Roburna'>Roburna Blockchain</a>"

            if group["sponsored_ads"] is []:
                sponsored_ads = ""

            for ad in group["common_ads"]:
                ads_string += f'<a href="{ad["link"]}">{ad["name"]}</a> | '
        
            for ad in group["sponsored_ads"]:
                sponsored_ads += f'<a href="{ad["link"]}">{ad["name"]}</a> | '
        


        caption = f"""
Image ID: {response.json()["id"]} \n
Image generated by <code>{username}</code>: (prompt used) <code>{prompt}</code> \n
Ad: {ads_string} \n
Sponsored Ad: {sponsored_ads}\n
&gt; <a href='https://t.me/mangaaiofficial'>Join MangaAI</a> | <a href='https://mangaai.org/'>Website</a> &lt;
        """
        reply2_keyboard = [
            [types.InlineKeyboardButton("Vote", callback_data="vote_")],
        ]

# Create the inline keyboard markup
        markup1 = types.InlineKeyboardMarkup(reply2_keyboard)

        #check db to check if voting is enabled in group
        group = DB['group'].find_one({"_id": message.chat.id})
        if group is not None:
            if group["voting_system"] is True:
                bot.send_photo(
                    message.chat.id,
                    photo=open('v1_txt2img_0.png', 'rb'),
                    caption=caption,
                    parse_mode='HTML',
                    reply_markup=markup1
                )
                return
            else:
                bot.send_photo(message.chat.id, photo=open('v1_txt2img_0.png', 'rb'), caption=caption, parse_mode='HTML')
                return
        else:
            bot.send_photo(message.chat.id, photo=open('v1_txt2img_0.png', 'rb'), caption=caption, parse_mode='HTML')
            return



    except Exception as e:
        print(e)
        image_generation_logger.error(f"User {message.from_user.id} encountered an error while generating an image, {e}")
        bot.reply_to(message, "An error occurred while generating the image. Please try again.")
        return
