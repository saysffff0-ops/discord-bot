from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()import discord
from discord.ext import commands
from discord.ui import View, Button, Select
import os, random, asyncio
from collections import defaultdict

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=None, intents=intents)
tree = bot.tree

# ───── بيانات ─────
economy = defaultdict(int)
xp = defaultdict(int)
levels = defaultdict(lambda: 1)
warnings = defaultdict(int)
spam = defaultdict(list)

TICKET_TYPES = ["دعم 🛠️","شراء 💰","مشاكل 🎮","اقتراح 💡"]
SHOP = {"VIP":500, "مميز":300}

# ───── تشغيل ─────
@bot.event
async def on_ready():
    await tree.sync()
    print(f"🔥 {bot.user} شغال")

# ───── أوامر عامة ─────
@tree.command(name="ping", description="سرعة البوت")
async def ping(i: discord.Interaction):
    await i.response.send_message(f"🏓 {round(bot.latency*1000)}ms")

# ───── إدارة ─────
@tree.command(name="حذف", description="حذف رسائل")
async def delete(i: discord.Interaction, عدد:int):
    await i.channel.purge(limit=عدد)
    await i.response.send_message(f"🧹 تم حذف {عدد}", ephemeral=True)

@tree.command(name="باند", description="حظر عضو")
async def ban(i: discord.Interaction, عضو:discord.Member):
    await عضو.ban()
    await i.response.send_message("🔨 تم الباند")

# ───── اقتصاد ─────
@tree.command(name="فلوسي", description="رصيدك")
async def money(i: discord.Interaction):
    await i.response.send_message(f"💰 {economy[i.user.id]}")

@tree.command(name="يومي", description="مكافأة يومية")
async def daily(i: discord.Interaction):
    economy[i.user.id]+=200
    await i.response.send_message("💸 +200")

@tree.command(name="تحويل", description="تحويل فلوس")
async def give(i: discord.Interaction, عضو:discord.Member, مبلغ:int):
    if economy[i.user.id] < مبلغ:
        return await i.response.send_message("❌ فلوسك قليلة")
    economy[i.user.id]-=مبلغ
    economy[عضو.id]+=مبلغ
    await i.response.send_message("✅ تم التحويل")

# ───── متجر ─────
@tree.command(name="المتجر", description="عرض المتجر")
async def shop(i: discord.Interaction):
    msg="\n".join([f"{k} = {v}💰" for k,v in SHOP.items()])
    await i.response.send_message(msg)

@tree.command(name="شراء", description="شراء عنصر")
async def buy(i: discord.Interaction, item:str):
    if item not in SHOP:
        return await i.response.send_message("❌ غير موجود")
    if economy[i.user.id] < SHOP[item]:
        return await i.response.send_message("❌ فلوسك قليلة")
    economy[i.user.id]-=SHOP[item]
    await i.response.send_message(f"✅ اشتريت {item}")

# ───── ألعاب ─────
@tree.command(name="رقم", description="رقم عشوائي")
async def num(i: discord.Interaction):
    await i.response.send_message(f"🎲 {random.randint(1,100)}")

# ───── لفلات ─────
@tree.command(name="لفلي", description="عرض لفلك")
async def lvl(i: discord.Interaction):
    await i.response.send_message(f"🎖️ {levels[i.user.id]}")

# ───── تذاكر ─────
class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

class TicketSelect(Select):
    def __init__(self):
        options=[discord.SelectOption(label=x) for x in TICKET_TYPES]
        super().__init__(placeholder="اختر نوع التذكرة", options=options)

    async def callback(self, i: discord.Interaction):
        name=f"ticket-{i.user.name}"
        if discord.utils.get(i.guild.channels,name=name):
            return await i.response.send_message("❌ عندك تذكرة",ephemeral=True)

        overwrites={
            i.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            i.user: discord.PermissionOverwrite(view_channel=True)
        }

        ch=await i.guild.create_text_channel(name, overwrites=overwrites)
        await ch.send(f"🎫 {i.user.mention}")
        await i.response.send_message(f"✅ {ch.mention}",ephemeral=True)

@tree.command(name="تذاكر", description="فتح تذكرة")
async def ticket(i: discord.Interaction):
    await i.response.send_message("🎫 اختر:", view=TicketView())

# ───── ذكاء بسيط ─────
@tree.command(name="ذكاء", description="رد عشوائي")
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
        warnings[user.id]+=1

    xp[user.id]+=5
    if xp[user.id]>=levels[user.id]*100:
        xp[user.id]=0
        levels[user.id]+=1
        await msg.channel.send(f"🎉 {user.mention} لفل {levels[user.id]}")

# تشغيل
keep_alive()bot.run(os.getenv("TOKEN"))