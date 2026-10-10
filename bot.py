import discord
from discord.ext import commands
import random
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

candies = {}

TRICKS = ["BOO! You got scared!", "Bats flew away with your candy!", "Skeleton stole it!"]
TREATS = ["Candy!", "Chocolate!", "Lollipop!", "Golden Pumpkin! +3"]

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        await bot.tree.sync()
        print("Commands synced!")
    except Exception as e:
        print(e)

@bot.tree.command(name="trickortreat", description="Trick or Treat!")
async def trickortreat(interaction: discord.Interaction):
    user = interaction.user.id
    is_treat = random.choice([True, False])
    if is_treat:
        treat = random.choice(TREATS)
        candies[user] = candies.get(user, 0) + (3 if "Golden" in treat else 1)
        await interaction.response.send_message(f"TREAT! {treat}\nYou have {candies[user]} candies")
    else:
        trick = random.choice(TRICKS)
        await interaction.response.send_message(f"TRICK! {trick}")

@bot.tree.command(name="leaderboard", description="Candy leaderboard")
async def leaderboard(interaction: discord.Interaction):
    if not candies:
        await interaction.response.send_message("No candies yet! Use /trickortreat")
        return
    sorted_c = sorted(candies.items(), key=lambda x: x[1], reverse=True)[:10]
    text = "\n".join([f"<@{uid}> - {count}" for uid, count in sorted_c])
    embed = discord.Embed(title="Halloween Leaderboard", description=text, color=0xFF6B00)
    await interaction.response.send_message(embed=embed)

bot.run(os.getenv("DISCORD_TOKEN"))
