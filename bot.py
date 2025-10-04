import discord
from discord.ext import commands
import json
import os
from dotenv import load_dotenv
import os


intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Load stored hearts
if os.path.exists("hearts.json"):
    with open("hearts.json", "r") as f:
        hearts = json.load(f)
else:
    hearts = {}

def save_hearts():
    with open("hearts.json", "w") as f:
        json.dump(hearts, f, indent=4)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    if str(reaction.emoji) == "❤️":  # Only count hearts
        message_author = str(reaction.message.author.id)

        # Increment count
        if message_author not in hearts:
            hearts[message_author] = 0
        hearts[message_author] += 1
        save_hearts()

        await reaction.message.channel.send(
            f"❤️ <@{message_author}> received a heart from {user.mention} "
            f"and now has {hearts[message_author]} hearts."
        )

@bot.command()
async def hearts_of(ctx, member: discord.Member):
    """Check hearts of a user."""
    count = hearts.get(str(member.id), 0)
    await ctx.send(f"❤️ {member.mention} has {count} hearts!")

@bot.command()
async def tophearts(ctx):
    """Show top 5 users with most hearts."""
    sorted_hearts = sorted(hearts.items(), key=lambda x: x[1], reverse=True)
    top = sorted_hearts[:5]
    if not top:
        await ctx.send("No hearts yet 💔")
        return

    msg = "🏆 **Top Hearts Leaderboard** 🏆\n"
    for i, (user_id, count) in enumerate(top, start=1):
        msg += f"{i}. <@{user_id}> — ❤️ {count}\n"

    await ctx.send(msg)
    
load_dotenv()
bot.run(os.getenv("DISCORD_TOKEN"))
