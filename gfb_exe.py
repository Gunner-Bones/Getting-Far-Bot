import gd
import time
import sys
import os
import discord
import nacl
import libnacl
import asyncio
import random
import json
import ctypes
import ctypes.util
import urllib.request as request
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

def corePYIPath(relative):
    return os.path.join(
        os.environ.get(
            "_MEIPASS2",
            os.path.abspath(".")
        ),
        relative
    )

def datasettings(file,method,line="",newvalue="",newkey=""):
	"""
	:param file: (str).txt
	:param method: (str) get,change,remove,add
	:param line: (str)
	:param newvalue: (str)
	:param newkey: (str)
	"""
	file = corePYIPath(file)
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


print("="*30)
print("GETTING FAR BOT v2")
print("By GunnerBones")
print("="*30)
print("-"*30)
BOT_PREFIX = "??"
print("[Input] BOT_PREFIX=" + BOT_PREFIX)
print("[Input] (Optional) Enter symbol prefix for your Discord Bot (Enter to use default).")
temp = input("BOT_PREFIX:")
if temp != "":
	BOT_PREFIX = temp
	print("[Input] BOT_PREFIX=" + BOT_PREFIX)
print("-"*30)
print("[Input] Enter your Discord Bot's SECRET (Refer to the README if you're unsure what that is).")
temp = input("BOT_SECRET:")
BOT_SECRET = temp
print("\n."*40)
print("[Input] BOT_SECRET entered and hidden.")
print("Running bot...")


Client = discord.Client()
client = commands.Bot(command_prefix=BOT_PREFIX)
client.remove_command("help")


BOT_OWNER = None
TIMEOUT = 30
GETTING_FAR = 30
FAR_CHANNEL = []
LIST_RQ = 0
WHITELIST = []


DEAFEN = False
VOICE_SESSION = None
SCANNING = False
LIST_RF = []
WHITEON = False
CURRENT_LEVEL = 0


