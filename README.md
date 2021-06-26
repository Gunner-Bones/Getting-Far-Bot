# Getting Far Bot

A Geometry Dash tool used on Discord for having a Bot deafen the user when they 'get far' on a level at a specified percentage. 

## Installation

This requires installing Python 3.7 or higher.
You will also need to install additional modules for the script:
- `discord` is needed to run a Discord Bot.
- `pynacl` is a dependency for the `discord` module and used for voice.
- `asyncio` provides asyncronous task-related commands.
- `gd.py` is the main Python wrapper for Geometry Dash interaction.
To install a module, in a **Command Prompt** type:
(With the module being the one of these above of course, you need to install all of them.)
```
pip install module_name_here
```
The exception to this is the `gd` module, which is installed in a
slightly different way to get the latest updated version:
```
python pip install --upgrade https://github.com/NeKitDS/gd.py/archive/master.zip
```

## Setup

You need to create a **Discord Bot** to have something to deafen you when you get far in a Geometry Dash level.
My video on [Getting Far Bot 1.0](https://www.youtube.com/watch?v=dlWmOtQ80PM) includes a visual guide on creating a Discord Bot, or
[this doc](https://discordpy.readthedocs.io/en/latest/discord.html) also works. 
These show how to create a Bot and get its essential **Token**.
Once you have the Bot Secret (Token), open `token.txt` and add it next to `TOKEN=`. The file should look like this:
```
TOKEN=wefwrgrwgrggr...
```
In addition, the Bot will only respond to commands if:
1) The Discord account who created the Bot made the command
2) The Bot has a role with the `Administrator` permission

NOTE! As of Discord API v1.5, all bots require enabling Priviledged Intents in order for basic functionality. Make sure to enable
it in your bot's application page by going to Bot > Priviledged Intents and enabling it *or the bot will not work*.

There are also additional setting configurations in `settings.txt`:
- `GETTING_FAR`: What % the bot will Server Deafen you at
- `TIMEOUT`: How long the program will wait during a Pause for a response (10 = 1s)
- `BOT_PREFIX`: Chars before the command name the bot will respond to
- `FAR_CHANNEL`: (Optional) Discord Channel ID to announce deaths past GETTING_FAR. (Bot will handle this)
- `LIST_RQ`: (Optional) (1=On,0=Off) When playing a List Demon, change the GETTING_FAR percentage to its Requirement %. 

## Usage

Once you have installed Python with its required modules, and set up a Discord Bot and linked it to `secret.txt`,
to run the program:
1) Open Geometry Dash
2) Run the script with (or debug if you have a proper IDE):
```
python main.py
```
To turn off the Bot, simply close the script/Command Prompt's window.

### Commands

- `join_call`: Joins the Voice Channel you are currently in. You must be in a Voice Channel to use this command.
- `change_far (integer)`: Changes the GETTING_FAR %.
- `far_channel`: Toggles the channel this command was typed in as a **Far Channel**. The Bot will send messages
to the channel when the user is getting far, has died past the far percentage, or has completed the level.
![Example](https://cdn.discordapp.com/attachments/471765577011036172/747288541654155304/unknown.png)
- `toggle_list`: When playing an Insane/Extreme Demon on the Pointercrate List, toggles whether the bot will
automatically update your GETTING_FAR % to the associated list demon's Requirement %.
