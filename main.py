import gd
import time
import sys
import discord
import asyncio
import random
import ctypes
import ctypes.util
from discord.ext import commands

"""lib_opus = ["libopus-0.x64.dll","libopus-0.x86.dll"]
if not discord.opus.is_loaded():
	for lib in lib_opus:
		discord.opus.load_opus(lib)"""

CHAR_SUCCESS = "✅"
CHAR_FAILED = "❌"
MES_DEATH = [
	"Ouch! ",
	"Yikes. ",
	"DANG! ",
	"Oh no.. ",
	"RIP. ",
	"☹️ ",
	"😬 ",
	"A tragedy. ",
	"Unfortunate. ",
	"LOL HAHAHAHA ",
	"NO WAY WHAT!!!! ",
	"L "
]
MES_WIN = [
	"GG! ",
	"GGGGG!! ",
	"INCREDIBLE! ",
	"Congradulations! ",
	"yeah easy ok ",
	"Insane! ",
	"ABSOLUTELY CRACKED!!! ",
	"YOU\'RE OFF THE GOOP! ",
	"You win! ",
	"Winner! ",
	"You did it! ",
	"Incredible! ",
	"Ok. ",
	"Jesse, did you just beat a Demon level? ",
	"After a mental breakdown.. "
]

def is_num(a):
	try:
		a = int(a)
		return True
	except ValueError:
		return False

def strtolist(s):
    if str(s) == "[]" or str(s) == "['']": return []
    st = str(s).replace("[",""); st = st.replace("]",""); st = st.replace("'",""); st = st.split(",")
    for t in st:
        if t.startswith(" "): st[st.index(t)] = t[1:]
        if is_num(t):
        	st[st.index(t)] = int(t)
    return st

def datasettings(file,method,line="",newvalue="",newkey=""):
	"""
	:param file: (str).txt
	:param method: (str) get,change,remove,add
	:param line: (str)
	:param newvalue: (str)
	:param newkey: (str)
	"""
	s = None
	try: s = open(file,"r")
	except: return None
	sl = []
	for l in s: sl.append(l.replace("\n",""))
	for nl in sl:
		if str(nl).startswith(line):
			if method == "get": s.close(); return str(nl).replace(line + "=","")
			elif method == "change": sl[sl.index(nl)] = line + "=" + newvalue; break
			elif method == "remove": sl[sl.index(nl)] = None; break
	if method == "add": sl.append(newkey + "=" + newvalue)
	if method == "get": return None
	s.close()
	s = open(file,"w")
	s.truncate()
	slt = ""
	for nl in sl:
		if nl is not None:
			slt += nl + "\n"
	s.write(slt); s.close(); return None


Client = discord.Client()
bot_prefix = datasettings(file="settings.txt",method="get",line="BOT_PREFIX")
client = commands.Bot(command_prefix=bot_prefix)
client.remove_command("help")

BOT_SECRET = datasettings(file="secret.txt",method="get",line="BOT_SECRET")
if BOT_SECRET == "lol" or not BOT_SECRET:
	print("[Error] BOT_SECRET in secret.txt needs to be set to bot's secret")
	print("Shutting down...")
	time.sleep(5)
	sys.exit()
BOT_OWNER = None
TIMEOUT = int(datasettings(file="settings.txt",method="get",line="TIMEOUT"))
GETTING_FAR = int(datasettings(file="settings.txt",method="get",line="GETTING_FAR"))
FAR_CHANNEL = strtolist(datasettings(file="settings.txt",method="get",line="FAR_CHANNEL"))


DEAFEN = False
VOICE_SESSION = None
SCANNING = False


async def response_message(ctx, response, message_reaction, preset=""):
	if preset != "":
		pi = {"author_not_owner":"You are not the Owner of this Bot!",
			  "bot_lacks_perms":client.user.name + " does not have Permissions to perform this!",
			  "invalid_params":"Invalid parameters!"}
		response = pi[preset]
	await ctx.message.channel.send("**" + ctx.author.name + "**, " + response)
	mri = {"success":CHAR_SUCCESS,"failed":CHAR_FAILED}
	await ctx.message.add_reaction(mri[message_reaction])

async def sendout_message(message_type, level_name, level_creator, level_perc=""):
	global FAR_CHANNEL
	pi = {"far": "**" + BOT_OWNER.name + "** is *getting far* on **__" + level_name + "__ by "
	 + level_creator + "**...  (" + str(GETTING_FAR) + "%+)",
	"dead": random.choice(MES_DEATH) + "**" + BOT_OWNER.name + "** just died at *" + level_perc
	 + "%* on **__" + level_name + "__ by " + level_creator + "**.",
	 "win": random.choice(MES_WIN) + "**" + BOT_OWNER.name + "** just completed **__"
	  + level_name + "__ by " + level_creator + "**! 🥳🥳"}
	message = pi[message_type]
	for c in FAR_CHANNEL:
		channel = client.get_channel(c)
		if channel:
			try:
				await channel.send(message)
			except discord.errors.Forbidden:
				pass
	return True


def bot_permissions(ctx):
	if not ctx.message.guild: return True
	for member in ctx.guild.members:
		if str(member.id) == str(client.user.id):
			for role in member.roles:
				if role.permissions.administrator: return True
	return False

def bot_owner(ctx):
	return ctx.author.id == BOT_OWNER.id


