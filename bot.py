import discord
from discord.ext import commands
from discord import app_commands
import os
import random
import json

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# تحميل البيانات
def load_data():
    try:
        with open("data.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open("data.json", "w") as f:
        json.dump(data, f)

data = load_data()

def create_user(user_id):
    if str(user_id) not in data:
        data[str(user_id)] = {
            "money": 0,
            "xp": 0,
            "level": 1,
            "items": []
        }

# جاهزية البوت
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ {bot.user} جاهز!")

# 💰 daily
@bot.tree.command(name="daily", description="استلام فلوس يومية")
async def daily(interaction: discord.Interaction):
    create_user(interaction.user.id)
    amount = random.randint(100, 500)
    data[str(interaction.user.id)]["money"] += amount
    save_data(data)

    await interaction.response.send_message(f"💰 حصلت على {amount} كوين!")

# 💳 balance
@bot.tree.command(name="balance", description="عرض رصيدك")
async def balance(interaction: discord.Interaction):
    create_user(interaction.user.id)
    money = data[str(interaction.user.id)]["money"]

    await interaction.response.send_message(f"💳 رصيدك: {money}")

# ⚔️ fight
@bot.tree.command(name="fight", description="قتال عشوائي")
async def fight(interaction: discord.Interaction):
    create_user(interaction.user.id)
    win = random.choice([True, False])

    if win:
        reward = random.randint(50, 200)
        data[str(interaction.user.id)]["money"] += reward
        msg = f"⚔️ فزت! +{reward} كوين"
    else:
        loss = random.randint(20, 100)
        data[str(interaction.user.id)]["money"] -= loss
        msg = f"💀 خسرت! -{loss} كوين"

    save_data(data)
    await interaction.response.send_message(msg)

# 🛒 shop
shop_items = {
    "sword": 500,
    "shield": 300,
    "potion": 100
}

@bot.tree.command(name="shop", description="عرض المتجر")
async def shop(interaction: discord.Interaction):
    msg = "🛒 المتجر:\n"
    for item, price in shop_items.items():
        msg += f"{item} - {price}💰\n"

    await interaction.response.send_message(msg)

# 🛍️ buy
@bot.tree.command(name="buy", description="شراء من المتجر")
@app_commands.describe(item="اسم العنصر")
async def buy(interaction: discord.Interaction, item: str):
    create_user(interaction.user.id)

    if item not in shop_items:
        return await interaction.response.send_message("❌ غير موجود")

    price = shop_items[item]
    user = data[str(interaction.user.id)]

    if user["money"] < price:
        return await interaction.response.send_message("❌ فلوسك ما تكفي")

    user["money"] -= price
    user["items"].append(item)
    save_data(data)

    await interaction.response.send_message(f"✅ اشتريت {item}")

# 🎒 inventory
@bot.tree.command(name="inventory", description="عرض أغراضك")
async def inventory(interaction: discord.Interaction):
    create_user(interaction.user.id)
    items = data[str(interaction.user.id)]["items"]

    if not items:
        return await interaction.response.send_message("📦 ما عندك شيء")

    await interaction.response.send_message(f"🎒 أغراضك: {', '.join(items)}")

# تشغيل
bot.run(os.environ["TOKEN"])