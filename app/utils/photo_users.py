from telegram import Bot
from telegram.error import TelegramError


from dotenv import load_dotenv  # For loading environment variables from .env file
import os  # For accessing environment variables


load_dotenv()

async def get_user_profile_photo_link(user_id):
    bot_token = os.getenv("BOT_TOKEN")  # Retrieve the bot token from environment variables
    bot = Bot(token=bot_token)
    try:
        # Getting user profile photos
        photos = await bot.get_user_profile_photos(user_id=user_id)

        if photos.total_count > 0:
            # We receive the photo file
            file_id = photos.photos[0][0].file_id
            file = await bot.get_file(file_id)

            # Get a link to a photo file
            file_url = file.file_path

            print(f"Link to profile photo: {file_url}")
            return file_url
        else:
            print("The user has no profile photos.")
    except TelegramError as err:
        print(f"Error is: {err}")