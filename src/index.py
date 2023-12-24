from flask import Flask, request, abort
import discord
from discord.ext import commands
import asyncio
import os

app = Flask(__name__)

# domain root
@app.route('/')
def home():
    return 'Hello, World!'

@app.route("/webhook", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

intents = discord.Intents.all()  # 啟用所有意圖
intents.voice_states = True  # 啟用語音狀態意圖，以捕捉使用者加入語音頻道的事件

bot = commands.Bot(command_prefix='@', intents=intents)

status = 'start'

# 要踢掉的身分組名稱
target_role_name = "活該"
# 替換成接收通知的身分組名稱與ID
role_name = "超級新"
role_id = 1188446166464069633
channelNum = 1188445931935383555

@bot.event
async def on_ready():
  print(f'Bot 已登入：{bot.user.name}')
  await bot.change_presence(status=discord.Status.offline)
  #await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name='music | /help'))

@bot.event
async def on_voice_state_update(member, before, after):
  guild = bot.get_guild(689114453354217559)  # 請填入你的伺服器ID
  target_role = discord.utils.get(guild.roles, name=target_role_name)
  role = discord.utils.get(guild.roles, name=role_name)

  global channelNum
  channel = bot.get_channel(channelNum)
  global status

  if role and role in member.roles:
    if before.channel is None and after.channel is not None:  # 使用者加入語音頻道
      status = 'stop'
      await channel.send(f'status = {status}')
    elif before.channel is not None and after.channel is None:  # 使用者離開語音頻道
      status = 'start'
      await channel.send(f'status = {status}')

  if before.channel is None and after.channel is not None:
     role_mention = f'<@&{role_id}>'
     if status == 'start':
        await channel.send(f'{role_mention}\n{member.display_name} 已加入語音頻道。')
     elif status == 'stop':
        await channel.send(f'{member.display_name} 已加入語音頻道。')
  elif before.channel is not None and after.channel is None:
        await channel.send(f'{member.display_name} 已離開語音頻道。')
  elif before.self_mute and not after.self_mute:
        await channel.send(f'{member.display_name} 已取消靜音。')
  elif not before.self_mute and after.self_mute:
        await channel.send(f'{member.display_name} 已靜音。')

  if target_role and target_role in member.roles:
    if after.channel:  # 使用者加入語音頻道
      print(f'{member.display_name} 已加入語音頻道。')
      # 在這裡設定秒數，這裡是1秒，你可以根據需要調整
      await asyncio.sleep(1)
      if member.voice and member.voice.channel:  # 確保使用者仍然在語音頻道中
        await member.move_to(None)  # 立即中斷連線
        print(f'{member.display_name} 已從語音頻道中斷線。')  

@bot.command()
async def start(ctx, *, args=""):
    if ctx.channel.id == channelNum:
        # 在特定頻道中收到命令
        await ctx.send(f'Command received in the specified channel. Start to notify.')
        global status
        status = 'start'

@bot.command()
async def stop(ctx, *, args=""):
    if ctx.channel.id == channelNum:
        # 在特定頻道中收到命令
        await ctx.send(f'Command received in the specified channel. Stop to notify.')
        global status
        status = 'stop'

@bot.command()
async def clear(ctx, arg):
    if ctx.channel.id == channelNum:
        if arg == 'all':
            await ctx.channel.purge()
            await ctx.send('All messages in this channel have been cleared.', delete_after=5)
        elif arg.isdigit():
            amount = int(arg)
            deleted = await ctx.channel.purge(limit=amount + 1)
            await ctx.send(f'{len(deleted) - 1} messages have been cleared.', delete_after=5)
        else:
            await ctx.send('Invalid command or argument.', delete_after=5)
    else:
        await ctx.send('Invalid channel.', delete_after=5)

if __name__ == "__main__":
    app.run()
    # 在這裡使用你的 bot token
    bot.run(os.getenv("TOKEN"))
