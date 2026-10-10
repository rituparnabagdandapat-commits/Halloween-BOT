from flask import Flask
import threading, os, random
import discord
from discord.ext import commands

app = Flask(__name__)
@app.route('/')
def home(): return "Halloween Bot Online! 🎃"
def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
threading.Thread(target=run_web, daemon=True).start()

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

candies = {}

class HalloweenView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🍬 Trick or Treat", style=discord.ButtonStyle.primary, custom_id="tot_btn")
    async def tot(self, interaction: discord.Interaction, button: discord.ui.Button):
        uid = str(interaction.user.id)
        candies[uid] = candies.get(uid, 0) + random.randint(1,5)
        await interaction.response.send_message(f"🎃 You got candies! You have **{candies[uid]}** 🍬", ephemeral=True)

    @discord.ui.button(label="🏆 Leaderboard", style=discord.ButtonStyle.secondary, custom_id="lb_btn")
    async def lb(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not candies:
            await interaction.response.send_message("No candies yet! Be first!", ephemeral=True)
            return
        sorted_c = sorted(candies.items(), key=lambda x: x[1], reverse=True)[:10]
        text = ""
        for i, (uid, count) in enumerate(sorted_c, 1):
            text += f"**{i}.** <@{uid}> - {count} 🍬\n"
        embed = discord.Embed(title="🏆 Candy Leaderboard", description=text, color=0xFF7518)
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="halloween-panel", description="Show Halloween event panel")
async def halloween_panel(interaction: discord.Interaction):
    await interaction.response.defer()
    embed = discord.Embed(
        title="🎃 Wisteria Halloween Event 🎃",
        description=f"**Welcome to the Spooky Season!**\n\n🕯️ **Total Members:** {interaction.guild.member_count}\n🍬 Collect candies with buttons below!",
        color=0xFF7518
    )
    await interaction.followup.send(embed=embed, view=HalloweenView())

@bot.event
async def on_ready():
    print(f"{bot.user} connected!")
    await bot.tree.sync()
    print("Commands synced!")

bot.run(os.environ.get("DISCORD_TOKEN"))
