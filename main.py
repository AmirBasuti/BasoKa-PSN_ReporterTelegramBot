import os
from dotenv import load_dotenv

from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext
import logging

from config import Config
from server_manager import ServerManager
from bot_handler import BotHandler

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Error handler function
async def error_handler(update: object, context: CallbackContext):
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    if hasattr(update, 'message') and update.message:
        await update.message.reply_text("⚠️ An error occurred while processing your request. Please try again later.")



def main():
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise ValueError("BOT_TOKEN environment variable is not set. Please set it to your bot token from BotFather.")

    config = Config(bot_token=bot_token)
    server_manager = ServerManager()
    bot_handler = BotHandler(config, server_manager)

    app = ApplicationBuilder().token(config.bot_token).build()

    # Register command handlers
    handlers = [
        ("add", bot_handler.add),
        ("log", bot_handler.log),
        ("start", lambda update, context: bot_handler.start(update)),
        ("list", lambda update , context: bot_handler.list(update, context)),
        ("status", lambda update, context: bot_handler.status(update, context)),
        ("delete", lambda update, context: bot_handler.delete(update, context)),
        ("stopall", lambda update, context: bot_handler.stopall(update, context)),
        ("startall", lambda update, context: bot_handler.startall(update, context)),
        ("statusall", lambda update, context: bot_handler.statusall(update, context)),
        ("is_running", lambda update, context: bot_handler.is_running(update, context)),
        ("stopserver", lambda update, context: bot_handler.stopserver(update, context)),
        ("startserver", lambda update, context: bot_handler.startserver(update, context)),
    ]

    for command, handler in handlers:
        app.add_handler(CommandHandler(command, handler))

    # Register error handler
    app.add_error_handler(error_handler)

    app.run_polling()

if __name__ == "__main__":
    main()
