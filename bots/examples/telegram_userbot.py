"""Example Telegram Userbot using Telethon."""

import sys
import os
import logging
import asyncio
from telethon import TelegramClient, events

# Configure logging to stdout for dashboard capture
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


async def main():
    """Main userbot function."""
    # Load configuration from environment variables
    api_id = os.getenv("API_ID")
    api_hash = os.getenv("API_HASH")
    phone = os.getenv("PHONE")
    session_name = os.getenv("SESSION_NAME", "userbot_session")
    bot_name = os.getenv("BOT_NAME", "Telegram Userbot")

    if not api_id or not api_hash:
        logger.error("API_ID and API_HASH are required!")
        sys.exit(1)

    logger.info(f"Starting {bot_name}...")
    logger.info(f"Using session: {session_name}")

    try:
        # Create Telegram client
        client = TelegramClient(session_name, int(api_id), api_hash)

        @client.on(events.NewMessage(pattern=r"^\.ping$"))
        async def ping_handler(event):
            """Handle .ping command."""
            try:
                await event.reply("🏓 Pong!")
                logger.info(f"Replied to ping from {event.sender_id}")
            except Exception as e:
                logger.error(f"Error handling ping: {e}")

        @client.on(events.NewMessage(pattern=r"^\.echo (.+)"))
        async def echo_handler(event):
            """Handle .echo command."""
            try:
                text = event.pattern_match.group(1)
                await event.reply(text)
                logger.info(f"Echoed: {text[:50]}")
            except Exception as e:
                logger.error(f"Error handling echo: {e}")

        @client.on(events.NewMessage(pattern=r"^\.info$"))
        async def info_handler(event):
            """Handle .info command."""
            try:
                me = await client.get_me()
                info_text = (
                    f"👤 **User Info**\n"
                    f"ID: `{me.id}`\n"
                    f"Name: {me.first_name or ''} {me.last_name or ''}\n"
                    f"Username: @{me.username if me.username else 'N/A'}\n"
                    f"Phone: {me.phone if me.phone else 'N/A'}"
                )
                await event.reply(info_text)
                logger.info("Sent user info")
            except Exception as e:
                logger.error(f"Error handling info: {e}")

        @client.on(events.NewMessage(pattern=r"^\.help$"))
        async def help_handler(event):
            """Handle .help command."""
            try:
                help_text = (
                    "📚 **Available Commands**\n\n"
                    "`.ping` - Check if bot is alive\n"
                    "`.echo <text>` - Echo back the text\n"
                    "`.info` - Show your user info\n"
                    "`.help` - Show this help message"
                )
                await event.reply(help_text)
                logger.info("Sent help message")
            except Exception as e:
                logger.error(f"Error handling help: {e}")

        # Start the client
        await client.start(phone=phone)
        logger.info(f"✅ {bot_name} started successfully!")

        me = await client.get_me()
        logger.info(f"Logged in as: {me.first_name} (@{me.username if me.username else me.id})")

        # Keep the client running
        logger.info("Userbot is now running. Press Ctrl+C to stop.")
        await client.run_until_disconnected()

    except KeyboardInterrupt:
        logger.info("Received stop signal, shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        if "client" in locals():
            await client.disconnect()
        logger.info("Userbot stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