@client.event
async def on_ready():
	global BOT_OWNER
	print("[Discord] Bot Connected!")
	print("[Discord] Name=" + client.user.name)
	print("[Discord] User ID=" + str(client.user.id))
	app_info = asyncio.create_task(client.application_info())
	BOT_OWNER = await app_info
	BOT_OWNER = BOT_OWNER.owner
	print("[Discord] Bot Owner ID=" + str(BOT_OWNER.id))
	print("[Getting Far] GETTING_FAR=" + str(GETTING_FAR) + "%")
	await client.change_presence(activity=discord.Game(name="Geometry Dash with " + BOT_OWNER.name))
	for guild in client.guilds:
		for vc in guild.voice_channels:
			for member in vc.members:
				if member.id == client.user.id:
					voice_state = await member.voice.channel.connect(reconnect=True)
					await voice_state.disconnect()
					break

@client.command(pass_context=True)
async def join_call(ctx):
	global SCANNING
	global VOICE_SESSION
	if bot_permissions(ctx):
		if bot_owner(ctx):
			if ctx.author.voice:
				VOICE_SESSION = await ctx.author.voice.channel.connect(reconnect=True)
				SCANNING = True
				await response_message(ctx,"Joined Voice Channel `" + ctx.author.voice.channel.name +
									   "`. Bot is now monitoring your screen.","success")
			else:
				await response_message(ctx,"You are not in a Voice Channel!","failed")
		else:
			await response_message(ctx,"","failed","author_not_owner")
	else:
		await response_message(ctx,"","failed","bot_lacks_perms")


@client.command(pass_context=True)
async def far_channel(ctx):
	global FAR_CHANNEL
	if bot_permissions(ctx):
		if bot_owner(ctx):
			if ctx.channel.id in FAR_CHANNEL:
				FAR_CHANNEL.remove(ctx.channel.id)
				await response_message(ctx, "Removed `" + ctx.channel.name + "` from *FAR_CHANNEL* list.", "success")
			else:
				FAR_CHANNEL.append(ctx.channel.id)
				await response_message(ctx, "Added `" + ctx.channel.name + "` to *FAR_CHANNEL* list.", "success")
			datasettings(file="settings.txt", method="change", line="FAR_CHANNEL" , newvalue=str(FAR_CHANNEL))
		else:
			await response_message(ctx,"","failed","author_not_owner")
	else:
		await response_message(ctx,"","failed","bot_lacks_perms")

@client.event
async def on_voice_state_update(member,before,after):
	global SCANNING
	global VOICE_SESSION
	if member.id == BOT_OWNER and not after.channel:
		SCANNING = False
		await VOICE_SESSION.disconnect()
		VOICE_SESSION = None


async def main():
	global SCANNING
	global VOICE_SESSION
	global DEAFEN
	global BOT_OWNER
	level_name = "None"
	level_creator = "None"
	level_best = 0
	memory = None
	await client.wait_until_ready()
	try:
		memory = gd.memory.get_memory()
	except RuntimeError:
		sys.exit("[Error] Geometry Dash needs to be open!")
	try:
		if memory.is_in_level():
			level_name = memory.get_level_name()
			level_creator = memory.get_level_creator()
			level_best = memory.get_normal_percent()
			await client.change_presence(activity=discord.Game(name=BOT_OWNER.name + " has " + str(level_best)
				 + "% on " + level_name + " by " + level_creator))
			print("[Getting Far] Level data generated: " + level_name + " by " + level_creator)
	except AttributeError:
		pass
	alive = True
	victory = False
	while True:
		if SCANNING and memory.is_in_level():
			level_name = memory.get_level_name()
			level_creator = memory.get_level_creator()
			level_best = memory.get_normal_percent()
			if not DEAFEN and memory.get_percent() >= GETTING_FAR and not memory.is_dead():
				DEAFEN = True
				await VOICE_SESSION.guild.get_member(BOT_OWNER.id).edit(deafen=True)
				await client.change_presence(activity=discord.Game(name=BOT_OWNER.name + " is GETTING FAR!"))
				await sendout_message(message_type="far", level_name=level_name, level_creator=level_creator)
				print("[Getting Far] User is GETTING FAR!")
			elif memory.is_dead() and alive:
				alive = False
				if DEAFEN:
					DEAFEN = False
					await VOICE_SESSION.guild.get_member(BOT_OWNER.id).edit(deafen=False)
				await client.change_presence(activity=discord.Game(name=BOT_OWNER.name + " has " + str(level_best)
		 + "% on " + level_name + " by " + level_creator))
				if memory.get_percent() >= GETTING_FAR:
					await sendout_message(message_type="dead", level_name=level_name, level_creator=level_creator, 
						level_perc=str(round(memory.get_percent())))
				print("[Getting Far] User DIED!")
			if not memory.is_dead() and not alive:
				alive = True
			if memory.get_percent() == 100 and not victory:
				victory = True
				await VOICE_SESSION.guild.get_member(BOT_OWNER.id).edit(deafen=False)
				await sendout_message(message_type="win", level_name=level_name, level_creator=level_creator)
				print("[Getting Far] User WON!!!")
		elif not memory.is_in_level():
			victory = False
		await asyncio.sleep(0.5)


client.loop.create_task(main())
client.run(BOT_SECRET)