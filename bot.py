import discord
from discord.ext import commands
from discord.ui import View, Button, Select
import os, random, asyncio
from collections import defaultdict

# ───── keep alive ─────
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home():
    return "Alive"

def keep_alive():
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()

# ───── bot ─────
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=None, intents=intents)
tree = bot.tree

economy = defaultdict(int)
xp = defaultdict(int)
levels = defaultdict(lambda:1)
warnings = defaultdict(int)
spam = defaultdict(list)

SHOP = {"VIP":500, "مميز":300}
TICKET_TYPES = ["دعم 🛠️","شراء 💰","مشاكل 🎮","اقتراح 💡"]

# ───── ready ─────
@bot.event
async def on_ready():
    await tree.sync()
    print("🔥 جاهز")

# ───── أوامر ─────
@tree.command(name="ping")
async def ping(i: discord.Interaction):
    await i.response.send_message(f"🏓 {round(bot.latency*1000)}ms")

@tree.command(name="حذف")
async def delete(i: discord.Interaction, عدد:int):
    await i.response.defer(ephemeral=True)
    await i.channel.purge(limit=عدد)
    await i.followup.send(f"🧹 تم حذف {عدد}", ephemeral=True)

@tree.command(name="فلوسي")
async def money(i: discord.Interaction):
    await i.response.send_message(f"💰 {economy[i.user.id]}")

@tree.command(name="يومي")
async def daily(i: discord.Interaction):
    economy[i.user.id]+=200
    await i.response.send_message("💸 +200")

@tree.command(name="تحويل")
async def give(i: discord.Interaction, عضو:discord.Member, مبلغ:int):
    if economy[i.user.id] < مبلغ:
        return await i.response.send_message("❌ فلوسك قليلة")
    economy[i.user.id]-=مبلغ
    economy[عضو.id]+=مبلغ
    await i.response.send_message("✅ تم")

@tree.command(name="المتجر")
async def shop(i: discord.Interaction):
    await i.response.send_message("\n".join([f"{k} = {v}" for k,v in SHOP.items()]))

@tree.command(name="شراء")
async def buy(i: discord.Interaction, item:str):
    if item not in SHOP:
        return await i.response.send_message("❌ غير موجود")
    if economy[i.user.id] < SHOP[item]:
        return await i.response.send_message("❌ فلوسك قليلة")
    economy[i.user.id]-=SHOP[item]
    await i.response.send_message(f"✅ اشتريت {item}")

@tree.command(name="رقم")
async def num(i: discord.Interaction):
    await i.response.send_message(f"🎲 {random.randint(1,100)}")

@tree.command(name="لفلي")
async def lvl(i: discord.Interaction):
    await i.response.send_message(f"🎖️ {levels[i.user.id]}")

# ───── تذاكر ─────
class Close(View):
    @discord.ui.button(label="إغلاق 🔒", style=discord.ButtonStyle.red)
    async def close(self, i: discord.Interaction, b: Button):
        await i.response.defer()
        await i.channel.delete()

class Ticket(View):
    def __init__(self):
        super().__init__()
        self.add_item(SelectMenu())

class SelectMenu(Select):
    def __init__(self):
        options=[discord.SelectOption(label=x) for x in TICKET_TYPES]
        super().__init__(placeholder="اختر", options=options)

    async def callback(self, i: discord.Interaction):
        await i.response.defer(ephemeral=True)
        name=f"ticket-{i.user.name}"

        if discord.utils.get(i.guild.channels,name=name):
            return await i.followup.send("❌ عندك تذكرة",ephemeral=True)

        ch=await i.guild.create_text_channel(name)
        await ch.send(f"🎫 {i.user.mention}", view=Close())
        await i.followup.send(f"✅ {ch.mention}",ephemeral=True)

@tree.command(name="تذاكر")
async def ticket(i: discord.Interaction):
    await i.response.send_message("🎫 اختر:", view=Ticket())

@tree.command(name="ذكاء")
async def ai(i: discord.Interaction, سؤال:str):
    await i.response.send_message(random.choice(["ايه","لا","مدري","ممكن"]))

# ───── حماية + XP ─────
@bot.event
async def on_message(msg):
    if msg.author.bot: return

    user=msg.author
    now=asyncio.get_event_loop().time()

    spam[user.id].append(now)
    spam[user.id]=[t for t in spam[user.id] if now-t<5]

    if len(spam[user.id])>5:
        await msg.delete()

    xp[user.id]+=5
    if xp[user.id]>=levels[user.id]*100:
        xp[user.id]=0
        levels[user.id]+=1
        await msg.channel.send(f"🎉 {user.mention} لفل {levels[user.id]}")

# ───── تشغيل ─────
keep_alive()
bot.run(os.getenv("TOKEN"))
       