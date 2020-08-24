import cv2
import numpy as np
import pytesseract
import time
import sys
import discord
import asyncio
from discord.ext import commands
from PIL import ImageGrab
from ctypes import windll
user32 = windll.user32
user32.SetProcessDPIAware()

lib_opus = ["libopus-0.x64.dll","libopus-0.x86.dll"]
if not discord.opus.is_loaded():
    for lib in lib_opus:
        discord.opus.load_opus(lib)

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract'
CHAR_SUCCESS = "✅"
CHAR_FAILED = "❌"

def has_letter(a):
    for letter in a:
        if letter.isalpha(): return True
    return False

def is_number(a):
    try: a = int(a)
    except: return False
    return True

def remove_letters(a):
    s = ""
    for letter in a:
        if not letter.isalpha() and is_number(letter): s += letter
    return s

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
BOT_OWNER = int(datasettings(file="settings.txt",method="get",line="BOT_OWNER"))
if BOT_OWNER == 0:
    print("[Error] BOT_OWNER in settings.txt needs to be set to bot's owner user ID")
    print("Shutting down...")
    time.sleep(5)
    sys.exit()


WINDOW_TYPE = datasettings(file="settings.txt",method="get",line="WINDOW_TYPE")
TIMEOUT = int(datasettings(file="settings.txt",method="get",line="TIMEOUT"))

GETTING_FAR = int(datasettings(file="settings.txt",method="get",line="GETTING_FAR"))

async def response_message(ctx,response,message_reaction,preset=""):
    if preset != "":
        pi = {"author_not_owner":"You are not the Owner of this Bot!",
              "bot_lacks_perms":client.user.name + " does not have Permissions to perform this!",
              "invalid_params":"Invalid parameters!"}
        response = pi[preset]
    await ctx.message.channel.send("**" + ctx.author.name + "**, " + response)
    mri = {"success":CHAR_SUCCESS,"failed":CHAR_FAILED}
    await ctx.message.add_reaction(mri[message_reaction])

def bot_permissions(ctx):
    if not ctx.message.guild: return True
    for member in ctx.guild.members:
        if str(member.id) == str(client.user.id):
            for role in member.roles:
                if role.permissions.administrator: return True
    return False

def bot_owner(ctx):
    return ctx.author.id == BOT_OWNER

percentage_list_x = {"WINDOWED-1360":1310,"FULL-SCREEN":1310}
percentage_list_y = {"WINDOWED-1360":25,"FULL-SCREEN":25}
percentage_list_off_x = {"WINDOWED-1360":120,"FULL-SCREEN":120}
percentage_list_off_y = {"WINDOWED-1360":60,"FULL-SCREEN":60}
""""
level_name_list_x = {"WINDOWED-1360":210}
level_name_list_y = {"WINDOWED-1360":25}
level_name_list_off_x = {"WINDOWED-1360":1300}
level_name_list_off_y = {"WINDOWED-1360":100}
level_best_list_x = {"WINDOWED-1360":870}
level_best_list_y = {"WINDOWED-1360":250}
level_best_list_off_x = {"WINDOWED-1360":150}
level_best_list_off_y = {"WINDOWED-1360":80}
"""
identifier_paused_list_x = {"WINDOWED-1360":1220,"FULL-SCREEN":1220}
identifier_paused_list_y = {"WINDOWED-1360":800,"FULL-SCREEN":800}
identifier_paused_list_off_x = {"WINDOWED-1360":120,"FULL-SCREEN":120}
identifier_paused_list_off_y = {"WINDOWED-1360":60,"FULL-SCREEN":60}
identifier_menu_list_x = {"WINDOWED-1360":800,"FULL-SCREEN":800}
identifier_menu_list_y = {"WINDOWED-1360":550,"FULL-SCREEN":550}
identifier_menu_list_off_x = {"WINDOWED-1360":310,"FULL-SCREEN":310}
identifier_menu_list_off_y = {"WINDOWED-1360":60,"FULL-SCREEN":60}
identifier_creator_list_x = {"WINDOWED-1360":1310,"FULL-SCREEN":1310}
identifier_creator_list_y = {"WINDOWED-1360":870,"FULL-SCREEN":870}
identifier_creator_list_off_x = {"WINDOWED-1360":300,"FULL-SCREEN":300}
identifier_creator_list_off_y = {"WINDOWED-1360":60,"FULL-SCREEN":60}


