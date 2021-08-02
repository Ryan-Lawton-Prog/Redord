from config import MongoDataBase
import discord
from discord.ext import commands
import asyncio
from prawcore import NotFound
import praw
import json
import os

DB = MongoDataBase()

bot = discord.Client()

description = '''A reddit bot poster'''

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='?', description=description, intents=intents)

with open(os.path.dirname(os.path.realpath(__file__))+'/config.json') as f:
  data = json.load(f)

reddit = praw.Reddit(
    user_agent=data['user_agent'],
    client_id=data['client_id'],
    client_secret=data['client_secret'],
    username=data['username'],
    password=data['password'],
    check_for_async=data['check_for_async']
)

TOKEN = data['TOKEN']

def sub_exists(sub):
    exists = True
    try:
        reddit.subreddits.search_by_name(sub, exact=True)
    except NotFound:
        exists = False
    return exists



"""
BOT EVENTS
"""
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    bot.loop.create_task(post_messages())

async def post_messages():
    #await bot.wait_until_ready()
    while True:
        subreddits = DB.get_collection("subreds")

        print(subreddits)

        for subreddit in subreddits.find():
            print(subreddit)
            sub_db = DB.get_collection(subreddit['name'])
            for message in sub_db.find({'used':False}):
                print(message)
                for channel in subreddit['channels']:
                    print("%s\n%s\n%s" % (message['title'], message['url'], message['permalink']))
                    discord_channel = bot.get_channel(channel['CHANNEL_ID'])

                    await discord_channel.send("%s\n%s\n%s" % (message['title'], message['url'], message['permalink']))

                message['used'] = True
                sub_db.replace_one({'_id':message['_id']}, message)
        
        await asyncio.sleep(60) # task runs every 60 seconds



"""
BOT COMMANDS
"""
@bot.command()
async def subscribe(ctx, subreddit_name: str, channel_name: str):
    #print("command",subreddit_name,channel_name)
    if not sub_exists(subreddit_name):
        await ctx.send("invalid subreddit")
        return

    subreddits = DB.get_collection("subreds")

    new_channel = {}

    channel_found = False
    for channel in ctx.guild.channels:
        if channel.name == channel_name:
            new_channel['CHANNEL_ID'] = channel.id
            channel_found = True
    if not channel_found: 
        await ctx.send("channel not found")
        return
    
    new_channel['SERVER_ID'] = ctx.message.guild.id

    subreddit = subreddits.find_one({'name': subreddit_name})
    if subreddit:
        channels = subreddit['channels']
        channels.append(new_channel)
        sub = {'name'}
        subreddits.replace_one({'name': subreddit_name}, {'name': subreddit_name, 'channels': channels})
    else:
        channel = {'name': subreddit_name, 'channels': [new_channel]}
        subreddits.insert_one(channel)
    
    await ctx.send("channel %s subscribed to %s" % (channel_name, subreddit_name))


@bot.command()
async def unsubscribe(ctx, subreddit_name: str, channel_name: str):
    subreddits = DB.get_collection("subreds")

    channel_query = {}

    for channel in ctx.guild.channels:
        if channel.name == channel_name:
            channel_query['CHANNEL_ID'] = channel.id
            channel_found = True

    if not channel_found: 
        await ctx.send("channel not found")
        return

    channel_query['SERVER_ID'] = ctx.message.guild.id

    subreddit = subreddits.find_one({'name': subreddit_name})
    if subreddit:
        channels = subreddit['channels']
        try:
            channels.remove(channel_query)
            subreddits.replace_one({'name': subreddit_name}, {'name': subreddit_name, 'channels': channels})
        except:
            await ctx.send("subreddit not subscribed currently")
            return
    else:
        await ctx.send("subreddit not subscribed currently")
        return

    await ctx.send("%s unsubscribed from %s" % (channel_name, subreddit_name))

while True:
    bot.run(TOKEN)