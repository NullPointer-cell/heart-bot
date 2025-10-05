# bot.py
import os
import json
import asyncio
from dotenv import load_dotenv
from aiohttp import web
import discord
from discord.ext import commands

# load env (works locally if you have a .env file; on Render, env vars are injected)
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    raise RuntimeError("DISCORD_TOKEN not set in environment")

# Bot intents & setup
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Hearts storage
HEARTS_FILE = "hearts.json"
if os.path.exists(HEARTS_FILE):
    with open(HEARTS_FILE, "r") as f:
        hearts = json.load(f)
else:
    hearts = {}

def save_hearts():
    with open(HEARTS_FILE, "w") as f:
        json.dump(hearts, f, indent=4)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")

@bot.event
@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    if str(reaction.emoji) == "❤️":
        message_author = str(reaction.message.author.id)

        # Increment count
        if message_author not in hearts:
            hearts[message_author] = 0
        hearts[message_author] += 1
        save_hearts()

        # Send message in specific channel
        HEART_LOG_CHANNEL_ID = 1424096327846854837  # your channel ID here
        channel = bot.get_channel(HEART_LOG_CHANNEL_ID)
        if channel:
            await channel.send(
                f"❤️ <@{message_author}> received a heart from {user.mention} "
                f"and now has {hearts[message_author]} hearts."
            )


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


# ---------------------
# Minimal aiohttp web server so Render sees an open port
# ---------------------
async def handle_root(request):
    return web.Response(text="OK - bot is running")

async def start_web_server():
    # Render (and many PaaS) provide a PORT env var. Default to 8000 locally.
    port = int(os.getenv("PORT", "8000"))
    app = web.Application()
    app.router.add_get("/", handle_root)
    app.router.add_get("/healthz", handle_root)  # simple health check

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"🌐 Web server started on port {port}")

# ---------------------
# Entrypoint: run webserver and bot in same event loop
# ---------------------
async def main():
    # start web server in background
    await start_web_server()

    # start the bot (this call does not return until bot stops)
    await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down...")

