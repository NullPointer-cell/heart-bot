# test_bot.py
import os
import asyncio
import discord
from discord.ext import commands

# -------------------
# Bot Token from environment
# -------------------
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    raise RuntimeError("DISCORD_TOKEN not set")

# -------------------
# Intents
# -------------------
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# -------------------
# Debug event for reactions
# -------------------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")

@bot.event
async def on_reaction_add(reaction, user):
    print(f"🪶 Reaction detected: {reaction.emoji} | type: {type(reaction.emoji)}")
    print(f"By user: {user} in channel: {reaction.message.channel}")

    # Test message in the same channel
    await reaction.message.channel.send(
        f"Reaction detected: {reaction.emoji} from {user.mention}"
    )

# -------------------
# Keep bot alive on Render
# -------------------
from aiohttp import web

async def handle_root(request):
    return web.Response(text="OK - bot running")

async def start_web_server():
    port = int(os.getenv("PORT", "8000"))
    app = web.Application()
    app.router.add_get("/", handle_root)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"🌐 Web server running on port {port}")

# -------------------
# Entrypoint
# -------------------
async def main():
    await start_web_server()
    await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
