import discord
from discord.ext import commands
from discord.ui import View, Button, Select
import os
import random
import asyncio
from collections import defaultdict

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

warnings = defaultdict(int)
spam_tracker = defaultdict(list)

bad_words = ["سب", "قذر", "كلب", "وصخ"]
links = ["http", "https", "discord.gg"]

economy = {}
xp = {}
levels = {}

TICKET_TYPES = [
    "دعم 🛠️",
    "شراء 💰",
    "مشاكل 🎮",
    "اقتراح 💡"
]

# ───── تشغيل ─────
@bot.event
async def on_ready():
    print(f"🔥 {bot.user} شغال")

# ───── التذاكر ─────
class TicketSelect(View):
    def __init__(self):
        super().__init__(timeout=None)
        options = [discord.SelectOption(label=t) for t in TICKET_TYPES]
        self.add_item(SelectMenu(options))

class SelectMenu(Select):
    def __init__(self, options):
        super().__init__(placeholder="اختر نوع التذكرة", options=options)

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user
        category = self.values[0]

        name = f"ticket-{user.name}"

        if discord.utils.get(guild.channels, name=name):
            await interaction.response.send_message("❌ عندك تذكرة مفتوحة", ephemeral=True)
            return

        support_role = discord.utils.get(guild.roles, name="Support")

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        if support_role:
            overwrites[support_role] = discord.PermissionOverwrite(view_channel=True)

        channel = await guild.create_text_channel(name, overwrites=overwrites)

        embed = discord.Embed(
            title="🎫 تذكرة جديدة",
            description=f"النوع: {category}\n{user.mention}",
            color=discord.Color.green()
        )

        await channel.send(embed=embed, view=CloseTicket())
        await interaction.response.send_message(f"✅ {channel.mention}", ephemeral=True)

class CloseTicket(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="إغلاق التذكرة 🔒", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, button: Button):
        channel = interaction.channel

        messages = []
        async for msg in channel.history(limit=100):
            messages.append(f"{msg.author}: {msg.content}")

        transcript = "\n".join(messages[::-1])
        file = discord.File(fp=bytes(transcript, "utf-8"), filename="transcript.txt")

        await interaction.response.send_message("📁 تم حفظ التذكرة", file=file)
        await channel.delete()

@bot.command()
async def تذاكر(ctx):
    await ctx.send("🎫 اختر نوع التذكرة:", view=TicketSelect())

# ───── أوامر ─────
@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 {round(bot.latency*1000)}ms")

@bot.command()
async def هلا(ctx):
    await ctx.send("هلا والله 👋")

@bot.command()
async def قول(ctx, *, كلام):
    await ctx.send(كلام)

# ───── إدارة ─────
@bot.command()
@commands.has_permissions(manage_messages=True)
async def حذف(ctx, عدد: int):
    await ctx.channel.purge(limit=عدد)

@bot.command()
@commands.has_permissions(kick_members=True)
async def طرد(ctx, member: discord.Member):
    await member.kick()

@bot.command()
@commands.has_permissions(ban_members=True)
async def باند(ctx, member: discord.Member):
    await member.ban()

# ───── اقتصاد ─────
@bot.command()
async def فلوسي(ctx):
    await ctx.send(f"💰 {economy.get(ctx.author.id, 0)}")

@bot.command()
async def يومي(ctx):
    economy[ctx.author.id] = economy.get(ctx.author.id, 0) + 100
    await ctx.send("💸 استلمت 100")

# ───── ألعاب ─────
@bot.command()
async def رقم(ctx):
    await ctx.send(f"🎲 {random.randint(1,10)}")

# ───── لفلات ─────
@bot.command()
async def لفلي(ctx):
    await ctx.send(f"🎖️ {levels.get(ctx.author.id, 1)}")

# ───── حماية + XP ─────
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user = message.author
    now = asyncio.get_event_loop().time()

    spam_tracker[user.id].append(now)
    spam_tracker[user.id] = [t for t in spam_tracker[user.id] if now - t < 5]

    if len(spam_tracker[user.id]) > 5:
        await message.delete()
        warnings[user.id] += 1

    if any(link in message.content.lower() for link in links):
        await message.delete()

    if any(word in message.content.lower() for word in bad_words):
        await message.delete()

    xp[user.id] = xp.get(user.id, 0) + 5
    level = levels.get(user.id, 1)

    if xp[user.id] >= level * 100:
        xp[user.id] = 0
        levels[user.id] = level + 1
        await message.channel.send(f"🎉 {user.mention} لفل {level+1}")

    await bot.process_commands(message)

# تشغيل
bot.run(os.getenv("TOKEN"))