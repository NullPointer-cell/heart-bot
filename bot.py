import discord
from discord.ext import commands
import json
import os
from dotenv import load_dotenv
from threading import Thread
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running ✅"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# Start web server in a separate thread
Thread(target=run_web).start()

# Load .env file
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Setup intents
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.messages = True
intents.guilds = True
intents.members = True  # helps with mentions

bot = commands.Bot(command_prefix="!", intents=intents)

# Load hearts data
if os.path.exists("hearts.json"):
    with open("hearts.json", "r") as f:
        hearts = json.load(f)
else:
    hearts = {}

def save_hearts():
    """Save hearts to file"""
    with open("hearts.json", "w") as f:
        json.dump(hearts, f, indent=4)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_reaction_add(reaction, user):
    # Ignore bot reactions
    if user.bot:
        return

    # Only count heart emoji ❤️
    if str(reaction.emoji) == "❤️":
        message_author = str(reaction.message.author.id)

        # Increment heart count
        if message_author not in hearts:
            hearts[message_author] = 0
        hearts[message_author] += 1
        save_hearts()

        # Send message in same channel
        await reaction.message.channel.send(
            f"❤️ <@{message_author}> received a heart from {user.mention}! "
            f"They now have **{hearts[message_author]} hearts**."
        )

@bot.command()
async def hearts_of(ctx, member: discord.Member):
    """Check how many hearts a user has"""
    count = hearts.get(str(member.id), 0)
    await ctx.send(f"❤️ {member.mention} has {count} hearts!")

@bot.command()
async def tophearts(ctx):
    """Show leaderboard of top users"""
    if not hearts:
        await ctx.send("No hearts yet 💔")
        return

    sorted_hearts = sorted(hearts.items(), key=lambda x: x[1], reverse=True)
    top = sorted_hearts[:5]

    msg = "🏆 **Top Hearts Leaderboard** 🏆\n"
    for i, (user_id, count) in enumerate(top, start=1):
        msg += f"{i}. <@{user_id}> — ❤️ {count}\n"

    await ctx.send(msg)
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

bot.run(TOKEN)


print("hello")