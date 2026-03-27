import discord
from discord.ext import commands
from discord import app_commands
import json
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# تحميل البيانات
def load_data():
    try:
        with open("data.json", "r") as f:
            return json.load(f)
    except:
        return {}

# حفظ البيانات
def save_data(data):
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)

data = load_data()

@bot.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {bot.user}")

# =========================
# 💰 نظام فلوس
# =========================

@tree.command(name="فلوسي", description="عرض فلوسك")
async def money(interaction: discord.Interaction):
    user = str(interaction.user.id)
    if user not in data:
        data[user] = {"money": 0}
        save_data(data)

    await interaction.response.send_message(f"💰 فلوسك: {data[user]['money']}")

@tree.command(name="اعطاء", description="تعطي فلوس لشخص")
@app_commands.describe(member="الشخص", amount="الكمية")
async def give(interaction: discord.Interaction, member: discord.Member, amount: int):
    user = str(interaction.user.id)
    target = str(member.id)

    if user not in data:
        data[user] = {"money": 0}
    if target not in data:
        data[target] = {"money": 0}

    if data[user]["money"] < amount:
        await interaction.response.send_message("❌ ما عندك فلوس كفاية")
        return

    data[user]["money"] -= amount
    data[target]["money"] += amount
    save_data(data)

    await interaction.response.send_message(f"✅ عطيت {member.mention} {amount}💰")

@tree.command(name="اضف_فلوس", description="إضافة فلوس (ادمن)")
@app_commands.describe(member="الشخص", amount="الكمية")
async def add_money(interaction: discord.Interaction, member: discord.Member, amount: int):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ هذا الأمر للأدمن فقط")
        return

    target = str(member.id)
    if target not in data:
        data[target] = {"money": 0}

    data[target]["money"] += amount
    save_data(data)

    await interaction.response.send_message(f"✅ تمت إضافة {amount}💰 لـ {member.mention}")

# =========================
# 🎮 أوامر عامة
# =========================

@tree.command(name="بنج", description="يعرض سرعة البوت")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"🏓 {round(bot.latency * 1000)}ms")

@tree.command(name="ايدي", description="يعرض ايديك")
async def myid(interaction: discord.Interaction):
    await interaction.response.send_message(f"🆔 ايديك: {interaction.user.id}")

@tree.command(name="معلوماتي", description="معلومات عنك")
async def info(interaction: discord.Interaction):
    user = interaction.user
    embed = discord.Embed(title="📋 معلوماتك", color=discord.Color.blue())
    embed.add_field(name="الاسم", value=user.name)
    embed.add_field(name="الايدي", value=user.id)
    embed.add_field(name="تاريخ الإنشاء", value=user.created_at.strftime("%Y-%m-%d"))
    await interaction.response.send_message(embed=embed)

# =========================

bot.run(TOKEN)