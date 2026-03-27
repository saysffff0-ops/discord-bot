import discord
from discord.ext import commands
from discord.ui import View, Button, Select
import os, asyncio, datetime
from flask import Flask
from threading import Thread
from collections import defaultdict

# ───── keep alive ─────
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

# ───── إعدادات ─────
CHAT_CHANNEL_ID = 123456789  # 🔥 حط ايدي الشات العام

TICKET_TYPES = ["دعم 🛠️","شراء 💰","مشاكل 🎮","اقتراح 💡"]

points = defaultdict(int)
claims = defaultdict(int)
messages = defaultdict(int)

# ───── تشغيل ─────
@bot.event
async def on_ready():
    await tree.sync()
    print("🔥 شغال")

# ───── التذاكر ─────
class TicketButtons(View):
    def __init__(self, owner_id):
        super().__init__(timeout=None)
        self.claimed_by = None
        self.owner_id = owner_id

    @discord.ui.button(label="🙋‍♂️ استلام", style=discord.ButtonStyle.green)
    async def claim(self, i: discord.Interaction, b: Button):

        if i.user.id == self.owner_id:
            return await i.response.send_message("❌ ما تقدر تستلم تذكرتك", ephemeral=True)

        if self.claimed_by:
            return await i.response.send_message(
                f"❌ التذكرة مستلمة من {self.claimed_by.mention}",
                ephemeral=True
            )

        self.claimed_by = i.user
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        # نقاط التذاكر
        claims[i.user.id] += 1
        if claims[i.user.id] % 2 == 0:
            points[i.user.id] += 1

        embed = discord.Embed(
            title="📌 Ticket Claimed",
            description=(
                f"👤 **الإداري المسؤول:** {i.user.mention}\n"
                f"⏰ **وقت الاستلام:** `{now}`\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "📋 تم استلام هذه التذكرة من قبل أحد أعضاء فريق الإدارة المختصين\n"
                "💬 سيتم التعامل مع طلبك في أقرب وقت ممكن\n\n"
                "⚠️ يرجى الالتزام بالقوانين واحترام الإدارة"
            ),
            color=discord.Color.green()
        )

        embed.set_thumbnail(url=i.user.display_avatar.url)
        embed.set_image(url=i.user.display_avatar.url)

        await i.response.send_message(embed=embed)

    @discord.ui.button(label="🔒 إغلاق", style=discord.ButtonStyle.gray)
    async def close(self, i: discord.Interaction, b: Button):
        await i.response.defer()
        await i.channel.delete()

# ───── إنشاء التذكرة ─────
class TicketSelect(Select):
    def __init__(self):
        options=[discord.SelectOption(label=x) for x in TICKET_TYPES]
        super().__init__(placeholder="اختر نوع التذكرة", options=options)

    async def callback(self, i: discord.Interaction):
        await i.response.defer(ephemeral=True)

        name=f"ticket-{i.user.name}"

        if discord.utils.get(i.guild.channels,name=name):
            return await i.followup.send("❌ عندك تذكرة",ephemeral=True)

        overwrites={
            i.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            i.user: discord.PermissionOverwrite(view_channel=True)
        }

        ch=await i.guild.create_text_channel(name, overwrites=overwrites)

        await ch.send(
            f"🎫 {i.user.mention}\nاستخدم الأزرار 👇",
            view=TicketButtons(i.user.id)
        )

        await i.followup.send(f"✅ {ch.mention}",ephemeral=True)

class TicketView(View):
    def __init__(self):
        super().__init__()
        self.add_item(TicketSelect())

@tree.command(name="تذاكر")
async def ticket(i: discord.Interaction):
    await i.response.send_message("🎫 اختر نوع التذكرة:", view=TicketView())

# ───── التفاعل + أفضل إداري ─────
@bot.event
async def on_message(msg):
    if msg.author.bot:
        return

    # التفاعل فقط بالشات العام
    if msg.channel.id == CHAT_CHANNEL_ID:
        messages[msg.author.id] += 1

        if messages[msg.author.id] % 100 == 0:
            points[msg.author.id] += 3
            await msg.channel.send(
                f"🏆 {msg.author.mention} حصل على 3 نقاط للتفاعل!"
            )

    # أفضل إداري
    if msg.content.strip() == "افضل اداري":

        sorted_users = sorted(points.items(), key=lambda x: x[1], reverse=True)

        embed = discord.Embed(
            title="🏆 لوحة أفضل الإداريين",
            description="📊 الترتيب يعتمد على النقاط والتفاعل",
            color=discord.Color.gold()
        )

        medals = ["🥇","🥈","🥉","🏅","🏅"]

        for i, (user_id, pts) in enumerate(sorted_users[:5]):
            try:
                user = await bot.fetch_user(user_id)

                embed.add_field(
                    name=f"{medals[i]} {user.name}",
                    value=f"💎 النقاط: {pts}\n💬 التفاعل: {messages[user_id]} رسالة",
                    inline=False
                )
            except:
                continue

        if sorted_users:
            top_user = await bot.fetch_user(sorted_users[0][0])
            embed.add_field(
                name="👑 أفضل إداري حاليا",
                value=f"{top_user.mention}",
                inline=False
            )
            embed.set_thumbnail(url=top_user.display_avatar.url)

        embed.set_footer(text="🔥 استمر بالمنافسة للوصول للقمة!")

        await msg.channel.send(embed=embed)

    await bot.process_commands(msg)

# ───── تشغيل ─────
keep_alive()
bot.run(os.getenv("TOKEN"))
       