import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# أمر ping
@bot.command()
async def ping(ctx):
    await ctx.send("🏓 pong!")

# أمر ترحيب
@bot.command()
async def hello(ctx):
    await ctx.send("هلا والله 👋")

# شغل البوت
bot.run("")