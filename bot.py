# bot.py
import os
import json
import asyncio
from dotenv import load_dotenv
from aiohttp import web
import discord
from discord.ext import commands

# -------------------
# Load environment variables
# -------------------
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    raise RuntimeError("DISCORD_TOKEN not set in environment")

# -------------------
# Bot setup with intents
# -------------------
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# -------------------
# Heart tracking storage
# -------------------
HEARTS_FILE = "hearts.json"
if os.path.exists(HEARTS_FILE):
    with open(HEARTS_FILE, "r") as f:
        hearts = json.load(f)
else:
    hearts = {}

def save_hearts():
    with open(HEARTS_FILE, "w") as f:
        json.dump(hearts, f, indent=4)

# -------------------
# Heart log channel ID
# -------------------
HEART_LOG_CHANNEL_ID = 1424096327846854837  # replace with your channel ID

# -------------------
# Heart emoji list
# -------------------
HEART_EMOJIS = ["❤️", "💖", "💓", "💕", "💗"]

# -------------------
# Bot events
# -------------------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")

@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    # Debug: show emoji detected
    print(f"🪶 Reaction emoji: {reaction.emoji} | Type: {type(reaction.emoji)}")

    # Count heart emoji (Unicode or custom)
    if (isinstance(reaction.emoji, str) and reaction.emoji in HEART_EMOJIS) or \
       (isinstance(reaction.emoji, discord.Emoji) and "heart" in reaction.emoji.name.lower()):
        
        message_author = str(reaction.message.author.id)
        hearts.setdefault(message_author, 0)
        hearts[message_author] += 1
        save_hearts()

        # Send message in log channel
        channel = bot.get_channel(HEART_LOG_CHANNEL_ID)
        if channel:
            await channel.send(
                f"❤️ <@{message_author}> received a heart from {user.mention} "
                f"and now has {hearts[message_author]} hearts."
            )

# -------------------
# Bot commands
# -------------------
@bot.command()
async def hearts_of(ctx, member: discord.Member):
    count = hearts.get(str(member.id), 0)
    await ctx.send(f"❤️ {member.mention} has {count} hearts!")

@bot.command()
async def tophearts(ctx):
    sorted_hearts = sorted(hearts.items(), key=lambda x: x[1], reverse=True)
    top = sorted_hearts[:5]
    if not top:
        await ctx.send("No hearts yet 💔")
        return

    msg = "🏆 **Top Hearts Leaderboard** 🏆\n"
    for i, (user_id, count) in enumerate(top, start=1):
        msg += f"{i}. <@{user_id}> — ❤️ {count}\n"

    await ctx.send(msg)

# -------------------
# Minimal aiohttp web server for Render
# -------------------
async def handle_root(request):
    return web.Response(text="OK - bot is running")

async def start_web_server():
    port = int(os.getenv("PORT", "8000"))
    app = web.Application()
    app.router.add_get("/", handle_root)
    app.router.add_get("/healthz", handle_root)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"🌐 Web server started on port {port}")

# -------------------
# Entrypoint
# -------------------
async def main():
    await start_web_server()
    await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down...")