def requestPCDemonRequirement(level_name):
	global LIST_RF
	if not LIST_RF:
		url1 = "https://pointercrate.com/api/v1/demons/?limit=100"
		url2 = "https://pointercrate.com/api/v1/demons/?after=100"
		req1 = request.urlopen(url1)
		req2 = request.urlopen(url2)
		rd1 = req1.read()
		rd2 = req2.read()
		js1 = json.loads(rd1.decode("utf-8"))
		js2 = json.loads(rd2.decode("utf-8"))
		demons = js1 + js2
		LIST_RF = sorted(demons, key=lambda j: j['position'])
		print("[Getting Far] Pointercrate Demon List refreshed.")
	for demon in LIST_RF:
		if demon['name'] == level_name:
			return int(demon['requirement'])
	return 30

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
	global LIST_RQ
	pflm = ""
	if LIST_RQ:
		pflm = ", List Requirement!"
	pi = {"far": "**" + BOT_OWNER.name + "** is *getting far* on **__" + level_name + "__ by "
	 + level_creator + "**...  (" + str(GETTING_FAR) + "%+" + pflm + ")",
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
				print("[Getting Far] Joined voice channel '" + ctx.author.voice.channel.name + "'")
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


@client.command(pass_context=True)
async def toggle_list(ctx):
	global LIST_RQ
	if bot_permissions(ctx):
		if bot_owner(ctx):
			LIST_RQ = abs(LIST_RQ - 1)
			if LIST_RQ:
				await response_message(ctx, "Scanning for List Demon Requirement % turned `ON`.", "success")
				print("[Getting Far] LIST_RQ turned ON")
			else:
				await response_message(ctx, "Scanning for List Demon Requirement % turned `OFF`.", "success")
				print("[Getting Far] LIST_RQ turned OFF")
			datasettings(file="settings.txt", method="change", line="LIST_RQ" , newvalue=str(LIST_RQ))
		else:
			await response_message(ctx,"","failed","author_not_owner")
	else:
		await response_message(ctx,"","failed","bot_lacks_perms")


@client.command(pass_context=True)
async def toggle_whitelist(ctx):
	global WHITEON
	if bot_permissions(ctx):
		if bot_owner(ctx):
			if not WHITEON:
				await response_message(ctx, "Whitelist turned `ON`.", "success")
				WHITEON = True
				print("[Getting Far] USE WHITELIST turned ON")

			else:
				await response_message(ctx, "Whitelist turned `OFF`.", "success")
				WHITEON = False
				print("[Getting Far] USE WHITELIST turned OFF")
		else:
			await response_message(ctx,"","failed","author_not_owner")
	else:
		await response_message(ctx,"","failed","bot_lacks_perms")


@client.command(pass_context=True)
async def whitelist_level(ctx):
	global WHITEON
	global WHITELIST
	global CURRENT_LEVEL
	if bot_permissions(ctx):
		if bot_owner(ctx):
			if CURRENT_LEVEL:
				if CURRENT_LEVEL not in WHITELIST:
					WHITELIST.append(CURRENT_LEVEL)
					await response_message(ctx, "`" + str(CURRENT_LEVEL) + "` added to WHITELIST.", "success")
					print("[Getting Far] " + str(CURRENT_LEVEL) + " added to WHITELIST")
				else:
					WHITELIST.remove(CURRENT_LEVEL)
					await response_message(ctx, "`" + str(CURRENT_LEVEL) + "` removed from WHITELIST.", "success")
					print("[Getting Far] " + str(CURRENT_LEVEL) + " removed from WHITELIST")
				datasettings(file="settings.txt", method="change", line="WHITELIST", newvalue=str(WHITELIST))
			else:
				await response_message(ctx, "You're not currently playing a level!", "failed")
		else:
			await response_message(ctx,"","failed","author_not_owner")
	else:
		await response_message(ctx,"","failed","bot_lacks_perms")


@client.command(pass_context=True)
async def change_far(ctx, num):
	global GETTING_FAR
	if bot_permissions(ctx):
		if bot_owner(ctx):
			if is_num(num):
				perc = int(num)
				if 1 < perc < 100:
					GETTING_FAR = perc
					datasettings(file="settings.txt", method="change", line="GETTING_FAR", newvalue=str(perc))
					await response_message(ctx, "GETTING FAR % changed to *" + str(perc) + "*.", "success")
					print("[Getting Far] GETTING_FAR=" + str(perc) + "%")
				else:
					await response_message(ctx, "Number must be between 1-100!", "failed")
			else:
				await response_message(ctx, "*" + num + "* is not a number!", "failed")
		else:
			await response_message(ctx,"","failed","author_not_owner")
	else:
		await response_message(ctx,"","failed","bot_lacks_perms")


"""@client.command(pass_context=True)
async def change_prefix(ctx, st):
	global BOT_PREFIX
	if bot_permissions(ctx):
		if bot_owner(ctx):
			if st.replace(" ","") != "":
				BOT_PREFIX = st
				await response_message(ctx, "BOT_PREFIX changed to `" + str(st) + "`.", "success")
				print("[Getting Far] BOT_PREFIX=" + str(st))
			else:
				await response_message(ctx, "Prefix cannot be blank!", "failed")
		else:
			await response_message(ctx,"","failed","author_not_owner")
	else:
		await response_message(ctx,"","failed","bot_lacks_perms") """

# This probably does not work post bot startup


@client.event
async def on_voice_state_update(member,before,after):
	global SCANNING
	global VOICE_SESSION
	if member.id == BOT_OWNER and not after.channel:
		SCANNING = False
		await VOICE_SESSION.disconnect()
		print("[Getting Far] Left voice channel.")
		VOICE_SESSION = None


async def main():
	global SCANNING
	global VOICE_SESSION
	global DEAFEN
	global BOT_OWNER
	global LIST_RQ
	global GETTING_FAR
	global WHITELIST
	global WHITEON
	global CURRENT_LEVEL
	# can't have this many globals with a global pandemic going on haha
	level_name = "None"
	level_creator = "None"
	level_best = 0
	memory = None
	await client.wait_until_ready()
	try:
		memory = gd.memory.get_memory()
	except RuntimeError:
		print("[ERROR] Geometry Dash needs to be open! Exiting in 5s.")
		time.sleep(5)
		sys.exit("Geometry Dash needs to be running.")
	try:
		if memory.is_in_level():
			level_name = memory.get_level_name()
			level_creator = memory.get_level_creator()
			level_best = memory.get_normal_percent()
			CURRENT_LEVEL = memory.get_level_id_fast()
			await client.change_presence(activity=discord.Game(name=BOT_OWNER.name + " has " + str(level_best)
				 + "% on " + level_name + " by " + level_creator))
			print("[Getting Far] Level data generated: " + level_name + " by " + level_creator)
		else:
			CURRENT_LEVEL = 0
	except AttributeError:
		pass
	alive = True
	victory = False
	changed_rq = False
	while True:
		if SCANNING and memory.is_in_level():
			level_name = memory.get_level_name()
			level_creator = memory.get_level_creator()
			level_best = memory.get_normal_percent()
			CURRENT_LEVEL = memory.get_level_id_fast()
			if WHITEON and WHITELIST and CURRENT_LEVEL not in WHITELIST:
				await asyncio.sleep(0.5)
				continue
			if LIST_RQ and not changed_rq:
				if memory.get_level_stars() == 10 and memory.get_level_demon_difficulty_value() >= 5:
					new_requirement = requestPCDemonRequirement(level_name)
					GETTING_FAR = new_requirement
					datasettings(file="settings.txt", method="change", line="GETTING_FAR", newvalue=str(new_requirement))
					changed_rq = True
					print("[Getting Far] LIST_RQ on, detected List Demon '" + level_name + 
						"' with Requirement " + str(new_requirement) + "%")
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
					print("[Getting Far] User DIED FAR! " + str(round(memory.get_percent())) + "% on '" + level_name + "', Attempt " + str(memory.get_attempt()))
			if not memory.is_dead() and not alive:
				alive = True
			if memory.get_percent() == 100 and not victory:
				victory = True
				await VOICE_SESSION.guild.get_member(BOT_OWNER.id).edit(deafen=False)
				await sendout_message(message_type="win", level_name=level_name, level_creator=level_creator)
				print("[Getting Far] User WON!!!")
		elif not memory.is_in_level():
			victory = False
			changed_rq = False
			CURRENT_LEVEL = 0
		await asyncio.sleep(0.5)


client.loop.create_task(main())
try:
	client.run(BOT_SECRET)
except discord.errors.LoginFailure:
	print("[ERROR] Invalid BOT_SECRET! Exiting in 5s.")
	time.sleep(5)
	sys.exit()