from flask import Flask
import threading, os, random
import discord
from discord.ext import commands
from discord import app_commands

# --- Keep Render FREE alive ---
app = Flask(__name__)
@app.route('/')
def home(): return "Halloween Bot Online! 🎃"
def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
threading.Thread(target=run_web, daemon=True).start()

# --- Discord Bot ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

candies = {} # simple database

class HalloweenView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🍬 Trick or Treat", style=discord.ButtonStyle.primary, custom_id="tot")
    async def tot(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = str(interaction.user.id)
        candies[user] = candies.get(user, 0) + random.randint(1,5)
        await interaction.response.send_message(f"You got candies! 🍬 Now you have **{candies[user]}** candies!", ephemeral=True)

    @discord.ui.button(label="🏆 Leaderboard", style=discord.ButtonStyle.secondary, custom_id="lb")
    async def lb(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not candies:
            await interaction.response.send_message("No candies yet!", ephemeral=True)
            return
        sorted_candies = sorted(candies.items(), key=lambda x: x[1], reverse=True)[:10]
        text = ""
        for i, (uid, count) in enumerate(sorted_candies, 1):
            text += f"**{i}.** <@{uid}> - {count} 🍬\n"
        embed = discord.Embed(title="🏆 Candy Leaderboard", description=text, color=0xFF7518)
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="halloween-panel", description="Show Halloween event panel")
async def halloween_panel(interaction: discord.Interaction):
    await interaction.response.defer()
    embed = discord.Embed(
        title="🎃 Wisteria Halloween Event 🎃",
        description="**Welcome to the Spooky Season!**\n\nClick the buttons below to play!\n\n🕯️ **Total Members:** {}\n🍬 **Collect candies and climb the leaderboard!**".format(interaction.guild.member_count),
        color=0xFF7518
    )
    embed.set_image(url="https://i.imgur.com/Czxt6v5.png") # halloween banner
    await interaction.followup.send(embed=embed, view=HalloweenView())

@bot.event
async def on_ready():
    print(f"{bot.user} connected!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)

# --- PUT YOUR TOKEN HERE ---
TOKEN = os.environ.get("DISCORD_TOKEN") # Set this in Render Environment
bot.run(TOKEN)
