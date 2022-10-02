import discord
from discord.ext import commands
from discord import app_commands
import datetime
import embedmodule as emm
import settings.settings as set
import asyncio
import random as rand
from string import Template

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!c ', intents=intents)

help_embed = discord.Embed(title="コマンド一覧", color=0xff0000)
help_embed.add_field(name="!j host 部屋名 最大人数(20人まで)", value="自分で部屋をホストすることができます。", inline=False)
help_embed.add_field(name="!j rand", value="今存在する部屋の中からランダムで5個部屋を持ってきます", inline=False)
help_embed.add_field(name="!j join 部屋名", value="参加したい部屋の名前を入力して参加することができます。部屋はroomlistから探すことができます", inline=False)
help_embed.add_field(name="!j leave", value="部屋から離脱することができます。", inline=False)
help_embed.add_field(name="!j chat メッセージ", value="部屋に参加している状態で使用すると、会話することができます。", inline=False)

room = {}
idroom = {}
idname = {}
txtroom = {}
pasw = {}
wel = [Template("${name}がただいま着陸いたしました。"),
       Template("${name}がパーティーに加わりました。"),
       Template("${name}がサーバーに飛び乗りました。"),
       Template("${name}がサーバーに滑り込みました。"),
       Template("${name}、ようこそ。"),
       Template("${name}がやってきました。"),
       Template("${name}が出たぞー！"),
       Template("${name}にご挨拶しな！"),
       Template("${name}、お会いできて何よりです。"),
       Template("いらっしゃい${name}ちゃん。ほら、ちゃんとご挨拶して！"),
       Template("やあ、${name}君。ピザ持ってきたよね？"),
       Template("あ！野生の${name}が飛び出してきた！"),
       Template("やったー、${name}が来たー！"),
       Template("おかえり、${name}宿題はやったよね？"),
       Template("それって${name}の感想ですよね？"), ]
# Template('Message: ${first}, ${second}')
all_channel = []
afkm = False
afk_member = []
verified = set.verify()
sensitive = set.sensitive_word()
txtlimit = set.txtlimit()


def welcome(id):
    title = rand.choice(wel)
    return title.substitute(name=id)


def afkmem():
    afk_member = list(idroom.keys())
    return afk_member


@ bot.event
async def on_ready():
    global afkm
    global afk_member
    global room
    global txtroom
    global idroom
    global idname
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    await bot.change_presence(activity=discord.Game(name=f"サーバー数{len(bot.guilds)}"))
    while (True):
        afkm = False
        await asyncio.sleep(1800)
        afk_member = afkmem()
        afkm = True
        for i in range(len(all_channel)):
            channel = bot.get_channel(all_channel[i])
            await channel.send("放置チェック\n5分以内に「!c afk」を入力してください")
        await asyncio.sleep(300)
        for i in range(len(afk_member)):
            room[idroom[afk_member[i]]].pop(room[idroom[afk_member[i]]].index(afk_member[i]))
            if len(room[idroom[afk_member[i]]]) == 0:
                room.pop(idroom[afk_member[i]])
            all_channel.pop(all_channel.index(txtroom[afk_member[i]]))
            idroom.pop(afk_member[i])
            idname.pop(afk_member[i])
            txtroom.pop(afk_member[i])
            afk_member.pop(afk_member.index(afk_member[i]))


@ bot.command()
async def chat(ctx, message: str):
    if ctx.author == ctx.author.bot:
        return
    if len(message) > txtlimit:
        await ctx.send("文章が長すぎます")
        return
    for i in range(len(sensitive)):
        if sensitive[i] in message:
            await ctx.send("禁止されているワードが含まれています")
            return
    for i in range(len(room[idroom[ctx.author.id]])):
        channel = bot.get_channel(txtroom[room[idroom[ctx.author.id]][i]])
        for j in range(len(verified)):
            if ctx.author.id == verified[j]:
                await channel.send(embed=discord.Embed(title=ctx.author.name + " — 今日\✔ " + str(datetime.datetime.now().strftime('%H:%M')),
                                                       description=message, color=discord.Colour.from_rgb(255, 0, 0)))
            else:
                await channel.send(embed=discord.Embed(title=ctx.author.name + " — 今日 " + str(datetime.datetime.now().strftime('%H:%M')),
                                                       description=message, color=discord.Colour.from_rgb(255, 0, 0)))
    await ctx.send("送信が完了しました。")


