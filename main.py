from discord.ext import commands
import interactions
from interactions import Intents
from interactions.ext.wait_for import wait_for,setup
from interactions import Message
import sqlite3
import asyncio
import os
import re

Token = ""

inter = interactions.Client(token=Token,intents=Intents.DEFAULT | Intents.GUILD_MESSAGE_CONTENT)
setup(inter)
bot = commands.Bot("!")
bot.remove_command("help")

@inter.command(
    name="dell_word", 
    description="指定されたワードを削除します", 
    options= [
        interactions.Option(
            type=interactions.OptionType.STRING,
            name="select", 
            description="設定", 
            required=False,
            choices=[
                interactions.Choice(name="ON", value="ON"), 
                interactions.Choice(name="OFF", value="OFF"), 
            ], 
        ),
        interactions.Option(
            type=interactions.OptionType.STRING,
            name="word", 
            description="設定", 
            required=False,
            choices=[
                interactions.Choice(name="ワードを追加", value="add"), 
                interactions.Choice(name="ワードを削除", value="dll"), 
            ], 
        ),
    ],
)
async def word_options(ctx: interactions.CommandContext, select=None, word=None):
    if ctx.author.permissions & interactions.Permissions.ADMINISTRATOR:
        guild = await ctx.get_guild()
        guild_id = guild.id

        try:
            conn = sqlite3.connect('data.db')
            c = conn.cursor()
            c.execute('CREATE TABLE guild (id integer primary key, value integer)')
        except:
            pass

        panel_info = [{'id': str(guild_id), 'value': str(select)}]
        conn = sqlite3.connect('data.db')
        c = conn.cursor()
        c.executemany(f'REPLACE INTO guild VALUES (:id, :value)', panel_info)
        conn.commit()
        conn.close()

        if not word == None:
            path = f"word"
            os.makedirs(path, exist_ok=True)
            if word == "add":
                await ctx.send('追加したいワードを入力してください',ephemeral=True)
                async def check(msg):
                    if int(msg.author.id) == int(ctx.author.user.id):
                        return True
                msg: Message = await wait_for(inter, "on_message_create", check=check)
                f = open(f'{path}/{guild_id}.txt','a',encoding="utf-8")
                f.write(f'{msg}\n')
                f.close()
            else:
                await ctx.send('削除したいワードを入力して下さい',ephemeral=True)
                async def check(msg):
                    if int(msg.author.id) == int(ctx.author.user.id):
                        return True
                msg: Message = await wait_for(inter, "on_message_create", check=check)
                with open(f'{path}/{guild_id}.txt') as f:
                    lines = f.readlines()
                    word_list = []
                    for i in lines:
                        i = i.rstrip("\n")
                        if not i == str(msg):
                            word_list.append(i)
                    f = open(f'{path}/{guild_id}.txt', 'w', encoding='UTF-8')
                    f.write("")
                    f.close()
                    for i in word_list:
                        f = open(f'{path}/{guild_id}.txt','a',encoding="utf-8")
                        f.write(f'{i}\n')
                        f.close()

        if not word == None:
            if word == "add":
                await ctx.send(f'設定完了しました\n{msg} を追加しました',ephemeral=True)
            else:
                await ctx.send(f'設定完了しました\n{msg} を削除しました',ephemeral=True)
            await msg.delete()
        else:
            await ctx.send(f'設定完了しました',ephemeral=True)

@bot.event
async def on_message(message):
    guild_id = message.guild.id
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    sql = 'select * from guild'
    for row in c.execute(sql):
        if row[0] == guild_id:
            if row[1] == "ON":
                with open(f'word/{guild_id}.txt') as f:
                    lines = f.readlines()
                for l in lines:
                    l = l.replace('\n','')
                    for i in message.content.split("\n"):
                        result = re.search(l, i)
                        if result:
                            await message.delete()
                        else:
                            pass

lp = asyncio.get_event_loop()
lp.create_task(bot.start(Token))
lp.create_task(inter._ready())
lp.run_forever()