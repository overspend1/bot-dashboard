"""Example Discord Bot using discord.py."""

import sys
import os
import logging
import discord
from discord.ext import commands

# Configure logging to stdout for dashboard capture
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


class MyBot(commands.Bot):
    """Custom bot class with event handlers."""

    async def on_ready(self):
        """Called when bot is ready."""
        logger.info(f"✅ Logged in as {self.user.name} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guild(s)")
        logger.info("Bot is ready!")

        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="Bot Dashboard"
            )
        )

    async def on_command_error(self, ctx, error):
        """Handle command errors."""
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("❌ Unknown command. Use `!help` to see available commands.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: {error.param.name}")
        else:
            logger.error(f"Command error: {error}", exc_info=error)
            await ctx.send(f"❌ An error occurred: {str(error)}")

    async def on_message(self, message):
        """Handle incoming messages."""
        # Ignore bot's own messages
        if message.author == self.user:
            return

        # Log messages (optional)
        if not message.content.startswith(self.command_prefix):
            logger.debug(f"Message from {message.author}: {message.content[:50]}")

        # Process commands
        await self.process_commands(message)


def main():
    """Main bot function."""
    # Load configuration from environment variables
    token = os.getenv("TOKEN") or os.getenv("DISCORD_TOKEN")
    prefix = os.getenv("COMMAND_PREFIX") or os.getenv("PREFIX", "!")
    bot_name = os.getenv("BOT_NAME", "Discord Bot")

    if not token:
        logger.error("TOKEN or DISCORD_TOKEN environment variable is required!")
        sys.exit(1)

    logger.info(f"Starting {bot_name}...")
    logger.info(f"Command prefix: {prefix}")

    # Configure intents
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    # Create bot instance
    bot = MyBot(command_prefix=prefix, intents=intents)

    @bot.command(name="ping")
    async def ping(ctx):
        """Check bot latency."""
        latency = round(bot.latency * 1000)
        await ctx.send(f"🏓 Pong! Latency: {latency}ms")
        logger.info(f"Ping command from {ctx.author} - Latency: {latency}ms")

    @bot.command(name="status")
    async def status(ctx):
        """Check bot status."""
        embed = discord.Embed(
            title="✅ Bot Status",
            description="Bot is online and operational!",
            color=discord.Color.green()
        )
        embed.add_field(name="Servers", value=len(bot.guilds), inline=True)
        embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
        await ctx.send(embed=embed)
        logger.info(f"Status command from {ctx.author}")

    @bot.command(name="echo")
    async def echo(ctx, *, text: str):
        """Echo back the provided text."""
        await ctx.send(text)
        logger.info(f"Echo command from {ctx.author}: {text[:50]}")

    @bot.command(name="info")
    async def info(ctx):
        """Get user information."""
        user = ctx.author
        embed = discord.Embed(
            title="👤 User Information",
            color=discord.Color.blue()
        )
        embed.add_field(name="Username", value=str(user), inline=True)
        embed.add_field(name="ID", value=user.id, inline=True)
        embed.add_field(name="Nickname", value=user.display_name, inline=True)
        embed.add_field(name="Account Created", value=user.created_at.strftime("%Y-%m-%d"), inline=True)
        if isinstance(user, discord.Member):
            embed.add_field(name="Joined Server", value=user.joined_at.strftime("%Y-%m-%d"), inline=True)
            embed.add_field(name="Roles", value=len(user.roles) - 1, inline=True)
        embed.set_thumbnail(url=user.display_avatar.url)
        await ctx.send(embed=embed)
        logger.info(f"Info command from {user}")

    @bot.command(name="serverinfo")
    async def serverinfo(ctx):
        """Get server information."""
        guild = ctx.guild
        if not guild:
            await ctx.send("This command can only be used in a server.")
            return

        embed = discord.Embed(
            title=f"🏰 {guild.name}",
            description=guild.description or "No description",
            color=discord.Color.purple()
        )
        embed.add_field(name="Server ID", value=guild.id, inline=True)
        embed.add_field(name="Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        embed.add_field(name="Channels", value=len(guild.channels), inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        embed.add_field(name="Created", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        await ctx.send(embed=embed)
        logger.info(f"Serverinfo command from {ctx.author} in {guild.name}")

    @bot.command(name="hello")
    async def hello(ctx):
        """Say hello."""
        await ctx.send(f"👋 Hello {ctx.author.mention}!")
        logger.info(f"Hello command from {ctx.author}")

    try:
        # Run the bot
        bot.run(token)
    except KeyboardInterrupt:
        logger.info("Received stop signal, shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
