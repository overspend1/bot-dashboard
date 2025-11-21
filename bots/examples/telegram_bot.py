"""Example Telegram Bot using python-telegram-bot."""

import sys
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Configure logging to stdout for dashboard capture
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    try:
        user = update.effective_user
        welcome_text = (
            f"👋 Hello {user.mention_html()}!\n\n"
            f"I'm a bot managed by the Bot Management Dashboard.\n\n"
            f"Use /help to see available commands."
        )
        await update.message.reply_html(welcome_text)
        logger.info(f"Start command from user {user.id} (@{user.username})")
    except Exception as e:
        logger.error(f"Error in start command: {e}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    try:
        help_text = (
            "📚 **Available Commands:**\n\n"
            "/start - Start the bot\n"
            "/help - Show this help message\n"
            "/status - Check bot status\n"
            "/ping - Check bot response time\n"
            "/echo <text> - Echo back your message\n"
            "/info - Get your user information"
        )
        await update.message.reply_text(help_text)
        logger.info(f"Help command from user {update.effective_user.id}")
    except Exception as e:
        logger.error(f"Error in help command: {e}")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command."""
    try:
        status_text = "✅ Bot is online and operational!"
        await update.message.reply_text(status_text)
        logger.info(f"Status command from user {update.effective_user.id}")
    except Exception as e:
        logger.error(f"Error in status command: {e}")


async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ping command."""
    try:
        await update.message.reply_text("🏓 Pong!")
        logger.info(f"Ping command from user {update.effective_user.id}")
    except Exception as e:
        logger.error(f"Error in ping command: {e}")


async def echo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /echo command."""
    try:
        if context.args:
            text = " ".join(context.args)
            await update.message.reply_text(text)
            logger.info(f"Echo command from user {update.effective_user.id}: {text[:50]}")
        else:
            await update.message.reply_text("Please provide text to echo. Usage: /echo <text>")
    except Exception as e:
        logger.error(f"Error in echo command: {e}")


async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /info command."""
    try:
        user = update.effective_user
        info_text = (
            f"👤 **Your Information:**\n\n"
            f"ID: `{user.id}`\n"
            f"First Name: {user.first_name}\n"
            f"Last Name: {user.last_name if user.last_name else 'N/A'}\n"
            f"Username: @{user.username if user.username else 'N/A'}\n"
            f"Language: {user.language_code if user.language_code else 'N/A'}"
        )
        await update.message.reply_text(info_text)
        logger.info(f"Info command from user {user.id}")
    except Exception as e:
        logger.error(f"Error in info command: {e}")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors."""
    logger.error(f"Update {update} caused error: {context.error}", exc_info=context.error)


def main():
    """Main bot function."""
    # Load configuration from environment variables
    token = os.getenv("TOKEN") or os.getenv("BOT_TOKEN")
    bot_name = os.getenv("BOT_NAME", "Telegram Bot")

    if not token:
        logger.error("TOKEN or BOT_TOKEN environment variable is required!")
        sys.exit(1)

    logger.info(f"Starting {bot_name}...")

    try:
        # Create application
        application = Application.builder().token(token).build()

        # Register command handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("status", status_command))
        application.add_handler(CommandHandler("ping", ping_command))
        application.add_handler(CommandHandler("echo", echo_command))
        application.add_handler(CommandHandler("info", info_command))

        # Register error handler
        application.add_error_handler(error_handler)

        logger.info(f"✅ {bot_name} started successfully!")
        logger.info("Bot is now running. Press Ctrl+C to stop.")

        # Start the bot
        application.run_polling(allowed_updates=Update.ALL_TYPES)

    except KeyboardInterrupt:
        logger.info("Received stop signal, shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Bot stopped.")


if __name__ == "__main__":
    main()
