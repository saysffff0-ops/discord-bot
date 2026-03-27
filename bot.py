import discord
from discord.ext import commands, tasks
from discord import app_commands
import os, json, time

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# ========= إعدادات =========
AUTO_PROMOTE = True
AUTO_DEMOTE = True

POINTS_PER_MESSAGE = 1
POINTS_PER_TICKET = 1

PROMOTE_POINTS = 500
DEMOTE_DAYS = 7

SUPPORT_ROLE_NAME = "Support Team"   # غيره لاسم رول الدعم عندك
LOG_CHANNEL_NAME = "logs"           # قناة اللوق

ROLE_HIERARCHY = [
    "⚜️【Management】 TC⚜️",
    "✦『Helper』 TC✦",
    "⟡《Trial Staff》 TC⟡",
    "⟦Staff⟧ TC",
    "✦『Senior Staff』 TC✦",
    "⚜️【Supervisor】 TC⚜️",
    "⟡《Admin》 TC⟡",
    "⚜️【Manager】 TC⚜️"
]

DATA_FILE = "points.json"
ECON_FILE = "economy.json"

# ========= تحميل =========
def load(file):
    try:
        with open(file) as f:
            return json.load(f)
    except:
        return {}

def save(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

points = load(DATA_FILE)
economy = load(ECON_FILE)

def add_points(uid, amount):
    uid = str(uid)
    if uid not in points:
        points[uid] = {"points": 0, "last": time.time(), "tickets": 0}

    points[uid]["points"] += amount
    points[uid]["last"] = time.time()
    save(DATA_FILE, points)

def get_points(uid):
    return points.get(str(uid), {}).get("points", 0)

# ========= تشغيل =========
@bot.event
async def on_ready():
    await tree.sync()
    check_members.start()
    print(f"🔥 Ready: {bot.user}")

# ========= نقاط من الشات =========
@bot.event
async def on_message(msg):
    if msg.author.bot:
        return

    if msg.author.guild_permissions.manage_messages:
        add_points(msg.author.id, POINTS_PER_MESSAGE)

    await bot.process_commands(msg)

# ========= Leaderboard =========
@tree.command(name="top", description="Top admins")
async def top(interaction: discord.Interaction):
    data = sorted(points.items(), key=lambda x: x[1]["points"], reverse=True)[:10]
    txt = ""
    for i,(uid,d) in enumerate(data,1):
        m = interaction.guild.get_member(int(uid))
        if m:
            txt += f"{i}. {m.mention} - {d['points']}\n"

    embed = discord.Embed(title="🏆 Top Admins", description=txt, color=discord.Color.gold())
    await interaction.response.send_message(embed=embed)

# ========= تذاكر =========
class TicketView(discord.ui.View):
    def __init__(self, owner_id):
        super().__init__(timeout=None)
        self.owner_id = owner_id
        self.claimed_by = None

    @discord.ui.button(label="👨‍💼 Claim", style=discord.ButtonStyle.green)
    async def claim(self, interaction: discord.Interaction, b):
        if interaction.user.id == self.owner_id:
            return await interaction.response.send_message("❌ ما تقدر تستلم تذكرتك", ephemeral=True)

        if self.claimed_by:
            return await interaction.response.send_message("❌ مستلمة", ephemeral=True)

        self.claimed_by = interaction.user
        guild = interaction.guild
        channel = interaction.channel
        owner = guild.owner

        await channel.set_permissions(guild.default_role, read_messages=False)
        await channel.set_permissions(interaction.user, read_messages=True)
        await channel.set_permissions(owner, read_messages=True)

        add_points(interaction.user.id, POINTS_PER_TICKET)

        try:
            await interaction.user.send(f"💰 نقاطك: {get_points(interaction.user.id)}")
        except:
            pass

        await interaction.response.send_message(f"📌 {interaction.user.mention} استلم التذكرة")

    @discord.ui.button(label="🔄 Transfer", style=discord.ButtonStyle.blurple)
    async def transfer(self, interaction: discord.Interaction, b):
        await interaction.response.send_message("✏️ اكتب منشن الإداري")

    @discord.ui.button(label="🔒 Close", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, b):
        await interaction.response.send_message("🔒 جاري الإغلاق...")
        await interaction.channel.delete()

class CreateTicket(discord.ui.View):
    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.green)
    async def create(self, interaction: discord.Interaction, b):
        g = interaction.guild
        overwrites = {
            g.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True)
        }

        ch = await g.create_text_channel(f"ticket-{interaction.user.name}", overwrites=overwrites)
        await ch.send("🎫 تذكرتك", view=TicketView(interaction.user.id))
        await interaction.response.send_message(f"✅ {ch.mention}", ephemeral=True)

@tree.command(name="ticketsetup", description="Ticket setup")
async def ticketsetup(interaction: discord.Interaction):
    embed = discord.Embed(title="🎫 Tickets", description="Create ticket", color=discord.Color.green())
    await interaction.channel.send(embed=embed, view=CreateTicket())
    await interaction.response.send_message("✅ Done", ephemeral=True)

# ========= ترقية =========
async def promote(member):
    if not AUTO_PROMOTE:
        return
    pts = get_points(member.id)
    if pts < PROMOTE_POINTS:
        return

    for i,name in enumerate(ROLE_HIERARCHY):
        role = discord.utils.get(member.guild.roles, name=name)
        if role in member.roles and i+1 < len(ROLE_HIERARCHY):
            new = discord.utils.get(member.guild.roles, name=ROLE_HIERARCHY[i+1])
            await member.add_roles(new)
            return

# ========= نزول =========
async def demote(member):
    if not AUTO_DEMOTE:
        return

    uid = str(member.id)
    if uid not in points:
        return

    last = points[uid]["last"]
    days = (time.time()-last)/86400

    if days < DEMOTE_DAYS:
        return

    for i,name in enumerate(ROLE_HIERARCHY):
        role = discord.utils.get(member.guild.roles, name=name)
        if role in member.roles and i-1 >= 0:
            new = discord.utils.get(member.guild.roles, name=ROLE_HIERARCHY[i-1])
            await member.remove_roles(role)
            await member.add_roles(new)
            return

# ========= فحص =========
@tasks.loop(hours=12)
async def check_members():
    for g in bot.guilds:
        for m in g.members:
            await promote(m)
            await demote(m)

# ========= تشغيل =========
bot.run(os.getenv("TOKEN"))