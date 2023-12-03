from telegram import Update, ChatMember
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram.error import Unauthorized
import uuid
from urllib.parse import quote  # Import the quote function for URL encoding

# Replace 'YOUR_TOKEN' with the actual token from BotFather
TOKEN = '6712317648:AAHLTcfbYhrdcPYt4A6poC6itZWW_5zXTpI'

# Replace 'ADMIN_CHAT_ID' with your admin chat ID
ADMIN_CHAT_ID = '5447083924'

# Replace 'CHANNEL_1_ID' with the ID of Channel 1 (where users need to subscribe)
CHANNEL_1_ID = '-1002143630143'

# Replace 'CHANNEL_2_ID' with the ID of Channel 2 (where new content is uploaded)
CHANNEL_2_ID = '-1002098991271'

# Dictionary to map content file IDs to content start links
content_links = {}

def start(update: Update, context: CallbackContext):
    print("Start function called!")
    user_id = update.message.from_user.id

    # Check if the user is a subscriber or admin of Channel 1
    if is_subscriber(user_id, context.bot):
        # Check if the command has arguments
        if context.args:
            content_file_id = context.args[0]
        elif context.match:
            # If there is no argument, check if it's a start link
            content_file_id = context.match.group(1)
        else:
            content_file_id = None

        if content_file_id and content_file_id in content_links:
            # Forward the content to the user from Channel 2
            context.bot.forward_message(chat_id=update.message.chat_id, from_chat_id=CHANNEL_2_ID, message_id=content_links[content_file_id])
        else:
            update.message.reply_text("Invalid content file ID. Please specify a valid content file ID.")
    else:
        update.message.reply_text("You are not a subscriber. Subscribe to Channel 1 to get access to the content.")

def is_subscriber(user_id, bot):
    try:
        chat_member = bot.get_chat_member(CHANNEL_1_ID, user_id)
        return chat_member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR]
    except Unauthorized:
        print(f"Unauthorized: The bot may not have the necessary permissions or is not an admin in Channel 1.")
        return False
    except Exception as e:
        print(f"Error checking subscriber status: {e}")
        return False

def save_content_link(content_file_id, message_id):
    # Save the content link for the given content file ID
    content_links[content_file_id] = message_id
    print(f"Content link saved: {content_file_id} -> {message_id}")

def handle_new_content(update: Update, context: CallbackContext):
    print("Handling new content...")

    try:
        # Check if the effective message contains any type of file
        if update.effective_message and update.effective_message.document:
            content_file_id = str(update.effective_message.document.file_id)
        elif update.effective_message and update.effective_message.photo:
            # For photos, use the largest size available
            photo_sizes = update.effective_message.photo
            content_file_id = str(max(photo_sizes, key=lambda size: size.width).file_id)
        elif update.effective_message and update.effective_message.video:
            content_file_id = str(update.effective_message.video.file_id)
        # Add more elif conditions for other file types (audio, voice, sticker, animation, video_note) as needed

        message_id = update.effective_message.message_id

        # Generate a unique identifier for the content
        content_identifier = str(uuid.uuid4())

        # Generate the start link for the content
        start_link = f"https://t.me/{context.bot.username}?start={quote(content_identifier.encode('utf-8'))}"

        # Save the content link
        save_content_link(content_identifier, message_id)

        # Print or log the start link (you can use it when posting in Channel 2)
        print(f"Start Link for Content: {start_link}")

        # Send the start link to the admin chat
        try:
            context.bot.send_message(chat_id=CHANNEL_2_ID, text=f"Start Link for Content: {start_link}")
            print("Message sent to Database!")
        except Exception as e:
            print(f"Error sending message to Database: {e}")
    except Exception as e:
        print(f"Error handling new content: {e}")

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start, pass_args=True))
    dp.add_handler(MessageHandler(Filters.all & ~Filters.forwarded, handle_new_content))

    print("Bot is online and waiting for updates...")

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
