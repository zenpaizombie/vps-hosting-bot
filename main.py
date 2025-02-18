import discord
from discord.ext import commands
import subprocess
import json

TOKEN = "YOUR_BOT_TOKEN"
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="/", intents=intents)

# In-memory user credits storage (Use a database in production)
user_credits = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_member_join(member):
    inviter = await get_inviter(member)
    if inviter:
        user_credits[inviter.id] = user_credits.get(inviter.id, 0) + 7
        await inviter.send(f"You earned 7 credits for inviting {member.name}!")

async def get_inviter(member):
    guild = member.guild
    invites_before = await guild.invites()
    invites_after = await guild.invites()
    for invite in invites_after:
        for old_invite in invites_before:
            if invite.code == old_invite.code and invite.uses > old_invite.uses:
                return invite.inviter
    return None

@bot.slash_command(name="free-deploy", description="Deploy a free VPS if you have 70 credits")
async def free_deploy(ctx):
    user = ctx.author
    if user_credits.get(user.id, 0) < 70:
        await ctx.send("You need at least 70 credits to deploy a VPS.", ephemeral=True)
        return
    
    user_credits[user.id] -= 70
    await ctx.send("Deploying your VPS... Check your DMs soon!", ephemeral=True)
    
    tmate_session = deploy_vps()
    await user.send(f"Your VPS is ready! Access it via this Tmate SSH link: {tmate_session}")

def deploy_vps():
    docker_cmd = "docker run -d --rm --memory=8g --cpus=4 --name ryn-i7 ubuntu bash -c 'apt update && apt install -y tmate && tmate -F json'"
    output = subprocess.check_output(docker_cmd, shell=True, text=True)
    try:
        session_data = json.loads(output)
        return session_data['ssh']
    except:
        return "Failed to generate SSH session."

bot.run(TOKEN)
