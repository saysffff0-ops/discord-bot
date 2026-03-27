import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# عند تشغيل البوت
@bot.event
async def on_ready():
    await bot.tree.sync()  # مهم عشان تظهر أوامر السلاش
    print(f"Logged in as {bot.user}")

# أمر سلاش /ping
@bot.tree.command(name="ping", description="Ping command")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong!")

# أمر سلاش /hello
@bot.tree.command(name="hello", description="Say hello")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("👋 هلا والله!")

# تشغيل البوت
bot.run(os.getenv("TOKEN"))