@ bot.hybrid_group()
async def host(ctx, name: str):
    if ctx.author.id in idroom:
        await ctx.send(embed=emm.embed("Error", "Error", "すでに他のルームに参加しています"))
        return
    if name not in room:
        room[name] = []
    else:
        embed = emm.embed("Error", "Error", name+"はもうすでに存在しています")
        await ctx.send(embed=embed)
        return
    pasw[name] = ""
    await join(ctx, name)


@ bot.command()
async def join(ctx, name: str, psw=""):
    if ctx.author == ctx.author.bot:
        return
    if ctx.author.id in idroom:
        await ctx.send(embed=emm.embed("Error", "Error", "すでに他のルームに参加しています"))
        return
    if name in room and pasw[name] == psw:
        room[name].append(ctx.author.id)
        idroom[ctx.author.id] = name
        idname[ctx.author.id] = ctx.author.name
        txtroom[ctx.author.id] = ctx.channel.id
        all_channel.append(ctx.channel.id)
        await ctx.send(name + "に参加しました")
        t = welcome(ctx.author.name)
        await chat(ctx, t)
    else:
        await ctx.send("パスワードが一致しません")

'''
@ bot.command()
async def debug(ctx):
    if ctx.author == ctx.author.bot:
        return
    print(idroom)
    print(room)
    print(txtroom)
    print(afk_member)
    print(pasw)
    await ctx.send("表示しました")
'''


@ bot.command()
async def leave(ctx):
    if ctx.author == ctx.author.bot:
        return
    if ctx.author.id in idroom:
        room[idroom[ctx.author.id]].pop(room[idroom[ctx.author.id]].index(ctx.author.id))
        if len(room[idroom[ctx.author.id]]) == 0:
            room.pop(idroom[ctx.author.id])
            await ctx.send("部屋を削除しました")
        all_channel.pop(all_channel.index(txtroom[ctx.author.id]))
        idroom.pop(ctx.author.id)
        idname.pop(ctx.author.id)
        txtroom.pop(ctx.author.id)
        if ctx.author.id in afk_member:
            afk_member.pop(afk_member.index(ctx.author.id))
        await ctx.send("退出しました")
    else:
        await ctx.send("部屋に参加していません")


@ bot.command()
async def afk(ctx):
    if ctx.author == ctx.author.bot:
        return
    if afkm == False:
        await ctx.send("放置チェック時間外です")
        return
    afk_member.pop(afk_member.index(ctx.author.id))
    await ctx.send("放置チェックが完了しました")


@ bot.command()
async def set_pass(ctx, psw):
    if ctx.author == ctx.author.bot:
        return
    if len(psw) < 4:
        await ctx.send("3文字以下のパスワードは使用できません")
        return
    pasw[idroom[ctx.author.id]] = psw
    await ctx.send("パスワードを設定しました")


@ bot.command()
async def random(ctx):
    if ctx.author.bot:
        return
    else:
        key = list(room.keys())
        r = rand.sample(key, min(5, len(room)))
        if len(room) == 0:
            await ctx.send("ルームが存在しません。")
            return ()
        elif len(room) > 5:
            match_embed = discord.Embed(title="ランダムルーム", color=0xff0000)
            for i in range(len(room)):
                match_embed.add_field(name="ルーム名 : "+r[i], value="参加人数 : "+str(len(room[r[i]])), inline=False)
            await ctx.send(embed=match_embed)
        else:
            match_embed = discord.Embed(title="ランダムルーム", color=0xff0000)
            for i in range(len(room)):
                match_embed.add_field(name="ルーム名 : "+r[i], value="参加人数 : "+str(len(room[r[i]])), inline=False)
            await ctx.send(embed=match_embed)

bot.run('TOKEN')
