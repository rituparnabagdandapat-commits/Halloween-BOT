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

@bot.tree.command(name="halloween-panel", description="Open Halloween Settings Panel")
async def halloween_panel(interaction: discord.Interaction):
    member_count = interaction.guild.member_count
    candles = member_count # candles = members
    total_candies = sum(candies.values())

    embed = discord.Embed(
        title="🎃 WISTERIA HALLOWEEN SETTING",
        description="```diff\n+ HALLOWEEN MODE: ENABLED\n+ VERSION: Spooky v2.0\n```\n**Welcome to the official Halloween control center!**\n\n> 🕸️ Manage everything from here\n> 🍂 Theme: **ORANGE NIGHT**",
        color=0xFF6B00
    )
    embed.add_field(name="🍬 System", value="> Candies: ON\n> Tricks: ON\n> Treats: ON", inline=True)
    embed.add_field(name="🕯️ Candles = Members", value=f"> Members: {member_count}\n> Candles: {candles} 🕯️\n> Lit: {candles}/{candles}", inline=True)
    embed.add_field(name="⚙️ Settings", value="> Mode: Spooky\n> Color: Orange\n> Role: Pumpkin", inline=True)
    embed.add_field(name="📊 Live Stats", value=f"> Total Candies: {total_candies} 🍬\n> Total Players: {len(candies)}\n> Total Candles: {candles} 🕯️", inline=False)
    embed.set_thumbnail(url="https://em-content.zobj.net/source/apple/391/jack-o-lantern_1f383.png")
    embed.set_footer(text=f"Wisteria • {member_count} members = {candles} candles • Discord.gg/marvinsfolder", icon_url=interaction.guild.icon.url if interaction.guild and interaction.guild.icon else None)

    view = HalloweenPanelView()
    await interaction.response.send_message(embed=embed, view=view)

bot.run(os.getenv("DISCORD_TOKEN"))
