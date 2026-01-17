#IMPORT REQUIRED DEPENDENCIES
import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
from discord import Member
from discord.ext.commands import has_permissions
from discord.ext.commands import MissingPermissions
import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()

LYLAToken = os.getenv("LYLAToken")

BREADAPI= os.getenv("LYLAAPI")
JOKEAPI= os.getenv("LYLAAPI")

queues = {}

def check_queue(ctx, id):
    if queues.get(id, []) != []:
        voice = ctx.guild.voice_client
        source = queues[id].pop(0)
        player = voice.play(source)


client = commands.Bot(command_prefix = '!', intents = discord.Intents.all())

#INDICATES WHEN LYLA IS ONLINE
@client.event
async def on_ready():
    print("Lyla's ready for use!")
    print("----------------------")


#RESPONSE WHEN CALLED
@client.command()
async def lyla(ctx):
    await ctx.send("Hello! I'm your LYrate Lifeform Approximation, but you can call me, LYLA. How may I assist you today?")




#BREADBOX
@client.command()
async def bread(ctx):

    breadurl = "https://breadbox3.p.rapidapi.com/breadbox"

    headers = {
	"X-RapidAPI-Key": BREADAPI,
	"X-RapidAPI-Host": "breadbox3.p.rapidapi.com"
}

    response = requests.get(breadurl, headers=headers)
    crust = response.json()

    await ctx.send(crust['data'])



#LIST OF COMMANDS
@client.command()
async def list(ctx):
    helpmessage = """Here are my available commands:
    
    !lyla - Greet LYLA
    !bread - Get a random bread fact or joke
    !join - Have LYLA join your vc
    !leave - Have LYLA leave your vc
    !play [song name] - Play a song in the vc (must be an mp3 file that LYLA has)
    !pause - Pause the current audio in the vc
    !resume - Resume the paused audio in the vc
    !queue [song name] - Add a song to the queue (must be an mp3 file that LYLA has)
    !kick [@user] - Kick a user from the server (Admin only)
    !ban [@user] - Ban a user from the server (Admin only)
    !unban [user name#discriminator] - Unban a user from the server (Admin only)
    """
    await ctx.send(helpmessage)




#WELCOME MESSAGE WHEN SOMEONE JOINS A SERVER
@client.event
async def on_member_join(member):

    jokeurl = "https://dad-jokes-by-api-ninjas.p.rapidapi.com/v1/dadjokes"

    headers = {
	"x-rapidapi-key": JOKEAPI,
	"x-rapidapi-host": "dad-jokes-by-api-ninjas.p.rapidapi.com"
    }

    response = requests.get(jokeurl, headers=headers)
    data = response.json()

    channel = member.guild.system_channel
    await channel.send("Welcome to the server, <@" + str(member.id) + ">. I'm your new assistant, LYLA! Would you like to hear a joke?")
    await channel.send(data[0]['joke'])


#GOODBYE MESSAGE WHEN SOMEONE LEAVES A SERVER
@client.event
async def on_member_remove(member):
    channel = member.guild.system_channel
    await channel.send("Goodbye, <@" + str(member.id) + ">! Have a lovely day!")


#TRIGGERS TO SPECIFIC WORDS, PHRASES, AND ROLES
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if "happy" in message.content.casefold():
        emoji = '\N{YELLOW HEART}'
        await message.add_reaction(emoji)



    if "nevermind" in message.content.casefold():
        await message.channel.send("Okay!")

    if "thank you lyla" in message.content.casefold():
        await message.channel.send("Anytime!")    
    
    if "thank you, lyla" in message.content.casefold():
        await message.channel.send("Anytime!")



    
    for role in message.role_mentions:
        if role.name.casefold() == "spyders":
            await message.channel.send("Pay attention, people! Important D&D info!")
    
    for role in message.role_mentions:
        if role.name.casefold() == "movies":
            await message.channel.send("Get your popcorn and snacks ready! We're watching a movie!")

    await client.process_commands(message)



#VOICE CHANNEL COMMANDS
@client.command(pass_context  = True)
async def join(ctx):
    if (ctx.author.voice):
        channel = ctx.message.author.voice.channel
        voice = await channel.connect()
        source = FFmpegPCMAudio('Lyla Greeting.wav')
        player = voice.play(source)

    else:
        await ctx.send("You don't meet the koalafications! You must be in the VC to tell me to do this.")

@client.command(pass_context = True)
async def leave(ctx):
    if (ctx.voice_client):
        await ctx.guild.voice_client.disconnect()
        await ctx.send("It was fun talking to you!")
    else:
        await ctx.send("I'm not in the VC")


#COMMANDS FOR AUDIO IN VOICE CHANNELS
@client.command(pass_context = True)
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("There's no audio to pause, silly goose!")

@client.command(pass_context = True)
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("What am I resuming? There's nothing playing.")

@client.command(pass_context = True)
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.stop()
    else:
        await ctx.send("What music am I stopping? There's nothing playing. Are you feeling okay?")

@client.command(pass_context = True)
async def play(ctx, arg):
    song = arg + '.mp3'
    if not os.path.exists(song):
        await ctx.send("I don't have that song! Sorry!")
        return

    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    source = FFmpegPCMAudio(song)
    player = voice.play(source, after=lambda x=None: check_queue(ctx, ctx.message.guild.id))

@client.command(pass_context = True)
async def queue(ctx, arg):
    voice = ctx.guild.voice_client
    song = arg + '.mp3'
    source = FFmpegPCMAudio(song)

    guild_id = ctx.message.guild.id

    if guild_id in queues:
        queues[guild_id].append(source)

    else:
        queues[guild_id] = [source]

    await ctx.send("Added to queue")



#EXCERISING ADMIN PRIVILEGES
@client.command()
@has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'User {member} has been kicked. DUN DUN DUNNNN!')

@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You can't tell me what to do! You're not my Dad!")

@client.command()
@has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'User {member} has been banned. Sucks to suck.')

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You can't tell me what to do! You're not my Dad!")
        
@client.command()
@has_permissions(ban_members=True)
async def unban(ctx, *, user: discord.User):
    await ctx.guild.unban(user)
    await ctx.send(f'User {user} has been unbanned. I missed them!')

@unban.error
async def unban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You can't tell me what to do! You're not my Dad!")








client.run(LYLAToken)

