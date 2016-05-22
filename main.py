import discord, settings;
client = discord.Client();

import subprocess;
EMULATOR_PROCESS = subprocess.Popen("visualboyadvance-m pkmn.gb &".split());

import os;
import json;

permittedChannels = [];
try:
	with open("permittedChannels.json", 'r', encoding="utf-8") as file:
		permittedChannels = json.load(file);
except FileNotFoundError:
	print("Permitted channel database doesn't exist, please use !permit on a channel.");

cur_screenshot = 1;

try:
	filelist = [ f for f in os.listdir(".") if f.endswith(".png") ];
	for f in filelist:
		os.remove(f);
except:
	pass;

def cur_screen():
	global cur_screenshot;
	subprocess.call("xdotool keydown --delay 200 d".split());
	subprocess.call("xdotool keyup d".split());
	cur_screenshot += 1;
	return settings.SCREEN_FILE.format('%02d' % (cur_screenshot - 1));

def set_active():
	subprocess.call("xdotool search --desktop 0 --class {0} windowactivate".format(settings.WINDOW_CLASS).split());

def save_state():
	subprocess.call("xdotool key Shift+F1".split());

def bttn_input(bttns):
	keys = {
		"up": "Up",
		"down": "Down",
		"left": "Left",
		"right": "Right",
		"A": "z",
		"B": "x",
		"start": "Return"
	};

	inputs = bttns.split("+");

	for i in range(0, min(len(inputs), 5)):
		parts = inputs[i].strip().split();

		try:
			bttn = parts[0];
		except:
			bttn = inputs[i];

		if bttn not in keys.keys():
			return False;

	for i in range(0, min(len(inputs), 5)):
		parts = inputs[i].strip().split();
		
		amount = 1;
		if len(parts) > 1:
			try:
				amount = int(parts[1]);
			except:
				pass;

		try:
			bttn = parts[0];
		except:
			bttn = inputs[i];

		if amount < 0:
			amount = 1;
		if amount > 5:
			amount = 5;

		if bttn in keys.keys():
			for j in range(0, amount):
				subprocess.call("xdotool keydown --delay 40 {0}".format(keys[bttn]).split());
				subprocess.call("xdotool keyup --delay 40 {0}".format(keys[bttn]).split());
		else:
			return False;

	return inputs;

@client.event
async def on_ready():
	set_active();
	subprocess.call("xdotool keydown --delay 400 Ctrl+l".split());
	subprocess.call("xdotool keyup Ctrl+l".split());
	print("Logged in");

@client.event
async def on_message(message):
	if message.channel.is_private:
		return;

	global permittedChannels;

	content = message.content.strip();

	if message.author.name in settings.ELEVATED_USERS:
		if content == "!permit":
			if message.channel.id not in permittedChannels:
				permittedChannels.append(message.channel.id);
				with open('permittedChannels.json', 'w') as file:
					json.dump(permittedChannels, file);

				print("Can now respond in channel ID " + str(message.channel.id));
				await client.send_message(message.channel, "Now permitted to use *" + message.channel.name + "*");
				return;

		elif content == "!permit remove":
			if message.channel.id in permittedChannels:
				permittedChannels.remove(message.channel.id);
				with open('permittedChannels.json', 'w') as file:
					json.dump(permittedChannels, file);

				print("Can no longer respond in channel ID " + str(message.channel.id));
				await client.send_message(message.channel, "No longer permitted to use *" + message.channel.name + "*");
				return;

	if message.channel.id not in permittedChannels:
		return;

	global cur_screenshot;

	set_active();

	if content == "screen":
		await client.send_file(message.channel, cur_screen());
		return;
	elif content == "save":
		save_state();
		await client.send_file(message.channel, cur_screen(), content="*State saved.*");
		return;

	inputs = bttn_input(content);
	if inputs:
		subprocess.call("sleep .25s".split());
		await client.send_file(message.channel, cur_screen(), content="**" + message.author.name + "**: \n`" + "\n".join(inputs) + "`");

'''
def main_func():
	set_active();
	bttn_input("down");
	subprocess.call("sleep 1s".split());
	cur_screen();

main_func();
'''

client.run(settings.DISCORD_TOKEN);