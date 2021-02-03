import datetime
import json
import os
from datetime import datetime, timedelta, timezone

from discord import Embed
from discord.ext import commands
from dotenv import load_dotenv
from selenium import webdriver

load_dotenv()
TOKEN = os.getenv('TOKEN')
ARCH = os.getenv('ARCH')

webdriver_options = webdriver.ChromeOptions()
webdriver_options.add_argument('headless')
executable_path = 'chromedriver.exe' if ARCH.upper(
).startswith('WIN') else 'chromedriver'

client = commands.Bot(command_prefix='!', help_command=None)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('==================================================')


def log_message(ctx):
    content = ctx.message.content
    author = ctx.message.author
    print(content, 'by', author)


def log_error(ctx):
    content = ctx.message.content
    author = ctx.message.author
    print('ERROR:', content, 'by', author)


def upcoming_ctf_list(count):
    if int(count) < 1:
        raise Exception

    driver = webdriver.Chrome(executable_path, options=webdriver_options)
    driver.get(f'https://ctftime.org/api/v1/events/?limit={count}')
    response = driver.find_element_by_css_selector('body').text
    response_dict = json.loads(response)

    data = []
    for row in response_dict:
        row_parsed = {'title': row['title'], 'description': row['description'],
                      'start': datetime.fromisoformat(row['start']).astimezone(timezone(timedelta(hours=9))), 'finish': datetime.fromisoformat(row['finish']).astimezone(timezone(timedelta(hours=9))), 'logo': row['logo'], 'url': row['url']}
        data.append(row_parsed)

    driver.close()
    return data


@ client.command()
async def upcoming(ctx):
    log_message(ctx)
    content = ctx.message.content
    parsed_message = content.split()

    data = []
    if len(parsed_message) >= 2:
        data = upcoming_ctf_list(parsed_message[1])
    else:
        data = upcoming_ctf_list(1)

    for datum in data:
        description = datum['description']
        if len(description) > 200:
            description = description[:200]
            description += '...'
        embed = Embed(
            title=datum['title'], description=description, url=datum['url'])
        embed.set_thumbnail(url=datum['logo'])
        embed.add_field(name='Start', value=datum['start'])
        embed.add_field(name='Finish', value=datum['finish'])
        await ctx.send(embed=embed)


@ client.command()
async def help(ctx):
    content = ''
    content += '!upcoming <max_count(default: 1)>'
    await ctx.send('```' + content + '```')


@ client.event
async def on_command_error(ctx, error):
    print(error)
    log_error(ctx)
    await ctx.send('사용할 수 없는 명령어입니다.')

client.run(TOKEN)