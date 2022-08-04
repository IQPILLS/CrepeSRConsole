import discord
from discord.ext import commands
import paramiko
from login import username, password, server, distoken
from mongo import get_database

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='>', intents=intents)
bot.remove_command('help')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(server, username=username, password=password)


@bot.command()
async def ping(ctx):
    await ctx.send('pong')


@bot.command()
async def help(ctx):
    await ctx.send('Доступные команды:\n>help\n>account <login>\n>avatar_add <id>\n>scene <planeid>\n>give <itemid> <count> <level>* <rank>* <promotion>*')


@bot.command()
async def account(ctx, login):
    dbname = get_database()
    db = dbname["accounts"]
    item_details = db.find()
    if len(login) <= 16:
        for item in item_details:
            if ctx.message.author.id in item.values():
                await ctx.send('Вы уже зарегистрировали аккаунт.')
                break
            elif login in item.values():
                await ctx.send('Этот логин занят.')
                break
        else:
            await ctx.send('Создаю аккаунт.')
            total_count = db.count_documents({})
            uid = total_count + 1
            add = {
                "discord_id": ctx.message.author.id,
                "uid": uid,
                "login": login}
            db.insert_one(add)
            await ctx.send('Создан аккаунт с логином ' + login + '. Ваш UID: ' + str(uid))
            ssh.exec_command(f'tmux send-keys -t hsr.0 "account create {login} {uid}" ENTER')
    else:
        await ctx.send('Длина логина должна быть меньше 16 символов.')


@bot.command()
async def avatar_add(ctx, avatarid):
    dbname = get_database()
    db = dbname["accounts"]
    item_details = db.find()
    for item in item_details:
        if ctx.message.author.id in item.values():
            uid = item['uid']
            await ctx.send('Добавлен аватар ' + avatarid)
            ssh.exec_command(f'tmux send-keys -t hsr.0 "t {uid}" ENTER')
            ssh.exec_command(f'tmux send-keys -t hsr.0 "avatar add {avatarid}" ENTER')
            ssh.exec_command(f'tmux send-keys -t hsr.0 "t 0" ENTER')
        else: await ctx.send('Вы ещё не создали аккаунт.')


@bot.command()
async def scene(ctx, planeid):
    dbname = get_database()
    db = dbname["accounts"]
    item_details = db.find()
    for item in item_details:
        if ctx.message.author.id in item.values():
            uid = item['uid']
            await ctx.send('Игрок перенесён на сцену ' + planeid)
            ssh.exec_command(f'tmux send-keys -t hsr.0 "t {uid}" ENTER')
            ssh.exec_command(f'tmux send-keys -t hsr.0 "scene {planeid}" ENTER')
            ssh.exec_command(f'tmux send-keys -t hsr.0 "t 0" ENTER')
        else: await ctx.send('Вы ещё не создали аккаунт.')


@bot.command()
async def give(ctx, itemid, count=1, level=1, rank=1, promotion=1):
    dbname = get_database()
    db = dbname["accounts"]
    item_details = db.find()
    for item in item_details:
        if ctx.message.author.id in item.values():
            uid = item['uid']
            ssh.exec_command(f'tmux send-keys -t hsr.0 "t {uid}" ENTER')
            ssh.exec_command(f'tmux send-keys -t hsr.0 "item give {itemid} x{count} l{level} r{rank} p{promotion}" ENTER')
            ssh.exec_command(f'tmux send-keys -t hsr.0 "t 0" ENTER')
            await ctx.send(f'Выдано {count} {itemid} игроку {uid}.')
        else:
            await ctx.send('Вы ещё не создали аккаунт.')
bot.run(distoken)
