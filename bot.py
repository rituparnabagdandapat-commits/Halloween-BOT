from flask import Flask
import threading, os

app = Flask(__name__)
@app.route('/')
def home():
    return "Halloween Bot is Online!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_web, daemon=True).start()
import discord
from discord.ext import commands
import random
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

candies = {}

# --- PANEL VIEW WITH BUTTONS ---
class HalloweenPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Trick or Treat", style=discord.ButtonStyle.primary, emoji="🍬", row=0)
    async def trick(self, interaction: discord.Interaction, button: discord.ui.Button):
        candies[interaction.user.id] = candies.get(interaction.user.id, 0) + 1
        await interaction.response.send_message(f"🎃 **TREAT!** +1 Candy! Total: {candies[interaction.user.id]} 🍬", ephemeral=True)

    @discord.ui.button(label="Spook Friend", style=discord.ButtonStyle.danger, emoji="👻", row=0)
    async def spook(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("💀 BOO! You spooked the chat!", ephemeral=True)

    @discord.ui.button(label="Pumpkin Role", style=discord.ButtonStyle.success, emoji="🎃", row=0)
    async def pumpkin(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, name="🎃 Pumpkin")
        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"Added {role.mention}!", ephemeral=True)
        else:
            await interaction.response.send_message("Create a role named `🎃 Pumpkin` first!", ephemeral=True)

    @discord.ui.button(label="Events", style=discord.ButtonStyle.secondary, emoji="📅", row=1)
    async def events(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="🎃 All Events", color=0xFF6B00)
        embed.add_field(name="🍬 Trick Hunt", value="Collect 100 candies", inline=False)
        embed.add_field(name="🎃 Pumpkin Hunt", value="Oct 25 - Find 10 hidden", inline=False)
        embed.add_field(name="💀 Boss Night", value="Oct 31 - 8PM IST VC Event", inline=False)
        embed.add_field(name="🏆 Top Collector", value="Winner gets Nitro!", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Leaderboard", style=discord.ButtonStyle.secondary, emoji="🏆", row=1)
    async def lb(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not candies:
            await interaction.response.send_message("No candies yet!", ephemeral=True)
            return
        top = sorted(candies.items(), key=lambda x: x[1], reverse=True)[:10]
        txt = "\n".join([f"`{i+1}.` <@{uid}> - **{c}** 🍬" for i, (uid, c) in enumerate(top)])
        embed = discord.Embed(title="🏆 Candy Leaderboard", description=txt, color=0xFF6B00)
        await interaction.response.send_message(embed=embed, ephemeral=True)

# --- EVENTS ---
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        await bot.tree.sync()
        print("Commands synced!")
    except Exception as e:
        print(e)

@bot.event
async def on_member_join(member):
    candles = member.guild.member_count
    channel = member.guild.system_channel or member.guild.text_channels[0]
    if channel:
        embed = discord.Embed(
            title="🕯️ New Candle Lit!",
            description=f"Welcome {member.mention}!\n\n> 🕯️ **+1 Candle Added**\n> Total Candles: **{candles}** = **{candles} Members**",
            color=0xFF6B00
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text="Wisteria Halloween • Candles = Members")
        try:
            await channel.send(embed=embed)
        except:
            pass

@bot.event
async def on_member_remove(member):
    candles = member.guild.member_count
    channel = member.guild.system_channel or member.guild.text_channels[0]
    if channel:
        embed = discord.Embed(
            title="🕯️ Candle Gone Out...",
            description=f"{member.name} left...\n\n> 🕯️ **-1 Candle**\n> Total Candles: **{candles}** = **{candles} Members**",
            color=0x2F3136
        )
        try:
            await channel.send(embed=embed)
        except:
            pass

# --- COMMANDS ---
@bot.tree.command(name="trickortreat", description="Trick or Treat!")
async def trickortreat(interaction: discord.Interaction):
    candies[interaction.user.id] = candies.get(interaction.user.id, 0) + 1
    await interaction.response.send_message(f"🍬 +1 Candy! Total: {candies[interaction.user.id]}")

@bot.tree.command(name="leaderboard", description="Candy leaderboard")
async def leaderboard(interaction: discord.Interaction):
    if not candies:
        await interaction.response.send_message("No candies yet! Use /trickortreat")
        return
    top = sorted(candies.items(), key=lambda x: x[1], reverse=True)[:10]
    txt = "\n".join([f"<@{uid}> - {c}" for uid, c in top])
    embed = discord.Embed(title="🏆 Halloween Leaderboard", description=txt, color=0xFF6B00)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="event", description="See all Halloween events")
async def event(interaction: discord.Interaction):
    embed = discord.Embed(title="🎃 Halloween Events", description="All events in Marvin's Folder", color=0xFF6B00)
    embed.add_field(name="🍬 Trick or Treat", value="`/trickortreat` - Collect candies", inline=False)
    embed.add_field(name="🏆 Leaderboard", value="`/leaderboard` - Top collectors", inline=False)
    embed.add_field(name="🎃 Main Panel", value="`/halloween-panel` - Open settings", inline=False)
    embed.add_field(name="🕯️ Candles", value="1 Member = 1 Candle", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="halloween-panel", description="Show Halloween event panel")
async def halloween_panel(interaction: discord.Interaction):
    await interaction.response.defer() # <- THIS FIXES IT
    
    embed = discord.Embed(
        title="🎃 Wisteria Halloween Event 🎃",
        description="Welcome to the spooky season!",
        color=discord.Color.orange()
    )
    embed.add_field(name="🕯️ Candles", value=f"{interaction.guild.member_count} Members", inline=True)
    embed.add_field(name="🍬 Trick or Treat", value="Click below!", inline=True)
    
    view = YourButtonView() # your buttons class
    
    await interaction.followup.send(embed=embed, view=view)

bot.run(os.getenv("DISCORD_TOKEN"))
