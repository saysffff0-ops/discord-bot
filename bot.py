import discord
from discord.ext import commands, tasks
from discord import app_commands
import os, json, time, re

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# ========= Data =========
DATA_FILE = "points.json"

def load():
    try:
        with open(DATA_FILE) as f:
            return json.load(f)
    except:
        return {}

def save(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

points = load()

def add_points(uid, amount):
    uid = str(uid)
    if uid not in points:
        points[uid] = {"points": 0, "last": 0}

    points[uid]["points"] += amount
    points[uid]["last"] = time.time()
    save(points)

def get_points(uid):
    return points.get(str(uid), {}).get("points", 0)

# ========= Normalize =========
def normalize(text):
    return re.sub(r"[^a-zA-Z0-9ء-ي]", "", text.lower())

# ========= Protection =========
BAN_WORDS = ["قحبه","كس","شرموطه","منيوك","ديوث","عرص","خول","زاني","زانيه","لوطي","عاهره","قواد","tizi","9a7ba","koss"]
BAD_WORDS = ["زق","كلب","حمار","حيوان","ورع","نوب","اقلع","انقلع","خبل"]

CUSTOM_WORDS = {
    "زوط": 10,
    "حمار": 30,
    "ياحمار": 30,
    "كلب": 60,
    "ياكلب": 60,
    "غبي": 15,
    "نوب": 15
}

SPAM = {}

# ========= Ready =========
@bot.event
async def on_ready():
    await tree.sync()
    check_members.start()
    print(f"🔥 Ready: {bot.user}")

# ========= Messages =========
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = normalize(message.content)

    # 🔴 روابط
    if re.search(r"(https?://|www\.|discord\.gg)", message.content):
        await message.delete()
        return

    # 🔴 كلمات مخصصة
    for word, minutes in CUSTOM_WORDS.items():
        if word in content:
            await message.delete()
            try:
                until = discord.utils.utcnow() + discord.timedelta(minutes=minutes)
                await message.author.timeout(until)
                await message.channel.send(f"⛔ | {message.author.mention} ميوت {minutes} دقيقة")
            except:
                pass
            return

    # 🔴 باند
    if any(word in content for word in BAN_WORDS):
        await message.delete()
        try:
            await message.guild.ban(message.author)
            await message.channel.send(f"💀🚫 | {message.author.mention} تبنيد نهائي")
        except:
            pass
        return

    # 🟡 ميوت 24 ساعة
    if any(word in content for word in BAD_WORDS):
        await message.delete()
        try:
            until = discord.utils.utcnow() + discord.timedelta(hours=24)
            await message.author.timeout(until)
            await message.channel.send(f"🚫💀 | {message.author.mention} ميوت 24 ساعة")
        except:
            pass
        return

    # 🔴 سبام
    uid = message.author.id
    if uid not in SPAM:
        SPAM[uid] = []

    SPAM[uid].append(time.time())
    SPAM[uid] = [t for t in SPAM[uid] if time.time() - t < 5]

    if len(SPAM[uid]) >= 5:
        await message.delete()
        try:
            until = discord.utils.utcnow() + discord.timedelta(minutes=10)
            await message.author.timeout(until)
        except:
            pass
        return

    await bot.process_commands(message)

# ========= Dummy Loop =========
@tasks.loop(hours=6)
async def check_members():
    pass

# ========= Run =========
bot.run(os.getenv("TOKEN"))