GAME_STATE = 0 #0=In Level 1=Paused 2=Menu
#LEVEL_STATE = 0 #0=Progressing 1=Died
CURRENT_PERCENTAGE = -1
#LEVEL_BEST = -1
#LEVEL_NAME = ""

DEAFEN = False
VOICE_SESSION = None
SCANNING = False
CYCLES_PASSED = 0

# Debug
PRINT_GLOBALS = False
SHOW_PERCENTAGE = True
#SHOW_LEVEL_NAME = False
#SHOW_LEVEL_BEST = False
SHOW_IDENTIFIER_PAUSED = False
SHOW_IDENTIFIER_MENU = False
SHOW_IDENTIFIER_CREATOR = False

@client.event
async def on_ready():
    print("[Discord] Bot Connected!")
    print("[Discord] Name=" + client.user.name)
    print("[Discord] User ID=" + str(client.user.id))
    print("[Discord] Bot Owner ID=" + str(BOT_OWNER))
    print("[Getting Far] GETTING_FAR=" + str(GETTING_FAR) + "%")
    await client.change_presence(activity=discord.Game(name="Geometry Dash with " + client.get_user(BOT_OWNER).name))
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

@client.event
async def on_voice_state_update(member,before,after):
    global SCANNING
    global VOICE_SESSION
    if member.id == BOT_OWNER and not after.channel:
        SCANNING = False
        await VOICE_SESSION.disconnect()
        VOICE_SESSION = None


def percentage_process(image):
    global CURRENT_PERCENTAGE
    global CYCLES_PASSED
    global TIMEOUT
    global GAME_STATE
    processed_img = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    txt = pytesseract.image_to_string(processed_img)
    if not has_letter(txt) and txt != "" and "%" in txt:
        txt = txt.replace("%","")
        num = -1
        try: num = int(txt)
        except: pass
        if num != -1: CURRENT_PERCENTAGE = num
    else: CYCLES_PASSED += 1
    if CYCLES_PASSED >= TIMEOUT:
        CURRENT_PERCENTAGE = -1
        CYCLES_PASSED = 0
    if CURRENT_PERCENTAGE != -1:
        GAME_STATE = 0
    if PRINT_GLOBALS:
        print("=============================")
        print("[Debug] CURRENT_PERCENTAGE=" + str(CURRENT_PERCENTAGE))
        #print("[Debug] percentage_process txt=" + txt)
    return processed_img
"""
placeholder_level_name = ""

def level_name_process(image):
    global GAME_STATE
    global LEVEL_NAME
    global placeholder_level_name
    processed_img = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    txt = pytesseract.image_to_string(processed_img)
    if GAME_STATE == 2 and txt != "":
        placeholder_level_name = txt
    if GAME_STATE < 2:
        LEVEL_NAME = placeholder_level_name
    if PRINT_GLOBALS:
        print("[Debug] LEVEL_NAME=" + LEVEL_NAME)
        print("[Debug] level_name_process txt=" + txt)
    return processed_img

def level_best_process(image):
    global GAME_STATE
    global LEVEL_BEST
    global LEVEL_STATE
    global CURRENT_PERCENTAGE
    processed_img = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    txt = pytesseract.image_to_string(processed_img)
    if GAME_STATE == 0 and txt != "" and "%" in txt:
        txt = txt.replace("%",""); txt = txt.replace(" ","")
        txt = remove_letters(txt)
        num = -1
        try: num = int(txt)
        except: pass
        if num != -1 and (CURRENT_PERCENTAGE - 3) <= num <= (CURRENT_PERCENTAGE + 3) and LEVEL_STATE == 0:
            LEVEL_BEST = num
            LEVEL_STATE = 1
    if PRINT_GLOBALS:
        print("[Debug] LEVEL_BEST=" + str(LEVEL_BEST))
        print("[Debug] LEVEL_STATE=" + str(LEVEL_STATE))
        #print("[Debug] level_best_process txt=" + txt)
    return processed_img
"""
def identifier_paused_process(image):
    global GAME_STATE
    processed_img = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    txt = pytesseract.image_to_string(processed_img)
    if txt.lower() == "sfx": GAME_STATE = 1
    if PRINT_GLOBALS:
        print("[Debug] GAME_STATE=" + str(GAME_STATE))
    return processed_img

