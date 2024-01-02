from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import discord, asyncio
import yt_dlp as youtube_dl
import random
import os

from table2ascii import table2ascii as t2a, PresetStyle
from discord.ext import commands

import pandas as pd

import requests
import urllib.request

from bs4 import BeautifulSoup
from gtts import gTTS


# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


# youtube 음악과 로컬 음악의 재생을 구별하기 위한 클래스 작성.
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume = 0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


# 음악 재생 클래스. 커맨드 포함.
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['재생','틀어','틀어줘','불러','불러줘'])
    async def play(self, ctx, *, url):
        """Streams from a url (same as yt, but doesn't predownload)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

        ctx.voice_client.source.volume = self.YOU_Volume
        await ctx.send(f'"{player.title} "을 재생하겠다냥! ')

    @commands.command(aliases=['볼륨','소리'])
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        self.YOU_Volume = volume / 100
        ctx.voice_client.source.volume = self.YOU_Volume
        await ctx.send(f"음악 볼륨을 {volume}%로 변경했다냥!")

    @commands.command(aliases=['정지', '멈춰'])
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()

    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("냥냥이가 채널을 찾다가 길을 잃어버렸습니다..")
                raise commands.CommandError("냥냥이가 채널을 찾다가 길을 잃어버렸습니다..")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()


### 초기화

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("&"),
    help_command=None,
    description='Nyan Nyan',
    intents=intents
)


### 데이터 파트
pd.set_option('display.float_format', '{:.0f}'.format)
pd.set_option('display.width', 1000)  # 열 너비 자동 조정

df1 = pd.read_excel('data.xlsx', sheet_name = 'Growth') # 성장의 비약
df2 = pd.read_excel('data.xlsx', sheet_name = 'Point') # EXP쿠폰
df3 = pd.read_excel('data.xlsx', sheet_name = 'Extreme') # 익스트림 몬스터파크
df4 = pd.read_excel('data.xlsx', sheet_name = 'Option') # 추옵표
df6 = pd.read_excel('data.xlsx', sheet_name = 'Hexa') # 6차전직표

TTS_Volume = 1
YOU_Volume = 1

### 함수 파트


def remove_decimal_from_list(input_list):
    """
    리스트에서 숫자 데이터의 소수점을 제거하는 함수
    :param input_list: 처리할 리스트
    :return: 소수점이 제거된 리스트
    """
    result_list = []
    for item in input_list:
        if isinstance(item, (int, float)):
            # 숫자 데이터인 경우만 소수점 제거 후 결과 리스트에 추가
            result_list.append(int(item))
        else:
            # 숫자가 아닌 경우 그대로 결과 리스트에 추가
            result_list.append(item)
    return result_list

def dice():
    a = random.randrange(1,7)
    b = random.randrange(1,7)
    if a > b:
        return "패배", 0xFF0000, str(a), str(b)
    elif a == b:
        return "무승부", 0xFAFA00, str(a), str(b)
    elif a < b:
        return "승리", 0x00ff56, str(a), str(b)

def distribution(N, amount):

    dist = amount/(N-0.05)

    return dist

def number_to_korean(num):
    units = ['', '만', '억', '조', '경']
    result = ''

    for i in range(len(units)):
        current_num = num % 10000
        if current_num != 0:
            result = str(current_num) + units[i] + result
        num //= 10000

    return result

def EXPcal(startlevel, endlevel=0):

    if endlevel == 0:
        value = df2.at[startlevel-200, 'EXPPoint']
        return value

    i = j = 0
    start = startlevel-200
    end = endlevel-200
    sum1 = sum2 = 0

    while i < start:
        value = df2.at[i, 'EXPPoint']
        sum1 += value
        i += 1

    while j < end:
        value = df2.at[j, 'EXPPoint']
        sum2 += value
        j += 1

    return abs(sum2 - sum1)

def EXPPotion(level):
    if level < 200:
        return 0
    value = df1.at[level-200, 'Percent']
    return round(value*100, 3)

def Extreme(level):
    if level < 260:
        return 0

    value1 = df3.at[level-260, 'Percent']
    return round(value1, 3)

def Option(Search):
    target_name = Search
    result = df4[df4['Weapon'] == target_name]
    selected_row = df4.iloc[result.index]
    new_df = pd.DataFrame(selected_row)
    return new_df

def Erase(input_string):

    # 괄호 안에 있는 문자 제거
    output_string = ""
    inside_bracket = False  # 괄호 안에 있는지 여부를 추적하기 위한 플래그

    for char in input_string:
        if char == '(':
            inside_bracket = True
        elif char == ')':
            inside_bracket = False
            continue  # 괄호 안의 문자는 제거하고 넘어감
        elif not inside_bracket:
            output_string += char

    return output_string

def Character(Search):
    user = Search
    url = "https://maple.gg/u/" + user
    response = requests.get(url)
    html = response.text

    # BeautifulSoup을 사용하여 HTML 파싱
    soup = BeautifulSoup(html, 'html.parser')

    try:
        level = soup.find_all('li', class_='user-summary-item')[1].text
    except IndexError:
        level = "-"

    world = soup.find('li', class_='user-summary-item').text

    # level = soup.find('span', class_='user-summary-level')
    try:
        guild = soup.find('a', class_='text-yellow text-underline').text
    except AttributeError:
        guild = "-"

    try:
        job = soup.find_all('li', class_='user-summary-item')[2].text
    except IndexError:
        job = "-"



    try:
        union = soup.find('span', class_='user-summary-level').text
        search_char = "업적"

        if search_char in union:
            union = "-"

    except AttributeError:
        union = "-"

    try:
        floor = soup.find('h1', class_='user-summary-floor').text
        floor = floor.replace(" ", "")
        floor = floor.replace("\n", "")
    except AttributeError:
        floor = "-"
        floor = floor.replace("\n", "")

    try:
        seed = soup.find_all('h1', class_='user-summary-floor')[1].text
        seed = seed.replace(" ", "")
        seed = seed.replace("\n", "")
    except IndexError:
        seed = "-"
        seed = seed.replace("\n", "")

    try:
        score = soup.find_all('span', class_='user-summary-level')[1].text
        score = ''.join(char for char in score if char.isdigit())
        score = score + "점"
    except IndexError:
        score = "-"
        score = seed.replace("\n", "")

    img_tag = soup.find('img', class_="character-image")
    image_src = img_tag.get('src')

    return level, job, world, guild, union, floor, image_src



def Conversion(Search):
    driver = webdriver.Chrome()
    user = Search
    url = 'https://maplescouter.com/info?name=' + user
    driver.get(url)

    wait = WebDriverWait(driver, 10)
    element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'flex')))

    # 데이터 추출
    combPW = driver.find_element(By.XPATH,
                                 '//*[@id="root"]/div/div[1]/div[2]/div[2]/div[2]/div[1]/div[1]/div[3]/div[2]')
    combPW = combPW.text

    convST = driver.find_element(By.XPATH,
                                 '//*[@id="root"]/div/div[1]/div[2]/div[2]/div[2]/div[1]/div[1]/div[4]/div/div[3]/div[1]')
    convST = convST.text

    hexaST = driver.find_element(By.XPATH,
                                 '//*[@id="root"]/div/div[1]/div[2]/div[2]/div[2]/div[1]/div[1]/div[5]/div/div[3]/div[1]')
    hexaST = hexaST.text

    img_element = driver.find_element(By.XPATH,
                                      '//*[@id="root"]/div/div[1]/div[2]/div[2]/div[2]/div[1]/div[1]/div[2]/img')
    img_src = img_element.get_attribute('src')

    return combPW, convST, hexaST, img_src

def Hexa(startlevel, endlevel=0):
    if startlevel < 1 :
        return 0, 0, 0, 0, 0, 0
    if startlevel > 29:
        return 0, 0, 0, 0, 0, 0

    if endlevel == 0:
        Sol6 = df6.at[startlevel-1, 'SixSol']
        Sol5 = df6.at[startlevel-1, 'FiveSol']
        Sol4 = df6.at[startlevel-1, 'FourSol']
        Piece6 = df6.at[startlevel-1, 'SixPiece']
        Piece5 = df6.at[startlevel-1, 'FivePiece']
        Piece4 = df6.at[startlevel-1, 'FourPiece']

        return Sol6, Piece6, Sol5, Piece5, Sol4, Piece4

    start = startlevel-1
    end = endlevel-1

    i = j = 0
    sum1 = sum2 = 0

    while i < start:
        value = df6.at[i, 'SixSol']
        sum1 += value
        i += 1

    while j < end:
        value = df6.at[j, 'SixSol']
        sum2 += value
        j += 1

    Sol6 = sum2 - sum1
    i = j = 0
    sum1 = sum2 = 0

    while i < start:
        value = df6.at[i, 'SixPiece']
        sum1 += value
        i += 1

    while j < end:
        value = df6.at[j, 'SixPiece']
        sum2 += value
        j += 1

    Piece6 = sum2 - sum1
    i = j = 0
    sum1 = sum2 = 0

    while i < start:
        value = df6.at[i, 'FiveSol']
        sum1 += value
        i += 1

    while j < end:
        value = df6.at[j, 'FiveSol']
        sum2 += value
        j += 1

    Sol5 = sum2 - sum1
    i = j = 0
    sum1 = sum2 = 0

    while i < start:
        value = df6.at[i, 'FivePiece']
        sum1 += value
        i += 1

    while j < end:
        value = df6.at[j, 'FivePiece']
        sum2 += value
        j += 1

    Piece5 = sum2 - sum1
    i = j = 0
    sum1 = sum2 = 0

    while i < start:
        value = df6.at[i, 'FourSol']
        sum1 += value
        i += 1

    while j < end:
        value = df6.at[j, 'FourSol']
        sum2 += value
        j += 1

    Sol4 = sum2 - sum1
    i = j = 0
    sum1 = sum2 = 0

    while i < start:
        value = df6.at[i, 'FourPiece']
        sum1 += value
        i += 1

    while j < end:
        value = df6.at[j, 'FourPiece']
        sum2 += value
        j += 1

    Piece4 = sum2 - sum1
    i = j = 0
    sum1 = sum2 = 0

    return Sol6, Piece6, Sol5, Piece5, Sol4, Piece4

### 명령어 설정 파트


@bot.command()
async def 냥냥(message):
    await message.channel.send('냥냥! 무엇을 도와드릴까요?')

@bot.command()
async def 주사위(ctx):
    await ctx.reply("도전을 받아들이겠다냥!")
    await ctx.send("주사위를 굴립니다. 데굴데굴~")
    result, _color, bot, user = dice()
    embed = discord.Embed(title = "주사위 게임 결과", description = None, color = _color)
    embed.add_field(name = "냥냥이의 숫자", value = ":game_die: " + bot, inline = True)
    embed.add_field(name = ctx.author.name+"의 숫자", value = ":game_die: " + user, inline = True)
    embed.set_footer(text="결과: " + result)
    await ctx.send(embed=embed)

    if (result == "승리"):
        await ctx.send("냥냥! 제가 졌네요~")
    elif (result == "무승부"):
        await ctx.send("냥냥! 비겼네요~")
    elif (result == "패배"):
        await ctx.send("냥냥! 제가 이겼다구요~")

@bot.command(aliases=['뽑기','당첨'])
async def 추첨(ctx, *args):
    await ctx.send("냥냥! 이번 주도 성실하게 보냈구냥!")
    arguments = ', '.join(args)
    await ctx.send(f'총 {len(args)}명이 추첨 대상이다냥!')
    embed = discord.Embed(title="추첨자 명단", description = arguments, color = 0xFFFFFF)
    await ctx.send(embed=embed)
    await ctx.send("고생한 길드원들을 위해 선물을 준비했다구요! 냥!")
    await ctx.send("두구두구냥~ 행운의 당첨자는 바로! 냥냥냥~!")
    choicelist = random.choice(args)
    embed = discord.Embed(title="당첨자", description = choicelist, color = 0xFFFFFF)
    await ctx.send(embed=embed)
    await ctx.send("축하한다냥!")


@bot.command(aliases=['분배금','경매'])
async def 분배(ctx, N, amount):
    if int(N) > int(amount):
        N, amount = amount, N
    dist = distribution(int(N),int(amount))

    if int(N) < 1 or int(amount) < 1 :
        await ctx.send(f'입력이 잘못된 것 같다냥!')
        await ctx.send(f'&분배금 인원 수령가격')
    else:
        await ctx.send("냥냥! 비싼 아이템을 얻은 거냥?")
        await ctx.send(f'총 {N}명에게 {number_to_korean(int(amount))}메소를 분배 하겠다냥!')
        embed = discord.Embed(title="분배금 계산", description="분배금 : " + number_to_korean(int(dist)), color=0xFFFFFF)
        await ctx.send(embed=embed)
        await ctx.send("이렇게 분배하면 모두 " + number_to_korean(int(dist * 0.95)) + "메소씩 공평하게 나눠 가진다냥!")

@bot.command(aliases=['EXP쿠폰'])
async def EXP교환권(ctx, startlevel, endlevel=0):
    await ctx.send('냥냥! EXP 교환권을 모아온거냥?')
    # 끝 레벨이 더 작을 경우 # 끝 레벨이 0이 아닐 경우
    if (int(startlevel) > int(endlevel) & endlevel != 0):
        startlevel, endlevel = endlevel, startlevel

    if endlevel == 0:
        embed = discord.Embed(title=str(int(startlevel)) + "레벨에서 레벨업하기 위해 필요한 EXP교환권 갯수", description=str(EXPcal(int(startlevel))) + "개", color=0x007FFF)
        embed.set_thumbnail(url="https://raw.githubusercontent.com/def-fault-self/Project-Nyan/main/img_exp.png")
    else:
        embed = discord.Embed(title=str(int(startlevel)) + "레벨에서 " + str(endlevel) + "레벨까지 필요한 EXP교환권 갯수", description=str(EXPcal(int(startlevel),int(endlevel))) + "개", color=0x007FFF)
        embed.set_thumbnail(url="https://raw.githubusercontent.com/def-fault-self/Project-Nyan/main/img_exp.png")
    await ctx.send(embed=embed)

@bot.command(aliases=['극한성장의비약','비약'])
async def 극성비(ctx, level):
    await ctx.send('냥냥! 극한 성장의 비약을 가져왔냥?')
    await ctx.send("어디보자냥~ " + str(level) + "레벨에서 먹으면 어떻게 되는지 알아보겠다냥!")
    if int(level) != 278:
        embed = discord.Embed(title=str(level) + "레벨 때 극성비를 먹었을 때 오르는 경험치량", description = str(EXPPotion(int(level))) + "%", color = 0xFF1493)
        embed.set_thumbnail(url="https://raw.githubusercontent.com/def-fault-self/Project-Nyan/main/img_potion.png")
    else:
        await ctx.send(str(level) + "레벨은 길마님 레벨 아니냥?")
        await ctx.send("약 먹을 생각하지 말고 사냥 좀 하라냥!")
    await ctx.send(embed=embed)

@bot.command(aliases=['몬스터파크','익스트림','익스트림몬스터파크'])
async def 익몬(ctx, level):
    await ctx.channel.send('냥냥! 익스트림 몬스터파크에 놀러가는거냥?')
    if int(level) !=276:
        await ctx.send("어디보자냥~ " + str(level) + "레벨에서 얼마나 경험치를 주는지 알아보겠다냥!")
        embed = discord.Embed(title=str(level) + "레벨 때 익스트림 몬스터파크에서 오르는 경험치량", description = "(평일) " + str(Extreme(int(level))) + "% (선데이) " + str(round(Extreme(int(level))*1.5,3)) + "%", color = 0xFFFFFF)
        embed.set_thumbnail(url="https://raw.githubusercontent.com/def-fault-self/Project-Nyan/main/img_mon.png")
    else :
        await ctx.send("어디보자냥~ " + str(level) + "레벨은 길마님 레벨 아니냥?")
        await ctx.send("혼자서 알아보라고 해라냥~")

    await ctx.send(embed=embed)

@bot.command(aliases=['사귀자'])
async def 여친생길확률(ctx):
    await ctx.channel.send('...')

@bot.command(aliases=['유저','조회'])
async def 캐릭터(ctx, Search): # return level, job, world, guild, union, floor
    level, job, world, guild, union, floor, src = Character(Search)
    special_script = ""
    await ctx.reply('냥냥! 요청한 유저의 정보를 조회하고 있다냥!')
    if Search == "아ship":
        special_script = "싹씹싹씹! 으윽.. 누가 나를 해킹하고 있다냥!"
    if Search == "Blurpoint":
        special_script = "멋진 우리 주인님이다냥!"
    if Search == "파천화령":
        special_script = "듀얼이다!!"
    if Search == "너구리의죽음":
        special_script = "십십~ 재입대 언제해~"
    if Search == "폭류참치":
        special_script = "있었는데.. 없어졌다냥!"
    if Search == "이태토르":
        special_script = "ㅅㅣㅂㄴㅣㅁ \n 왜 팔라딘하는 거 안말렸어요"
    if Search == "김소나":
        special_script = "무적 \'줘\' "
    if Search == "검성스팀":
        special_script = "치익.. 치익.."

    embed = discord.Embed(title=str(Search), url="https://maple.gg/u/" + str(Search), description = special_script ,color = 0x00ff40)
    embed.set_author(name="캐릭터 검색 결과")

    urllib.request.urlretrieve(str(src), "explain.png")
    image = discord.File("explain.png", filename="image.png")

    embed.set_thumbnail(url="attachment://image.png")
    embed.add_field(name="레벨", value=Erase(level), inline=True)
    embed.add_field(name="직업", value=job, inline=True)
    embed.add_field(name="월드", value=world, inline=True)
    embed.add_field(name="길드", value=guild, inline=True)
    embed.add_field(name="유니온", value=union, inline=True)
    embed.add_field(name="무릉", value=floor, inline=True)
    await ctx.send(embed=embed, file=image)


@bot.command(aliases=['환산스탯','스탯','스텟','스펙'])
async def 환산(ctx, Search):
    await ctx.reply('냥냥! 환산 계산기를 두드리는 중이다냥!')
    combPW, convST, hexaST, src = Conversion(Search)
    special_script = ""
    if Search == "아ship":
        special_script = "십십 재입대 언제해?"

    await ctx.send('내 전투력은 530000이다냥! 그렇지만 물론 풀파워로 싸울 생각은 없으니 걱정하지 말라냥!')
    embed = discord.Embed(title=str(Search), url="https://maplescouter.com/info?name=" + str(Search), description = special_script ,color = 0x00ff40)
    embed.set_author(name="전투력 조회 결과")

    urllib.request.urlretrieve(str(src), "explain.png")
    image = discord.File("explain.png", filename="image.png")
    embed.set_thumbnail(url="attachment://image.png")

    embed.add_field(name="전투력", value=combPW, inline=True)
    embed.add_field(name="환산", value=convST, inline=True)
    embed.add_field(name="헥사", value=hexaST, inline=True)
    await ctx.send(embed=embed, file=image)


@bot.command(aliases=['추가옵션','무기'])
async def 추옵(ctx, Search):
    await ctx.channel.send('냥냥! 무기에 붙는 추가옵션이 궁금한거냥?')
    df = Option(Search)
    output = t2a(
        header=list(df.columns)[1:],
        body = [remove_decimal_from_list(df.iloc[0].values.tolist())[1:], remove_decimal_from_list(df.iloc[1].values.tolist())[1:], remove_decimal_from_list(df.iloc[2].values.tolist())[1:],remove_decimal_from_list(df.iloc[3].values.tolist())[1:]],
        first_col_heading = True
    )

    code_block_content = f"""\
    ```{output}```
    """

    embed = discord.Embed(title=str(Search + "의 추가옵션표"), description = code_block_content, color = 0x00FF7F)
    await ctx.send(embed=embed)

@bot.command(aliases=['6차','HEXA','Hexa','hexa'])
async def 헥사(ctx, startlevel, endlevel=0):
    await ctx.send('냥냥! 솔에르다를 모아온 거냥?')
    # 끝 레벨이 더 작을 경우 # 끝 레벨이 0이 아닐 경우
    if (int(startlevel) > int(endlevel) & endlevel != 0):
        startlevel, endlevel = endlevel, startlevel

    Sol6, Piece6, Sol5, Piece5, Sol4, Piece4 = Hexa(int(startlevel), int(endlevel))
    d = [["Origin(6th)", Sol6, Piece6], ["Reinforce(5th)", Sol5, Piece5], ["Mastery(4th)", Sol4, Piece4]]
    df = pd.DataFrame(d, columns=['Kind', 'Sol Erda', 'Sol Piece'])


    output = t2a(
        header=list(df.columns),
        body=[df.iloc[0].values.tolist(), df.iloc[1].values.tolist(), df.iloc[2].values.tolist()],
        first_col_heading=True
    )

    code_block_content = f"""\
    ```{output}```
    """

    if endlevel == 0:
        embed = discord.Embed(title=str(int(startlevel)) + "레벨에서 레벨업하기 위해 필요한 \n 솔에르다와 솔에르다 조각 갯수", description=code_block_content, color=0x7b40e3)
        embed.set_thumbnail(url="https://raw.githubusercontent.com/def-fault-self/Project-Nyan/main/img_six.png")
        #embed.add_field(name="Table in Code Block", value=code_block_content, inline=True)
        await ctx.send(embed=embed ) #
    else:
        embed = discord.Embed(title=str(int(startlevel)) + "레벨에서 " + str(endlevel) + "레벨까지 필요한 \n 솔에르다와 솔에르다 조각 갯수", description=code_block_content, color=0x7b40e3)
        embed.set_thumbnail(url="https://raw.githubusercontent.com/def-fault-self/Project-Nyan/main/img_six.png")
        #embed.add_field(name="Table in Code Block", value=code_block_content, inline=True)
        await ctx.send(embed=embed)

@bot.command(aliases=['들어와', 'join'])
async def 입장(ctx):
        if ctx.author.voice and ctx.author.voice.channel:
            channel = ctx.author.voice.channel
            await channel.connect()
        else:
            await ctx.send("냥냥이가 채널을 찾다가 길을 잃어버렸습니다..")

@bot.command(aliases=['나가'])
async def 퇴장(ctx):
    try:
        await ctx.voice_client.disconnect()
    except IndexError as error_message:
        print(f"에러 발생: {error_message}")
        await ctx.send("냥냥이가 왔지만 {0.author.voice.channel}에 아무도 없었습니다..".format(ctx))
    except AttributeError as not_found_channel:
        print(f"에러 발생: {not_found_channel}")
        await ctx.send("냥냥이가 채널을 찾다가 길을 잃어버렸습니다..")

@bot.command(aliases=['명령어','도움말','도움'])
async def help(ctx):

        embed = discord.Embed(title="▶ 냥냥이 명령어 모음집", description="&명령어 &도움말 &도움 &help", color=0x00D4FF)
        embed.add_field(name="", value="", inline=False)

        embed.add_field(name="▶ 메이플 유틸리티", value="", inline=False)
        embed.add_field(name="&극성비 &비약 &극한성장의비약  ", value="\n-  N레벨에 극성비로 오르는 경험치를 계산합니다.", inline=False)
        embed.add_field(name="&익몬 &익스트림 &몬스터파크 ", value="- N레벨에 익몬으로 오르는 경험치를 계산합니다.", inline=False)
        embed.add_field(name="&EXP교환권 &EXP쿠폰", value="- N레벨에 EXP교환권로 오르는 경험치를 계산합니다.\n" + "- N레벨에서 M레벨까지 필요한 EXP 교환권 갯수를 계산합니다.", inline=False)
        embed.add_field(name="&헥사 &6차 &HEXA &hexa", value="- N레벨에서 필요한 헥사 재료 갯수를 계산합니다.\n" + "- N레벨에서 M레벨까지 필요한 헥사 재료 갯수를 계산합니다.", inline=False)
        embed.add_field(name="&추옵 &추가옵션 &무기 ", value="- 무기에 붙는 추가옵션 등급표를 검색합니다.", inline=False)
        embed.add_field(name="&캐릭터 &조회 &유저 ", value="- 유저의 캐릭터 정보를 검색합니다.", inline=False)
        embed.add_field(name="&환산 &스탯 &스텟 &스펙 ", value="- 유저의 환산을 검색합니다.", inline=False)
        embed.add_field(name="&분배 &분배금", value="- N명에게 나눌 분배금을 계산합니다.\n" + "- 경매장에서 M메소를 수령한 후 N명에게 분배금을 계산합니다", inline=False)

        embed.add_field(name="", value="", inline=False)

        embed.add_field(name="▶ 편리한 유틸리티", value="", inline=False)
        embed.add_field(name="&입장 &들어와 &join", value="- 냥냥이를 음성 채널에 들여보냅니다..", inline=False)
        embed.add_field(name="&퇴장 &나가 &멈춰 &정지 &stop", value="- 냥냥이를 음성 채널에서 내보냅니다.", inline=False)
        embed.add_field(name="&재생 &틀어 &틀어줘 &불러 &불러줘 &play", value="- 해당 링크의 유튜브 음악을 재생합니다.", inline=False)
        embed.add_field(name="&볼륨 &소리 &volume", value="- 유튜브 음악 볼륨을 조절합니다. (*TTS와 별개의 볼륨입니다.)", inline=False)
        embed.add_field(name="&말해 &TTS &tts", value="- TTS기능으로 말합니다. ", inline=False)

        embed.add_field(name="", value="", inline=False)

        embed.add_field(name="▶ 냥냥이랑 대화하기", value="", inline=False)
        embed.add_field(name="&사귀자", value="- 냥냥이에게 데이트를 신청합니다.", inline=False)
        embed.add_field(name="&여친생길확률", value="- 여자친구가 생길 확률을 계산합니다.", inline=False)

        await ctx.send(embed=embed)

@bot.command()
async def tts(ctx, *, text):
    # 봇이 현재 접속해 있는 음성 채널을 가져옵니다.
    voice_channel = ctx.author.voice.channel

    if voice_channel:
        # 텍스트를 음성으로 변환합니다.
        tts = gTTS(text=text, lang='ko')
        tts.save('tts.mp3')

        # 변환한 음성 파일을 음성 채널에서 재생합니다.
        ctx.voice_client.play(discord.FFmpegPCMAudio('tts.mp3'))

        # 재생이 끝날 때까지 대기합니다.
        while ctx.voice_client.is_playing():
            await asyncio.sleep(1)

        # 임시로 생성한 음성 파일을 삭제합니다.
        os.remove('tts.mp3')
    else:
        await ctx.send('음성 채널에 먼저 입장해주세요.')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

@bot.event
async def on_member_join(member):
    fmt = '{0.mention}, {1.name} 에 온 것을 환영한다냥!'
    channel = member.server.get_channel("507201204997062658")
    await member.send(channel, fmt.format(member, member.server))


async def main():
    async with bot:
        await bot.add_cog(Music(bot))
        await bot.start("MTEzODM5OTgxNzk1ODE2NjUyOA.GqfBxN.ceHyReZxkijSkrVhO2GLHSymFHWoZyt3IkFjQY") # bot.run("MTEzODM5OTgxNzk1ODE2NjUyOA.GqfBxN.ceHyReZxkijSkrVhO2GLHSymFHWoZyt3IkFjQY")

asyncio.run(main())