def identifier_menu_process(image):
    global GAME_STATE
    processed_img = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    txt = pytesseract.image_to_string(processed_img)
    if txt.lower() == "normal mode": GAME_STATE = 2
    return processed_img

def identifier_creator_process(image):
    global GAME_STATE
    processed_img = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    txt = pytesseract.image_to_string(processed_img)
    if "verified" in txt.lower() or "uploaded" in txt.lower(): GAME_STATE = 2
    return processed_img


async def main():
    global SCANNING
    global VOICE_SESSION
    global DEAFEN
    global GAME_STATE
    global WINDOW_TYPE
    #global LEVEL_NAME
    #global LEVEL_BEST
    #global LEVEL_STATE
    await client.wait_until_ready()
    #status_changed = False
    while True:
        if SCANNING:
            percentage_x = percentage_list_x[WINDOW_TYPE]
            percentage_y = percentage_list_y[WINDOW_TYPE]
            percentage_off_x = percentage_list_off_x[WINDOW_TYPE]
            percentage_off_y = percentage_list_off_y[WINDOW_TYPE]

            percentage_img = np.array(ImageGrab.grab(bbox=(percentage_x, percentage_y, percentage_x + percentage_off_x,
                                                percentage_y + percentage_off_y)))
            percentage_img = np.array(percentage_img)
            percentage_img = percentage_process(percentage_img)
            if SHOW_PERCENTAGE:
                cv2.imshow('Percentage', percentage_img)
                cv2.namedWindow("Percentage", cv2.WINDOW_NORMAL)
                cv2.resizeWindow("Percentage", 400, 100)
            """
            level_name_x = level_name_list_x[WINDOW_TYPE]
            level_name_y = level_name_list_y[WINDOW_TYPE]
            level_name_off_x = level_name_list_off_x[WINDOW_TYPE]
            level_name_off_y = level_name_list_off_y[WINDOW_TYPE]
            level_name_img = np.array(ImageGrab.grab(bbox=(level_name_x, level_name_y, level_name_x + level_name_off_x,
                                                           level_name_y + level_name_off_y)))
            level_name_img = np.array(level_name_img)
            level_name_img = level_name_process(level_name_img)
            if SHOW_LEVEL_NAME:
                cv2.imshow('Level Name', level_name_img)
                cv2.namedWindow("Level Name", cv2.WINDOW_NORMAL)
                cv2.resizeWindow("Level Name", 1700, 500)
    
            level_best_x = level_best_list_x[WINDOW_TYPE]
            level_best_y = level_best_list_y[WINDOW_TYPE]
            level_best_off_x = level_best_list_off_x[WINDOW_TYPE]
            level_best_off_y = level_best_list_off_y[WINDOW_TYPE]
            level_best_img = np.array(ImageGrab.grab(bbox=(level_best_x, level_best_y, level_best_x + level_best_off_x,
                                                           level_best_y + level_best_off_y)))
            level_best_img = np.array(level_best_img)
            level_best_img = level_best_process(level_best_img)
            if SHOW_LEVEL_BEST:
                cv2.imshow('Level Best', level_best_img)
                cv2.namedWindow("Level Best", cv2.WINDOW_NORMAL)
                cv2.resizeWindow("Level Best", 600, 600)
            """
            identifier_paused_x = identifier_paused_list_x[WINDOW_TYPE]
            identifier_paused_y = identifier_paused_list_y[WINDOW_TYPE]
            identifier_paused_off_x = identifier_paused_list_off_x[WINDOW_TYPE]
            identifier_paused_off_y = identifier_paused_list_off_y[WINDOW_TYPE]
            identifier_paused_img = np.array(ImageGrab.grab(bbox=(identifier_paused_x, identifier_paused_y,
                                                                  identifier_paused_x + identifier_paused_off_x,
                                                                  identifier_paused_y + identifier_paused_off_y)))
            identifier_paused_img = np.array(identifier_paused_img)
            identifier_paused_img = identifier_paused_process(identifier_paused_img)
            if SHOW_IDENTIFIER_PAUSED:
                cv2.imshow('Paused Identifier', identifier_paused_img)
                cv2.namedWindow("Paused Identifier", cv2.WINDOW_NORMAL)
                cv2.resizeWindow("Paused Identifier", 400, 100)

            identifier_menu_x = identifier_menu_list_x[WINDOW_TYPE]
            identifier_menu_y = identifier_menu_list_y[WINDOW_TYPE]
            identifier_menu_off_x = identifier_menu_list_off_x[WINDOW_TYPE]
            identifier_menu_off_y = identifier_menu_list_off_y[WINDOW_TYPE]
            identifier_menu_img = np.array(ImageGrab.grab(bbox=(identifier_menu_x, identifier_menu_y,
                                                                identifier_menu_x + identifier_menu_off_x,
                                                                identifier_menu_y + identifier_menu_off_y)))
            identifier_menu_img = np.array(identifier_menu_img)
            identifier_menu_img = identifier_menu_process(identifier_menu_img)
            if SHOW_IDENTIFIER_MENU:
                cv2.imshow('Menu Identifier', identifier_menu_img)
                cv2.namedWindow("Menu Identifier", cv2.WINDOW_NORMAL)
                cv2.resizeWindow("Menu Identifier", 400, 100)

            identifier_creator_x = identifier_creator_list_x[WINDOW_TYPE]
            identifier_creator_y = identifier_creator_list_y[WINDOW_TYPE]
            identifier_creator_off_x = identifier_creator_list_off_x[WINDOW_TYPE]
            identifier_creator_off_y = identifier_creator_list_off_y[WINDOW_TYPE]
            identifier_creator_img = np.array(ImageGrab.grab(bbox=(identifier_creator_x, identifier_creator_y,
                                                                   identifier_creator_x + identifier_creator_off_x,
                                                                   identifier_creator_y + identifier_creator_off_y)))
            identifier_creator_img = np.array(identifier_creator_img)
            identifier_creator_img = identifier_creator_process(identifier_creator_img)
            if SHOW_IDENTIFIER_CREATOR:
                cv2.imshow('Creator Identifier', identifier_creator_img)
                cv2.namedWindow("Creator Identifier", cv2.WINDOW_NORMAL)
                cv2.resizeWindow("Creator Identifier", 400, 100)

            """
            if GAME_STATE < 2 and not status_changed and LEVEL_BEST != -1 and LEVEL_NAME != "":
                #await client.change_presence(activity=discord.Game(name=LEVEL_NAME + " (" + str(LEVEL_BEST) + "%)"))
                status_changed = True
            elif GAME_STATE == 2: status_changed = False
            if LEVEL_STATE == 1:
                #await client.change_presence(activity=discord.Game(name=LEVEL_NAME + " (" + str(LEVEL_BEST) + "%)"))
                LEVEL_STATE = 0
            """
            if CURRENT_PERCENTAGE >= GETTING_FAR and GAME_STATE == 0:
                DEAFEN = True
                await VOICE_SESSION.guild.get_member(BOT_OWNER).edit(deafen=True)
            if DEAFEN and (CURRENT_PERCENTAGE >= 99 or GAME_STATE > 0) and CURRENT_PERCENTAGE != -1:
                DEAFEN = False
                await VOICE_SESSION.guild.get_member(BOT_OWNER).edit(deafen=False)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
        await asyncio.sleep(0.5)

client.loop.create_task(main())
client.run(BOT_SECRET)