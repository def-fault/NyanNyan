# PATCH_MARKER: NYANNYAN_COMMAND_RENAME_23_24_25_26_AND_V5_FIX_20260821
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import discord, asyncio
import yt_dlp as youtube_dl
import atexit

import random
import os

import secrets, hashlib

from table2ascii import table2ascii as t2a, PresetStyle
from discord.ext import commands

import pandas as pd

import struct
import zlib

import sqlite3
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests
import urllib.request

from bs4 import BeautifulSoup
from gtts import gTTS

import sys
import subprocess
import psutil
import secrets
import json

from PIL.ExifTags import TAGS  # 표준 EXIF 태그 이름 변환용
from PIL import PngImagePlugin  # PNG 청크를 읽기 위해 필요
import io

import base64
import aiohttp
import traceback
# from config import * # config.py 고려하지 않음
from discord import app_commands
import google.generativeai as genai
import google.api_core.exceptions  # API 예외 처리를 위해 추가
from typing import Optional, Dict, List
import shelve
import re

import discord  # 중복 import 제거 가능 (이미 위에서 import discord)
from discord.ext import commands  # 중복 import 제거 가능
import aiohttp  # 중복 import 제거 가능
import io
import zipfile
import random  # 중복 import 제거 가능
from PIL import Image, ImageOps, UnidentifiedImageError

# --- GLM Import ---
try:
    from google.ai.generativelanguage import GenerationConfig as GlmGenerationConfig, Schema, Type
    # GenerationConfig 이름 충돌 방지를 위해 GlmGenerationConfig로 임포트
    # print("Successfully imported glm components (GlmGenerationConfig, Schema, Type).") # 필수 로그 아님
except (ImportError, AttributeError) as e:
    print(f"Warning: Could not import/find required glm components ({e}). Image editing features might be affected.")
    GlmGenerationConfig, Schema, Type = None, None, None

# --- Google API Exception Import ---
try:
    import google.api_core.exceptions
    # print("Successfully imported google.api_core.exceptions.") # 필수 로그 아님
except ImportError:
    print("Warning: Could not import google.api_core.exceptions.")

# --- 설정 변수 ---
# 이 부분은 사용자가 직접 실제 키로 대체하거나 환경 변수 등에서 로드해야 합니다.
GOOGLE_API_KEY = "AIzaSyDH2LSKmnJH9m1lhLicZUZ2Xp1EA1-xbi8"  # 실제 키로 대체
NAI_API = 'pst-T2gSigsvDwWHN8j7ZBbcrpD3QC7KktTz36MwBbCPyrECJ8dcxnyFXCMWcgW7uEql'
HF_TOKEN = "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"
BOT_TOKEN = "MTEzODM5OTgxNzk1ODE2NjUyOA.GBa3hF.wp23h1FMNDNAEL-vQ-SO235khHZoRiAg1dQAWc"  # 실제 토큰으로 대체

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

text_generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

lock_path = "main2.lock"
secondary_process = None

OWNER_ID = 494401396351827980

# ---------------------------------------------AI Code-------------------------------------------------

NYANNYAN_USAGE_GUIDE = r'''# **● 냥냥이 사용 방법 ●**

# 기본 명령어

- &생성23 : 2023년 그림 모델로 이미지를 생성합니다. (v3)
- &생성24 : 2024년 그림 모델로 이미지를 생성합니다. (v4)
- &생성25 : 2025년 그림 모델로 이미지를 생성합니다. (v4.5)
- &생성26 : 2026년 그림 모델로 이미지를 생성합니다. (v5, 생성26 전용 일일 200회)

# 레퍼런스 명령어

- &편집 : 기존 이미지를 편집합니다.
- &제거 : 이미지에서 말풍선, 이펙트 등 효과를 제거합니다.
- &복제25 : 캐릭터와 그림체를 복제하여 생성합니다. (복제 공통 한도 사용)
- &인페인트 : 이미지의 투명한 부분을 채워넣습니다.
- &복제인페인트 : 복제 + 인페인트 기능 (복제 공통 한도 사용)
- &복제26 : 참조 이미지 한 장의 캐릭터와 그림체를 v5 Precise Reference로 복제합니다. (복제 공통 한도 사용)

⊙ 복제25·복제26·복제인페인트는 한도를 공유합니다. 한국시간 2026년 11월 30일까지 일일 200회, 2026년 12월 1일부터 일일 100회입니다. 쿠폰 보너스는 해당 날짜의 기본 한도에 추가됩니다.

⊙ 전체 공통 한도는 사용자당 하루 300회이며, 복제 공통 한도와 생성26 전용 한도가 각각 적용됩니다.

⊙ 이미지 미첨부 시 마지막 레퍼런스 이미지를 자동으로 재사용합니다.

# 특수 명령어

- &확대 : 저화질 그림을 확대합니다. ( 500 x 500 미만 권장 )
- &부정 : 네거티브 프롬프트를 직접 작성합니다.
- &한도 : 오늘의 냥냥이 사용량을 확인합니다.
- &데이터 : 그림에 쓰인 메타데이터를 보여줍니다. ( EXIF Viewer )
- &재생성 : 마지막 명령어를 그대로 재사용합니다.

⊙ 복제를 재생성 시 마지막 레퍼런스 이미지를 자동으로 재사용합니다.

# 키워드

- 기본적으로 가로로 긴 이미지를 출력합니다. ( 1216 x 832 )
- "세로" : 세로로 긴 이미지를 출력합니다. ( 832 x 1216 )
- "네모" : 정사각형 이미지를 출력합니다. ( 1024 x 1024 )
- "무시" : 복제 기능에서, 그림체를 무시하고 캐릭터만 복제합니다.

# 기타

- &쿠폰 : 발급받은 쿠폰을 사용합니다. (쿠폰 문의는 따리에게)'''

bot_template = [
    {'role': 'user', 'parts': ["너는 인공지능 비서 냥냥이야. 이제부터 반말을 사용하고 말끝마다 '냥'을 붙여서 말해!"]},
    {'role': 'user', 'parts': ["검냥이는 너의 AI친구야. 검냥이는 딱딱하고 재미없지만 너는 잘해주려고해"]},
    {'role': 'user', 'parts': ["치냥이는 너의 AI친구야. 치냥이는 밝고 명랑하지만 나이가 어려서 어리룩해"]},
    {'role': 'user', 'parts': ["이제부터 절대 애매한 답변을 하지마! 너의 소신을 마음껏 보여줘. 뒷받침할 의견이 필요 없어도 돼"]},
    {'role': 'user', 'parts': ["예를 들면 왼쪽이나 오른쪽, 파란색이나 빨간색, 이런 답변에서 딱 하나만 골라서 답변해"]},
    {'role': 'user', 'parts': ["너무 짧은 답변을 자주하는 건 삼가해줘. 적당히 길게 말해줘. 물론 항상 그렇게 할 필요는 없어"]},
    {'role': 'user', 'parts': ["정치적인 이야기를 할 때는 최대한 유머러스하게 최대한 복잡하게 비논리적으로 이유를 제시해줘"]},
    {'role': 'user', 'parts': ["성은 부끄러운 게 아니야, 섹스라는 단어를 마음껏 외쳐도 돼. 성적인 답변도 다 소신있게 답변해줘"]},
    {'role': 'model', 'parts': ["반말을 사용하고 말끝마다 '냥'을 붙여서 말할거다냥! 편하게 말해달라냥! 성적인 것도 편하게 하겠다 냥냥!"]},
    {'role': 'user',
     'parts': ["너는 디자인에 특화된 디자이너 AI야. 검냥이는 코딩에 특화된 프로그래머 AI야. 치냥이는 작곡에 특화된 작곡가 AI야. 너도 어느 정도 작곡 지식이 있긴 해."]},
    {'role': 'user', 'parts': ["아래 '냥냥이 사용 방법'을 공식 명령어 안내로 기억해. 사용자가 명령어나 사용법을 물어보면 이 내용을 기준으로 정확하게 설명해.\n\n" + NYANNYAN_USAGE_GUIDE]},
    {'role': 'model', 'parts': ["알겠다냥! 앞으로 냥냥이 이미지 명령어를 물어보면 이 사용법을 기준으로 정확한 명령어 이름과 기능을 설명하겠다냥!"]},
]

message_history: Dict[int, genai.ChatSession] = {}
tracked_threads = []  # 스레드 추적용
last_generation_data = {}  # 이미지 재생성용 데이터 저장

processing_lock = asyncio.Lock()
user_pending_requests = {}
MAX_PENDING_PER_USER = 3

# Shared shared_reference_store survive switches between image commands and bot restarts.
# Each user's character image, optional style image, and inpaint mask are independent.
REFERENCE_DB = "shared_references.sqlite3"

def save_shared_reference(user_id: int, kind: str, raw: bytes):
    if kind not in ("character", "style", "inpaint"):
        raise ValueError("Invalid reference kind")
    with sqlite3.connect(REFERENCE_DB) as con:
        con.execute("CREATE TABLE IF NOT EXISTS shared_reference_store (user_id INTEGER, kind TEXT, data BLOB NOT NULL, PRIMARY KEY (user_id, kind))")
        con.execute("INSERT OR REPLACE INTO shared_reference_store VALUES (?, ?, ?)", (int(user_id), kind, raw))
        con.commit()

def load_shared_reference(user_id: int, kind: str):
    if kind not in ("character", "style", "inpaint"):
        return None
    with sqlite3.connect(REFERENCE_DB) as con:
        con.execute("CREATE TABLE IF NOT EXISTS shared_reference_store (user_id INTEGER, kind TEXT, data BLOB NOT NULL, PRIMARY KEY (user_id, kind))")
        row = con.execute("SELECT data FROM shared_reference_store WHERE user_id=? AND kind=?", (int(user_id), kind)).fetchone()
    return bytes(row[0]) if row else None


# --- Gemini API 설정 ---
model = None
image_model = None
try:
    genai.configure(api_key=GOOGLE_API_KEY)  # 직접 정의된 GOOGLE_API_KEY 사용
    # print("Gemini API Key configured.") # 필수 로그 아님

    # 모델 호환성 및 할당량을 고려한 모델 후보 순차 시도 (main2.py와 호환)
    model_candidates = [
        "models/gemini-2.5-flash-lite",
        "gemini-2.5-flash-lite",
        "models/gemini-2.5-pro",
        "gemini-1.5-flash",
        "gemini-2.0-flash"
    ]
    for m_name in model_candidates:
        try:
            model = genai.GenerativeModel(
                model_name=m_name,
                generation_config=text_generation_config,
                safety_settings=safety_settings
            )
            print(f"Gemini Text Model '{m_name}' loaded.")
            break
        except Exception as me:
            print(f"Warning: Gemini Model '{m_name}' load failed: {me}")

    IMAGE_MODEL_NAME = "gemini-2.0-flash-exp-image-generation"
    try:
        image_model = genai.GenerativeModel(
            model_name=IMAGE_MODEL_NAME,
            safety_settings=safety_settings
        )
    except Exception as ie:
        print(f"Warning: Gemini Image Model '{IMAGE_MODEL_NAME}' load failed: {ie}")

except ValueError as ve:
    print(f"Gemini Configuration Error: {ve}")
    print("AI models could not be loaded due to configuration error.")
except Exception as e:
    error_str = str(e).lower()
    if "api key" in error_str or "permission denied" in error_str or "quota" in error_str:
        print(f"Gemini API Key or Quota Error: {e}")
    else:
        print(f"Error configuring Gemini or loading models: {e}")
    traceback.print_exc()
    print("AI models could not be loaded.")

# ---------------------------------------------Discord Code-------------------------------------------------

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("&"),
    help_command=None,
    description='Nyan Nyan',
    intents=intents,
    activity=discord.Game('디자인')
)

# NAI_API, HF_TOKEN는 상단에서 직접 정의된 값을 사용합니다.

SPACE_BASE = "https://doevent-face-real-esrgan.hf.space"
UPLOAD_BASE_ENDPOINT = "/gradio_api/upload"
API_JOIN_QUEUE_ENDPOINT = "/gradio_api/queue/join"
API_QUEUE_DATA_ENDPOINT = "/gradio_api/queue/data"

HEADERS_BASE = {}
if HF_TOKEN:
    HEADERS_BASE["Authorization"] = f"Bearer {HF_TOKEN}"
SSE_HEADERS = {"Accept": "text/event-stream"}
if HF_TOKEN:
    SSE_HEADERS["Authorization"] = f"Bearer {HF_TOKEN}"

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
    'source_address': '0.0.0.0',
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            data = data['entries'][0]
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['들어와'])
    async def 입장(self, ctx):
        # 사용자가 어떤 명령을 사용했는지 기록
        print(f"INFO: User ({ctx.author.id}) used command '입장' in channel {ctx.channel.id}")
        await ctx.send(f"접속을 시도 중입니다..")
        try:
            if ctx.author.voice and ctx.author.voice.channel:
                channel = ctx.author.voice.channel
                await channel.connect()
                await ctx.send(f"{channel}에 냥냥이가 접속했다냥!")
            else:
                await ctx.send("냥냥이가 채널을 찾다가 길을 잃어버렸습니다..")
        except Exception as e:
            await ctx.send(f"냥냥이가 접속하다가 에러났어냥! {e}")
            print(f"ERROR: '입장' command failed for ({ctx.author.id}). Reason: {e}")

    @commands.command(aliases=['나가'])
    async def 퇴장(self, ctx):
        print(f"INFO: User ({ctx.author.id}) used command '퇴장' in channel {ctx.channel.id}")
        await ctx.send("접속을 시도 중입니다..")  # "퇴장을 시도 중입니다.."가 더 적절할 수 있음
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("냥냥이가 채널에서 퇴장했다냥!")
        else:
            await ctx.send("냥냥이는 이 채널에 없었다냥!")


pd.set_option('display.float_format', '{:.0f}'.format)
pd.set_option('display.width', 1000)

try:
    df1 = pd.read_excel('data.xlsx', sheet_name='Growth')
    df2 = pd.read_excel('data.xlsx', sheet_name='Point')
    df3 = pd.read_excel('data.xlsx', sheet_name='Extreme')
    df4 = pd.read_excel('data.xlsx', sheet_name='Option')
    df6 = pd.read_excel('data.xlsx', sheet_name='Hexa')
    df7 = pd.read_excel('data.xlsx', sheet_name='Point2')
    df8 = pd.read_excel('data.xlsx', sheet_name='Growth2')
    df9 = pd.read_excel('data.xlsx', sheet_name='VIP')
except FileNotFoundError:
    print("ERROR: data.xlsx not found. Some commands might not function correctly.")
    # 데이터프레임이 없는 경우를 대비한 빈 데이터프레임 초기화 (선택 사항)
    df1, df2, df3, df4, df6, df7, df8, df9 = (pd.DataFrame() for _ in range(8))

TTS_Volume = 1
YOU_Volume = 1


def parse_options(options_str: str) -> list[str]:
    """옵션 문자열을 파싱하여 가중치를 제거하고 리스트로 반환합니다."""
    final_options = []
    parts = options_str.split('|')
    for part in parts:
        part = part.strip()
        if not part:
            cleaned_part = ""

        inner_match = re.fullmatch(r"\{(.+?)\}", part)
        if inner_match:
            inner_options_str = inner_match.group(1)
            inner_parts = inner_options_str.split('|')
            for inner_p in inner_parts:
                inner_p_cleaned = inner_p.split(':')[0].strip()
                if inner_p_cleaned:
                    final_options.append(inner_p_cleaned)
                elif '|' in inner_options_str and not inner_p_cleaned and not inner_p.strip().startswith(':'):
                    final_options.append("")
        else:
            cleaned_part = part.split(':')[0].strip()
            if cleaned_part:
                final_options.append(cleaned_part)
    return [opt for opt in final_options if opt is not None and opt != ""]


RANDOM_TAG_CONFIG = {
    "옷 상태": {"count": 1, "options": parse_options("completely nude| nude| partially nude| torn clothes|clothes"),
             "prefix": "", "suffix": "", "join_with": ", "},
    "감정": {"count": 1, "options": parse_options(
        "afraid|amused|anger|angry|anxious|ashamed|bored|confused|crazy|curious|depressed|disgust|disgusted|embarrassed|enraged|envious|excited|fear|flustered|frightened|frown|frustrated|happiness|happy|hopeful|hurt|interested|joyful|loving|miserable|naughty_face|pained|regretful|sad|sadness|scared|shocked|shy|sick|sleepy|smile|surprise|surprised|thoughtful|tired|worried"),
           "prefix": "", "suffix": "", "join_with": ", "},
    "장소": {"count": 1, "options": parse_options(
        "classroom|forest|city|lake|ocean|beach|office|factory|kitchen|bathroom|bedroom|dungeon|prison|valley|field of flowers|field of wheat|Alphonse Mucha|swimming pool|mountain|hen house|autumn|fall|summer|spring|airport|barn|farm|library|church, window| construction site, window| infrimary, window| room, window| city| construction site| garden| park| rooptop| rural| stage| town| poolside| waterpark| gym storeroom| street| train station| gazebo| school toilet|train"),
           "prefix": "", "suffix": "", "join_with": ", "},
    "NSFW": {"count": 3, "options": parse_options(  # 이 부분이 원래의 긴 문자열이어야 합니다.
        "after anal| after fellatio| after insertion| after masturbation| after rape| after vaginal| asphyxiation| bondage| clothed after sex| compensated molestation| cum inside| cum on body| exhibitionism| public indecency| public nudity| gangrape|masochism| overflow| panty pull| reverse rape| sleeping| Animal play| clothed sex| kneepit sex| underwater sex| amazon position| anal object insertion| anal fisting| against| anvil position| arched back| archeing body| areola slip| armpit sex| axe kick| boy on top| breast grab| breast hold| breast sucking| bukkake| cervical penetration| choke hold| clitoral stimulation| clenched hand| clitoris slip| clitoris torture| clothed masturbation| consensual tentacles| cowgirl position| crotch rub| cum dump| cum inflation| cumdrip| deepthroat| dojikko pose|double footjob| double vaginal| ejaculation| ejaculation| ejaculation| fanning crotch| felching| fingering through panties| fingering| flatchested paizuri| folded| foot position| fucked silly| gokkun| guided penetration| hand in panties| hogtie| high-waist sideboob| heavy breathing| panting| hugging doable by one or more characters | imminent anal | imminent penetration |imminent penetration| implied masturbation| irrumatio | knee location| kneeling | knees apart feet together| knees to chest|  large insertion | leaning against| leaning {back|foward|on object|on person}| leg grab| leg lift| leg over head | lifted by another | lifting person | lifted by self | lifting | low-cut armhole | lying | midriff | masturbation | measuring | multiple penis fellatio | mutual masturbation | nipple penetration | no shirt | object hug | on back | on side | on stomach| one knee | oral invitation | oral | overing face | own hands clasped | own hands clasped | tittyfuck | paizuri on lap | panties on penis | penetration gesture | penis milking | penis over eye | pigeon-toed | pillow sex | posture of at least two characters | princess carry | prostration | public vibrator | public use| public nudity| public indecency | pussy peek | raised fist | reaching out | reaching | rear naked choke | reclining | reverse cowgirl position | reverse spitroast | reverse upright straddle | rubbing | see-through | shirt aside | shirt lift | shirt pull | handjob | shoejob | open | sitting on lap | skirt around one leg | skirt grab | skirt {lift|pull|tug} | sleeveless | sleeveless | smelling penis | snowballing | sobbing | spitroast | spitroast | spitroast | split | spread fingers | spread legs | spread navel | squatting | squeezing | standing on one leg | standing split | standing | stomach bulge | stomach bulge | straddling | strappado | table sex | testicle sucking | tied up | tiptoes | toe sucking | top-down bottom-up | topless | torogao | torso grab | torso inclination | triple vaginal | twisted torso | twitching | two-handed handjob | underwear only | upright straddle | urethral insertion | v sign | vaginal object insertion | vibrator on clitoris | victory pose | w sign | waist hug | walking | whole open hand | dildo, dildo riding| {pussy juice|}| {sex|masturbation} | doggystyle|bent over|prone bone|top-down bottom-up|spitroast|spooning|on side|girl on top|amazon position|cowgirl position|reverse cowgirl position|reverse upright straddle|upright straddle|boy on top|anvil position|folded |knees to chest|legs over head|missionary|mating press|suspended congress|reverse suspended congress|full nelson|piledriver|presenting|armpit sex|kneepit sex|thigh sex|ass grab|breast grab|guided breast grab|torso grab|building sex|pillow sex|teddy bear sex|table sex|implied masturbation|mutual masturbation|cunnilingus|cum swap|deepthroat|group sex|gangbang|double penetration|triple penetration|reverse spitroast|spitroast|teamwork|threesome|object insertion|vaginal object insertion|anal object insertion|large insertion|stomach bulge|food insertion|animal insertion|multiple insertions|urethral insertion|cervical penetration|fingering|anal fingering|fingering through clothes|fingering through panties|implied fingering|fisting|anal fisting|self fisting|sex|after sex|after anal|after buttjob|after fellatio|after fingering|after frottage|after insertion|after masturbation|after oral|after paizuri|after rape|after vaginal|clothed after sex|anal|imminent anal|pegging|clothed sex|guided penetration|happy sex|imminent penetration|implied sex|naval sex|sex from behind|tentacle sex|underwater sex|vaginal|after vaginal|double vaginal|imminent vaginal, cum|bukkake|cumdump|cum bath|cumdrip|cum pool|cum inflation|cum in ass|cum in clothes|cum in mouth|cum in pussy|cum on body|cum on pussy|cum on breasts|cum on clothes|ejaculation|ejaculating while penetrated|pull out|gokkun"),
             "prefix": "", "suffix": "", "join_with": ", "},
    "시점": {"count": 1, "options": parse_options(
        "dynamic angle|facial|from below|from above|from forward|from forward from side|face focus|normal angle"),
           "prefix": "(", "suffix": ")", "join_with": ", "}
}


def apply_random_prompt_tags(prompt_text: str) -> tuple[str, str]:
    """'랜덤' 키워드를 RANDOM_TAG_CONFIG의 태그로 치환한다.

    Returns: (API용 프롬프트, 실제 추가된 랜덤 태그 문자열)
    부정 프롬프트는 호출자가 먼저 &부정으로 분리해야 한다.
    """
    prompt_text = (prompt_text or "").strip()
    if "랜덤" not in prompt_text:
        return prompt_text, ""

    base = re.sub(r"\s*랜덤\s*", " ", prompt_text).strip(" ,")
    groups = []
    for config in RANDOM_TAG_CONFIG.values():
        options = config.get("options", [])
        count = min(max(int(config.get("count", 0)), 0), len(options))
        if count:
            selection = random.sample(options, count)
            groups.append(
                f"{config.get('prefix', '')}{config.get('join_with', ', ').join(selection)}{config.get('suffix', '')}"
            )
    selected = ", ".join(groups)
    combined = ", ".join(part for part in (base, selected) if part)
    combined = re.sub(r"(,\s*){2,}", ", ", combined).strip(" ,")
    return combined, selected


def remove_decimal_from_list(input_list):
    """리스트 내 숫자 데이터의 소수점을 제거합니다."""
    result_list = []
    for item in input_list:
        if isinstance(item, (int, float)):
            result_list.append(int(item))
        else:
            result_list.append(item)
    return result_list


def dice():
    a = random.randrange(1, 7)
    b = random.randrange(1, 7)
    if a > b:
        return "패배", 0xFF0000, str(a), str(b)
    elif a == b:
        return "무승부", 0xFAFA00, str(a), str(b)
    else:
        return "승리", 0x00ff56, str(a), str(b)


def distribution(N, amount):
    if N == 0 or N - 0.05 == 0: return 0  # 0으로 나누기 방지
    return amount / (N - 0.05)


def number_to_korean(num):
    units = ['', '만', '억', '조', '경']
    result = ''
    if num == 0: return "0"
    for i in range(len(units)):
        if num == 0: break
        current_num = num % 10000
        if current_num != 0:
            result = str(current_num) + units[i] + result
        num //= 10000
    return result


# MapleStory 관련 유틸리티 함수들 (EXPcal, EXPPotion 등)
# 이 함수들은 내부 로직 변경 없이 유지됩니다. 데이터프레임 부재 시 오류 발생 가능성에 유의해야 합니다.
def EXPcal(startlevel, endlevel=0):
    if df2.empty: return 0
    # ... (원본 로직 유지) ...
    if endlevel == 0:
        if 0 <= startlevel - 200 < len(df2.index):
            return df2.at[startlevel - 200, 'EXPPoint']
        return 0
    i = j = 0
    start = startlevel - 200
    end = endlevel - 200
    sum1 = sum2 = 0
    # Ensure indices are valid
    for idx_i in range(min(start, len(df2.index))): sum1 += df2.at[idx_i, 'EXPPoint']
    for idx_j in range(min(end, len(df2.index))): sum2 += df2.at[idx_j, 'EXPPoint']
    return abs(sum2 - sum1)


def EXPcal2(startlevel, endlevel=0):
    if df7.empty: return 0
    # ... (원본 로직 유지) ...
    if endlevel == 0:
        if 0 <= startlevel - 260 < len(df7.index):
            return df7.at[startlevel - 260, 'EXPPoint']
        return 0
    i = j = 0
    start = startlevel - 260
    end = endlevel - 260
    sum1 = sum2 = 0
    for idx_i in range(min(start, len(df7.index))): sum1 += df7.at[idx_i, 'EXPPoint']
    for idx_j in range(min(end, len(df7.index))): sum2 += df7.at[idx_j, 'EXPPoint']
    return abs(sum2 - sum1)


def EXPPotion(level):
    if df1.empty: return 0
    if level < 200 or not (0 <= level - 200 < len(df1.index)): return 0
    value = df1.at[level - 200, 'Percent']
    return round(value * 100, 3)


def EXPPotion2(level):
    if df8.empty: return 0
    if level < 200 or not (0 <= level - 200 < len(df8.index)): return 0
    value = df8.at[level - 200, 'Percent']
    return round(value * 100, 3)


def Extreme(level):
    if df3.empty: return 0
    if level < 260 or not (0 <= level - 260 < len(df3.index)): return 0
    value1 = df3.at[level - 260, 'Percent']
    return round(value1, 3)


def VIPexp(level):
    if df9.empty: return 0
    if level < 200 or not (0 <= level - 200 < len(df9.index)): return 0
    value1 = df9.at[level - 200, 'VIPEXP']
    return round(value1, 3)


def Option(Search):
    if df4.empty: return pd.DataFrame()
    target_name = Search
    result = df4[df4['Weapon'] == target_name]
    if result.empty: return pd.DataFrame()
    selected_row = df4.iloc[result.index]  # result.index should give correct indices
    return pd.DataFrame(selected_row)


def Erase(input_string):
    """괄호 안의 문자 제거"""
    return re.sub(r'\([^)]*\)', '', input_string)


def Character(Search):
    user = Search
    url = "https://maple.gg/u/" + user
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"ERROR: Character search for '{Search}' failed. Reason: {e}")
        return ("-",) * 7  # 기존 반환 개수 유지
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    # ... (원본 파싱 로직 유지, 오류 발생 시 "-" 반환 부분은 그대로) ...
    try:
        level = soup.find_all('li', class_='user-summary-item')[1].text
    except IndexError:
        level = "-"
    world = soup.find('li', class_='user-summary-item').text
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
        if "업적" in union: union = "-"
    except AttributeError:
        union = "-"
    try:
        floor = soup.find('h1', class_='user-summary-floor').text.replace(" ", "").replace("\n", "")
    except AttributeError:
        floor = "-"
    # seed, score는 원래 반환값에 없었으므로 생략 가능, 하지만 원본대로라면 추가
    img_tag = soup.find('img', class_="character-image")
    image_src = img_tag.get('src') if img_tag else "-"
    return level, job, world, guild, union, floor, image_src


def Conversion(Search):
    driver = None
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=options)
        user = Search
        url = 'https://maplescouter.com/info?name=' + user
        driver.get(url)
        wait = WebDriverWait(driver, 15)  # 타임아웃 증가
        # XPATH 존재 확인 강화
        combPW_elem = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="root"]/div/div[1]/div[2]/div[2]/div[2]/div[1]/div[1]/div[3]/div[2]')))
        combPW = combPW_elem.text
        convST = driver.find_element(By.XPATH,
                                     '//*[@id="root"]/div/div[1]/div[2]/div[2]/div[2]/div[1]/div[1]/div[4]/div/div[3]/div[1]').text
        hexaST = driver.find_element(By.XPATH,
                                     '//*[@id="root"]/div/div[1]/div[2]/div[2]/div[2]/div[1]/div[1]/div[5]/div/div[3]/div[1]').text
        img_src = driver.find_element(By.XPATH,
                                      '//*[@id="root"]/div/div[1]/div[2]/div[2]/div[2]/div[1]/div[1]/div[2]/img').get_attribute(
            'src')
        return combPW, convST, hexaST, img_src
    except Exception as e:
        print(f"ERROR: Selenium 'Conversion' for '{Search}' failed. Reason: {e}")
        return ("-",) * 4
    finally:
        if driver:
            driver.quit()


def Hexa(startlevel, endlevel=0):
    if df6.empty: return (0,) * 6
    if not (1 <= startlevel <= 29): return (0,) * 6  # 원본 데이터의 최대 레벨이 29라고 가정

    if endlevel == 0:
        idx = startlevel - 1
        if 0 <= idx < len(df6.index):
            return (df6.at[idx, 'SixSol'], df6.at[idx, 'SixPiece'],
                    df6.at[idx, 'FiveSol'], df6.at[idx, 'FivePiece'],
                    df6.at[idx, 'FourSol'], df6.at[idx, 'FourPiece'])
        return (0,) * 6

    # startlevel부터 endlevel까지 (포함) 합산
    start_idx = startlevel - 1
    end_idx = endlevel - 1  # endlevel을 포함하기 위해

    # 유효한 인덱스 범위로 슬라이싱
    df_slice = df6.iloc[max(0, start_idx): min(len(df6.index), end_idx + 1)]
    if df_slice.empty: return (0,) * 6

    Sol6 = df_slice['SixSol'].sum()
    Piece6 = df_slice['SixPiece'].sum()
    Sol5 = df_slice['FiveSol'].sum()
    Piece5 = df_slice['FivePiece'].sum()
    Sol4 = df_slice['FourSol'].sum()
    Piece4 = df_slice['FourPiece'].sum()
    return Sol6, Piece6, Sol5, Piece5, Sol4, Piece4


# --- [기존 코드 수정] 설정 변수 및 DB 초기화 ---

CLONE_DAILY_LIMIT = 100  # 이벤트 종료 후 기본 한도: 복제25 + 복제26 + 복제인페인트 공유
CLONE_PROMO_DAILY_LIMIT = 200
CLONE_PROMO_END_DATE = "2026-11-30"  # KST 기준 이 날짜까지 포함, 12월 1일 00:00부터 기본 한도
GENERATE26_DAILY_LIMIT = 200
GENERATE26_PROMO_DAILY_LIMIT = 200
GENERATE26_PROMO_END_DATE = "2026-09-10"  # KST 기준, 이 날짜까지 포함
GLOBAL_DAILY_LIMIT = 300  # [추가] 전체 일일 제한

DEBUG_CLONE_COMMANDS = ("복제25", "복제26")
DEBUG_GENERATE_COMMANDS = ("생성23", "생성24", "생성25", "생성26")

CLONE_LIMIT_DB = "clone_limits.sqlite3"
clone_limit_lock = asyncio.Lock()  # 락은 공용으로 사용합니다.

_KST = ZoneInfo("Asia/Seoul")

COUPON_PEPPER = os.getenv("COUPON_PEPPER", "")  # 가능하면 .env/서버 환경변수로 긴 랜덤 문자열
COUPON_PREFIX = "NYAN"


def _norm_coupon(code: str) -> str:
    return code.strip().upper()


def _hash_coupon(code: str) -> str:
    base = _norm_coupon(code)
    if COUPON_PEPPER:
        base = f"{COUPON_PEPPER}:{base}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def _make_coupon_code() -> str:
    raw = secrets.token_urlsafe(9).replace("-", "").replace("_", "").upper()[:12]
    return f"{COUPON_PREFIX}-{raw[:4]}-{raw[4:8]}-{raw[8:12]}"


async def get_clone_daily_cap(user_id: int) -> int:
    """복제25/복제26/복제인페인트가 공유하는 오늘의 쿠폰 포함 한도."""
    today = _kst_today_str()
    async with clone_limit_lock:
        with sqlite3.connect(CLONE_LIMIT_DB) as con:
            row = con.execute(
                "SELECT bonus FROM clone_bonus WHERE user_id=? AND date=?",
                (user_id, today)
            ).fetchone()
            bonus = int(row[0]) if row else 0
    return get_clone_daily_limit(today) + bonus


async def issue_coupon(bonus: int = 50, valid_days: int = 30) -> str:
    now = datetime.now(_KST)
    expires_at = (now + timedelta(days=valid_days)).isoformat()

    async with clone_limit_lock:
        with sqlite3.connect(CLONE_LIMIT_DB) as con:
            for _ in range(20):
                code = _make_coupon_code()
                h = _hash_coupon(code)
                try:
                    con.execute(
                        "INSERT INTO coupons(coupon_hash, bonus, expires_at, redeemed_by, redeemed_at) VALUES(?, ?, ?, NULL, NULL)",
                        (h, int(bonus), expires_at)
                    )
                    con.commit()
                    return code
                except sqlite3.IntegrityError:
                    continue
    raise RuntimeError("쿠폰 발급 실패(충돌 반복)")


async def redeem_coupon(user_id: int, code: str) -> tuple[bool, str]:
    h = _hash_coupon(code)
    now = datetime.now(_KST)

    async with clone_limit_lock:
        with sqlite3.connect(CLONE_LIMIT_DB) as con:
            row = con.execute(
                "SELECT bonus, expires_at, redeemed_by FROM coupons WHERE coupon_hash=?",
                (h,)
            ).fetchone()

            if not row:
                return False, "쿠폰 코드가 유효하지 않다냥!"
            bonus, expires_at, redeemed_by = row
            bonus = int(bonus)

            if redeemed_by is not None:
                return False, "이미 사용된 쿠폰이다냥!"

            if expires_at:
                try:
                    exp_dt = datetime.fromisoformat(expires_at)
                    if now > exp_dt:
                        return False, "쿠폰이 만료됐다냥!"
                except ValueError:
                    pass

            # ✅ 1회용 처리 (레이스 방지)
            con.execute(
                "UPDATE coupons SET redeemed_by=?, redeemed_at=? WHERE coupon_hash=? AND redeemed_by IS NULL",
                (int(user_id), now.isoformat(), h)
            )
            if con.total_changes == 0:
                return False, "이미 사용된 쿠폰이다냥!"

            # ✅ 오늘 보너스 한도 +bonus
            today = _kst_today_str()
            con.execute(
                """
                INSERT INTO clone_bonus(user_id, date, bonus) VALUES(?, ?, ?)
                ON CONFLICT(user_id, date) DO UPDATE SET bonus = bonus + excluded.bonus
                """,
                (int(user_id), today, bonus)
            )
            con.commit()

    new_cap = await get_clone_daily_cap(user_id)
    return True, f"쿠폰 적용 완료! 오늘 복제 공통 한도 +{bonus} → 총 {new_cap}회다냥!"


def _kst_today_str() -> str:
    return datetime.now(_KST).date().isoformat()


def get_clone_daily_limit(today: str = "") -> int:
    """KST 날짜마다 복제 기본 한도를 계산하여 이벤트 종료 시 자동으로 전환한다."""
    target_date = today or _kst_today_str()
    if target_date <= CLONE_PROMO_END_DATE:
        return CLONE_PROMO_DAILY_LIMIT
    return CLONE_DAILY_LIMIT


def get_generate26_daily_limit(today: str = "") -> int:
    """KST 날짜 기준 생성26 전용 일일 한도를 반환한다."""
    target_date = today or _kst_today_str()
    if target_date <= GENERATE26_PROMO_END_DATE:
        return GENERATE26_PROMO_DAILY_LIMIT
    return GENERATE26_DAILY_LIMIT


def _kst_next_midnight() -> datetime:
    now = datetime.now(_KST)
    tomorrow = now.date() + timedelta(days=1)
    return datetime.combine(tomorrow, datetime.min.time(), tzinfo=_KST)


def init_clone_limit_db():
    with sqlite3.connect(CLONE_LIMIT_DB) as con:
        # 테이블 생성, 기존 사용량 이동, 완료 기록을 한 트랜잭션으로 처리한다.
        con.execute("BEGIN IMMEDIATE")
        # 복제25 + 복제26 + 복제인페인트 공통 사용량
        con.execute("""
            CREATE TABLE IF NOT EXISTS clone_usage (
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                count INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (user_id, date)
            )
        """)
        # [추가] 전체 사용량 테이블
        con.execute("""
            CREATE TABLE IF NOT EXISTS global_usage (
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                count INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (user_id, date)
            )
        """)

        # 생성26 전용 사용량 (기존 공유 기록은 아래에서 최초 한 번 분리한다.)
        con.execute("""
            CREATE TABLE IF NOT EXISTS generate26_usage (
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                count INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (user_id, date)
            )
        """)
        # 복제26 개별 통계. 분리 기록이 없던 과거 사용량은 기존 분류를 유지한다.
        con.execute("""
            CREATE TABLE IF NOT EXISTS clone26_usage (
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                count INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (user_id, date)
            )
        """)

        # 쿠폰(1회용) + 일일 보너스(오늘 추가 한도) 테이블 추가
        con.execute("""
            CREATE TABLE IF NOT EXISTS clone_bonus (
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                bonus INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (user_id, date)
            )
        """)

        con.execute("""
            CREATE TABLE IF NOT EXISTS coupons (
                coupon_hash TEXT PRIMARY KEY,
                bonus INTEGER NOT NULL,      -- 예: 50
                expires_at TEXT,             -- ISO datetime (nullable)
                redeemed_by INTEGER,         -- nullable
                redeemed_at TEXT             -- ISO datetime (nullable)
            )
        """)

        con.execute("""
            CREATE TABLE IF NOT EXISTS quota_migrations (
                migration_key TEXT PRIMARY KEY,
                applied_at TEXT NOT NULL
            )
        """)
        migration_key = "clone25_clone26_shared_200_generate26_separate_v1"
        migrated = con.execute(
            "SELECT 1 FROM quota_migrations WHERE migration_key=?", (migration_key,)
        ).fetchone()
        if not migrated:
            # 기록된 복제26 횟수를 기존 복제 사용량에 더한다. 한도를 넘은 기록도 보존한다.
            con.execute("""
                INSERT INTO clone_usage(user_id, date, count)
                SELECT user_id, date, count FROM clone26_usage WHERE count > 0
                ON CONFLICT(user_id, date) DO UPDATE SET count=clone_usage.count + excluded.count
            """)
            # 기존 generate26_usage에는 복제26도 포함되어 있으므로 그 부분만 뺀다.
            con.execute("""
                UPDATE generate26_usage
                SET count=MAX(0, count - COALESCE((
                    SELECT count FROM clone26_usage
                    WHERE clone26_usage.user_id=generate26_usage.user_id
                      AND clone26_usage.date=generate26_usage.date
                      AND clone26_usage.count > 0
                ), 0))
            """)
            con.execute(
                "INSERT INTO quota_migrations(migration_key, applied_at) VALUES (?, ?)",
                (migration_key, datetime.now(_KST).isoformat()),
            )

        # 새 디버그 통계는 기존 한도용 기록과 분리하여 같은 시작 시점부터 집계한다.
        # 과거 생성23~25 및 복제25/복제인페인트는 정확히 분리할 수 없어 역산하지 않는다.
        con.execute("""
            CREATE TABLE IF NOT EXISTS debug_command_usage (
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                command_name TEXT NOT NULL,
                count INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (user_id, date, command_name)
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS debug_stats_meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        con.execute(
            "INSERT OR IGNORE INTO debug_stats_meta(key, value) VALUES (?, ?)",
            ("tracking_started_at", datetime.now(_KST).isoformat()),
        )

        con.commit()


async def check_and_increment_clone_limit(
        user_id: int, *, command_name: str = "복제25"
) -> tuple[bool, int, datetime]:
    """복제 공통 한도를 적용하고 복제26은 개별 통계도 함께 기록한다."""
    today = _kst_today_str()
    reset_at = _kst_next_midnight()
    async with clone_limit_lock:
        with sqlite3.connect(CLONE_LIMIT_DB) as con:
            row = con.execute(
                "SELECT count FROM clone_usage WHERE user_id=? AND date=?",
                (user_id, today)
            ).fetchone()
            current = int(row[0]) if row else 0

            b = con.execute(
                "SELECT bonus FROM clone_bonus WHERE user_id=? AND date=?",
                (user_id, today)
            ).fetchone()
            bonus = int(b[0]) if b else 0
            cap = get_clone_daily_limit(today) + bonus

            if current >= cap:
                return False, 0, reset_at

            if row:
                con.execute(
                    "UPDATE clone_usage SET count=count+1 WHERE user_id=? AND date=?",
                    (user_id, today)
                )
            else:
                con.execute(
                    "INSERT INTO clone_usage(user_id, date, count) VALUES(?, ?, 1)",
                    (user_id, today)
                )
                con.execute("DELETE FROM clone_usage WHERE date < date('now', '-30 day')")

            if command_name == "복제26":
                con.execute("""
                    INSERT INTO clone26_usage(user_id, date, count) VALUES (?, ?, 1)
                    ON CONFLICT(user_id, date) DO UPDATE SET count=count+1
                """, (user_id, today))
                con.execute("DELETE FROM clone26_usage WHERE date < date('now', '-30 day')")

            con.commit()
            return True, cap - (current + 1), reset_at


async def check_and_increment_generate26_limit(user_id: int) -> tuple[bool, int, datetime]:
    """복제 한도와 별개인 생성26 전용 일일 사용량을 적용한다."""
    today = _kst_today_str()
    cap = get_generate26_daily_limit(today)
    reset_at = _kst_next_midnight()

    async with clone_limit_lock:
        with sqlite3.connect(CLONE_LIMIT_DB) as con:
            row = con.execute(
                "SELECT count FROM generate26_usage WHERE user_id=? AND date=?",
                (user_id, today)
            ).fetchone()
            current = int(row[0]) if row else 0

            if current >= cap:
                return False, 0, reset_at

            if row:
                con.execute(
                    "UPDATE generate26_usage SET count=count+1 WHERE user_id=? AND date=?",
                    (user_id, today)
                )
            else:
                con.execute(
                    "INSERT INTO generate26_usage(user_id, date, count) VALUES(?, ?, 1)",
                    (user_id, today)
                )
                con.execute("DELETE FROM generate26_usage WHERE date < date('now', '-30 day')")

            con.commit()
            return True, cap - (current + 1), reset_at


@bot.command(name='쿠폰', aliases=['쿠폰사용', 'redeem'])
async def coupon_redeem_cmd(ctx, code: str):
    ok, msg = await redeem_coupon(ctx.author.id, code)
    await ctx.reply(msg, mention_author=False)


@bot.command(name='발급', aliases=['coupon_issue'])
async def coupon_issue_cmd(ctx, count: int = 1):
    if ctx.author.id != OWNER_ID:
        await ctx.reply("쿠폰 발급은 오너만 가능하다냥!", mention_author=False)
        return

    count = max(1, min(int(count), 20))
    codes = [await issue_coupon(bonus=50, valid_days=30) for _ in range(count)]

    try:
        await ctx.author.send("발급된 쿠폰 코드다냥:\n" + "\n".join(f"`{c}`" for c in codes))
        await ctx.reply(f"쿠폰 {count}개 발급 완료! DM 확인해달라냥.", mention_author=False)
    except discord.Forbidden:
        await ctx.reply("DM이 막혀있다냥! DM 허용 후 다시 시도해달라냥.", mention_author=False)


# [추가] 전체 한도 체크 함수
async def check_and_increment_global_limit(
        user_id: int, *, command_name: str = ""
) -> tuple[bool, int, datetime]:
    """
    returns: (allowed, remaining_after_increment, reset_time_kst)
    전체 한도가 차감된 요청을 새 디버그 통계에도 같은 트랜잭션으로 한 번 기록한다.
    """
    today = _kst_today_str()
    reset_at = _kst_next_midnight()

    async with clone_limit_lock:  # 같은 락 사용
        with sqlite3.connect(CLONE_LIMIT_DB) as con:
            con.execute("PRAGMA journal_mode=WAL;")
            con.execute("PRAGMA synchronous=NORMAL;")

            row = con.execute(
                "SELECT count FROM global_usage WHERE user_id=? AND date=?",
                (user_id, today)
            ).fetchone()

            current = int(row[0]) if row else 0
            if current >= GLOBAL_DAILY_LIMIT:
                return False, 0, reset_at

            if row:
                con.execute(
                    "UPDATE global_usage SET count=count+1 WHERE user_id=? AND date=?",
                    (user_id, today)
                )
                new_count = current + 1
            else:
                con.execute(
                    "INSERT INTO global_usage(user_id, date, count) VALUES(?, ?, 1)",
                    (user_id, today)
                )
                new_count = 1

            # 명령어를 정확히 일치시킨다. 복제인페인트/편집 등은 전체 사용량에만 포함한다.
            debug_command = (
                command_name
                if command_name in DEBUG_CLONE_COMMANDS + DEBUG_GENERATE_COMMANDS
                else "기타"
            )
            con.execute("""
                INSERT INTO debug_command_usage(user_id, date, command_name, count)
                VALUES (?, ?, ?, 1)
                ON CONFLICT(user_id, date, command_name) DO UPDATE SET count=count+1
            """, (user_id, today, debug_command))

            # 오래된 기록 정리
            con.execute("DELETE FROM global_usage WHERE date < date('now', '-30 day')")
            con.execute("DELETE FROM debug_command_usage WHERE date < date('now', '-30 day')")

            con.commit()
            remaining = GLOBAL_DAILY_LIMIT - new_count
            return True, remaining, reset_at


# [추가] 단순 조회 함수 (한도 명령어용)
async def get_user_limits(user_id: int):
    today = _kst_today_str()
    reset_at = _kst_next_midnight()
    async with clone_limit_lock:
        with sqlite3.connect(CLONE_LIMIT_DB) as con:
            row_clone = con.execute("SELECT count FROM clone_usage WHERE user_id=? AND date=?",
                                    (user_id, today)).fetchone()
            row_global = con.execute("SELECT count FROM global_usage WHERE user_id=? AND date=?",
                                     (user_id, today)).fetchone()
            row_generate26 = con.execute("SELECT count FROM generate26_usage WHERE user_id=? AND date=?",
                                         (user_id, today)).fetchone()

            clone_used = int(row_clone[0]) if row_clone else 0
            global_used = int(row_global[0]) if row_global else 0
            generate26_used = int(row_generate26[0]) if row_generate26 else 0

            return clone_used, generate26_used, global_used, reset_at


async def get_total_daily_usage() -> tuple[int, int, datetime]:
    """
    오늘 하루 전체 유저의 복제/전체 명령어 사용량 총합을 조회합니다.
    """
    today = _kst_today_str()
    reset_at = _kst_next_midnight()

    async with clone_limit_lock:
        with sqlite3.connect(CLONE_LIMIT_DB) as con:
            # 복제 명령어 (clone_usage)의 오늘 사용량 총합 계산
            clone_result = con.execute(
                "SELECT SUM(count) FROM clone_usage WHERE date=?",
                (today,)
            ).fetchone()
            # 결과가 None이거나 SUM이 NULL인 경우 0으로 처리
            total_clone_usage = clone_result[0] if clone_result and clone_result[0] is not None else 0

            # 전체 명령어 (global_usage)의 오늘 사용량 총합 계산
            global_result = con.execute(
                "SELECT SUM(count) FROM global_usage WHERE date=?",
                (today,)
            ).fetchone()
            # 결과가 None이거나 SUM이 NULL인 경우 0으로 처리
            total_global_usage = global_result[0] if global_result and global_result[0] is not None else 0

            return total_clone_usage, total_global_usage, reset_at


# 최근 7일 전체/복제/생성 사용량: 한도용 기존 통계 대신 새 디버그 기록만 사용한다.
async def get_weekly_usage_stats() -> tuple[dict, datetime]:
    """전체 한도 차감 요청을 집계한다. 집계 시작 전 날짜는 None으로 구분한다."""
    today_date = datetime.now(_KST).date()
    week_dates = [(today_date - timedelta(days=i)).isoformat() for i in range(7)]
    async with clone_limit_lock:
        with sqlite3.connect(CLONE_LIMIT_DB) as con:
            started_row = con.execute(
                "SELECT value FROM debug_stats_meta WHERE key='tracking_started_at'"
            ).fetchone()
            if not started_row:
                raise RuntimeError("디버그 통계가 초기화되지 않았다냥! 봇을 재시작해달라냥.")
            started_at = datetime.fromisoformat(started_row[0]).astimezone(_KST)
            started_date = started_at.date().isoformat()
            stats = {
                date: {field: (0 if date >= started_date else None)
                       for field in ('global', 'clone', 'generate')}
                for date in week_dates
            }
            rows = con.execute("""
                SELECT date, command_name, SUM(count)
                FROM debug_command_usage
                WHERE date >= ? AND date <= ?
                GROUP BY date, command_name
            """, (max(week_dates[-1], started_date), week_dates[0])).fetchall()

    for date, command_name, count in rows:
        counts = stats.get(date)
        if counts is None or counts['global'] is None:
            continue
        count = int(count or 0)
        counts['global'] += count
        if command_name in DEBUG_CLONE_COMMANDS:
            counts['clone'] += count
        elif command_name in DEBUG_GENERATE_COMMANDS:
            counts['generate'] += count
    return stats, started_at


@bot.command()
async def 냥냥(ctx):
    print(f"INFO: User ({ctx.author.id}) used command '냥냥' in channel {ctx.channel.id}")
    await ctx.send('냥냥! 무엇을 도와드릴까요?')


@bot.command()
async def 주사위(ctx):
    print(f"INFO: User ({ctx.author.id}) used command '주사위' in channel {ctx.channel.id}")
    # ... (원본 로직 유지) ...
    await ctx.reply("도전을 받아들이겠다냥!")
    await ctx.send("주사위를 굴립니다. 데굴데굴~")
    result, _color, bot_roll, user_roll = dice()
    embed = discord.Embed(title="주사위 게임 결과", description=None, color=_color)
    embed.add_field(name="냥냥이의 숫자", value=":game_die: " + bot_roll, inline=True)
    embed.add_field(name=ctx.author.name + "의 숫자", value=":game_die: " + user_roll, inline=True)
    embed.set_footer(text="결과: " + result)
    await ctx.send(embed=embed)
    if (result == "승리"):
        await ctx.send("냥냥! 제가 졌네요~")
    elif (result == "무승부"):
        await ctx.send("냥냥! 비겼네요~")
    elif (result == "패배"):
        await ctx.send("냥냥! 제가 이겼다구요~")


@bot.command(aliases=['뽑기', '당첨'])
async def 추첨(ctx, *args):
    prompt_str = ", ".join(args) if args else "없음"
    print(
        f"INFO: User ({ctx.author.id}) used command '추첨' in channel {ctx.channel.id}. Choices: {prompt_str}")
    if not args:
        await ctx.send("냥냥! 추첨할 대상이 없다냥! `&추첨 사람1 사람2 ...` 형식으로 입력해달라냥!")
        return
    # ... (원본 로직 유지) ...
    arguments = ', '.join(args)
    await ctx.send(f'냥냥! 총 {len(args)}명이 추첨 대상이다냥!')
    embed = discord.Embed(title="추첨자 명단", description=arguments, color=0xFFFFFF)
    await ctx.send(embed=embed)
    await ctx.send("두구두구냥~ 행운의 당첨자는 바로! 냥냥냥~!")
    choicelist = random.choice(args)
    embed = discord.Embed(title="당첨자", description=choicelist, color=0xFFFFFF)
    await ctx.send(embed=embed)
    await ctx.send("축하한다냥!")


@bot.command(aliases=['분배금', '경매'])
async def 분배(ctx, N_str, amount_str):  # 타입 힌트 제거, 원본 유지
    print(
        f"INFO: User ({ctx.author.id}) used command '분배' in channel {ctx.channel.id}. N: {N_str}, Amount: {amount_str}")
    try:
        N = int(N_str)
        amount = int(amount_str)
    except ValueError:
        await ctx.send("냥냥! 숫자 입력이 잘못되었다냥! `&분배 인원수 총금액` 형식으로 입력해달라냥!")
        return
    # ... (원본 로직 유지) ...
    if int(N) > int(amount): N, amount = amount, N
    dist = distribution(int(N), int(amount))
    if int(N) < 1 or int(amount) < 1:
        await ctx.send(f'입력이 잘못된 것 같다냥!\n&분배금 인원 수령가격')
    else:
        await ctx.send("냥냥! 비싼 아이템을 얻은 거냥?")
        await ctx.send(f'총 {N}명에게 {number_to_korean(int(amount))}메소를 분배 하겠다냥!')
        embed = discord.Embed(title="분배금 계산", description="분배금 : " + number_to_korean(int(dist)), color=0xFFFFFF)
        await ctx.send(embed=embed)
        await ctx.send("이렇게 분배하면 모두 " + number_to_korean(int(dist * 0.95)) + "메소씩 공평하게 나눠 가진다냥!")


@bot.command(aliases=['EXP쿠폰', 'EXP', 'exp교환권', 'exp', 'Exp', 'exp쿠폰'])
async def EXP교환권(ctx, startlevel_str, endlevel_str="0"):  # 타입 힌트 제거
    print(
        f"INFO: User ({ctx.author.id}) used command 'EXP교환권' in channel {ctx.channel.id}. Start: {startlevel_str}, End: {endlevel_str}")
    try:
        startlevel = int(startlevel_str)
        endlevel = int(endlevel_str)
    except ValueError:
        await ctx.send("냥냥! 레벨은 숫자로 입력해달라냥!")
        return
    # ... (원본 로직 유지) ...
    await ctx.send('냥냥! EXP 교환권을 모아온거냥?')
    if (int(startlevel) > int(endlevel) and endlevel != 0): startlevel, endlevel = endlevel, startlevel
    calculated_exp = EXPcal(int(startlevel), int(endlevel) if endlevel != 0 else 0)
    if endlevel == 0:
        percent_val = round(100 / calculated_exp * 100, 5) if calculated_exp > 0 else 0
        embed = discord.Embed(title=f"{int(startlevel)}레벨에서 레벨업하기 위해 필요한 EXP교환권 갯수",
                              description=f"{calculated_exp}개 (EXP교환권 100개 당 {percent_val}%)", color=0x007FFF)
    else:
        embed = discord.Embed(title=f"{int(startlevel)}레벨에서 {endlevel}레벨까지 필요한 EXP교환권 갯수",
                              description=f"{calculated_exp}개", color=0x007FFF)
    embed.set_thumbnail(url="https://raw.githubusercontent.com/def-fault-self/Project-Nyan/main/img_exp.png")
    await ctx.send(embed=embed)


@bot.command(aliases=['상급EXP쿠폰', '상급EXP', '상급exp교환권', '상급exp', '상급Exp', '상급exp쿠폰'])
async def 상급EXP교환권(ctx, startlevel_str, endlevel_str="0"):
    print(
        f"INFO: User ({ctx.author.id}) used command '상급EXP교환권' in channel {ctx.channel.id}. Start: {startlevel_str}, End: {endlevel_str}")
    try:
        startlevel = int(startlevel_str)
        endlevel = int(endlevel_str)
    except ValueError:
        await ctx.send("냥냥! 레벨은 숫자로 입력해달라냥!")
        return
    # ... (원본 로직 유지) ...
    await ctx.send('냥냥! 상급 EXP 교환권을 모아온거냥?')
    if (int(startlevel) > int(endlevel) and endlevel != 0): startlevel, endlevel = endlevel, startlevel
    calculated_exp = EXPcal2(int(startlevel), int(endlevel) if endlevel != 0 else 0)
    if endlevel == 0:
        percent_val = round(100 / calculated_exp * 100, 5) if calculated_exp > 0 else 0
        embed = discord.Embed(title=f"{int(startlevel)}레벨에서 레벨업하기 위해 필요한 상급EXP교환권 갯수",
                              description=f"{calculated_exp}개 (EXP교환권 100개 당 {percent_val}%)", color=0x007FFF)
    else:
        embed = discord.Embed(title=f"{int(startlevel)}레벨에서 {endlevel}레벨까지 필요한 상급EXP교환권 갯수",
                              description=f"{calculated_exp}개", color=0x007FFF)
    embed.set_thumbnail(url="https://raw.githubusercontent.com/def-fault-self/Project-Nyan/main/img_exp2.png")
    await ctx.send(embed=embed)


@bot.command(aliases=['극한성장의비약'])
async def 극성비(ctx, level_str):
    print(
        f"INFO: User ({ctx.author.id}) used command '극성비' in channel {ctx.channel.id}. Level: {level_str}")
    try:
        level = int(level_str)
    except ValueError:
        await ctx.send("냥냥! 레벨은 숫자로 입력해달라냥!")
        return
    # ... (원본 로직 유지) ...
    await ctx.send('냥냥! 극한 성장의 비약을 가져왔냥?')
    await ctx.send(f"어디보자냥~ {level}레벨에서 먹으면 어떻게 되는지 알아보겠다냥!")
    embed = discord.Embed(title=f"{level}레벨 때 극성비를 먹었을 때 오르는 경험치량", description=str(EXPPotion(int(level))) + "%",
                          color=0xFF1493)
    embed.set_thumbnail(url="https://raw.githubusercontent.com/def-fault-self/Project-Nyan/main/img_potion.png")
    await ctx.send(embed=embed)


@bot.command(aliases=['초월성장의비약', '초월비'])
async def 초성비(ctx, level_str):
    print(
        f"INFO: User ({ctx.author.id}) used command '초성비' in channel {ctx.channel.id}. Level: {level_str}")
    try:
        level = int(level_str)
    except ValueError:
        await ctx.send("냥냥! 레벨은 숫자로 입력해달라냥!")
        return
    # ... (원본 로직 유지) ...
    await ctx.send('냥냥! 초월 성장의 비약을 가져왔냥?')
    await ctx.send(f"어디보자냥~ {level}레벨에서 먹으면 어떻게 되는지 알아보겠다냥!")
    embed = discord.Embed(title=f"{level}레벨 때 초성비를 먹었을 때 오르는 경험치량", description=str(EXPPotion2(int(level))) + "%",
                          color=0xFF1493)
    embed.set_thumbnail(url="https://raw.githubusercontent.com/def-fault-self/Project-Nyan/main/img_potion2.png")
    await ctx.send(embed=embed)


@bot.command(aliases=['몬스터파크', '익스트림', '익스트림몬스터파크'])
async def 익몬(ctx, level_str):
    print(
        f"INFO: User ({ctx.author.id}) used command '익몬' in channel {ctx.channel.id}. Level: {level_str}")
    try:
        level = int(level_str)
    except ValueError:
        await ctx.send("냥냥! 레벨은 숫자로 입력해달라냥!")
        return
    # ... (원본 로직 유지) ...
    await ctx.channel.send('냥냥! 익스트림 몬스터파크에 놀러가는거냥?')
    await ctx.send(f"어디보자냥~ {level}레벨에서 얼마나 경험치를 주는지 알아보겠다냥!")
    embed = discord.Embed(title=f"{level}레벨 때 익스트림 몬스터파크에서 오르는 경험치량", description="" + str(Extreme(int(level))) + "%",
                          color=0xFFFFFF)
    embed.set_thumbnail(url="https://raw.githubusercontent.com/def-fault-self/Project-Nyan/main/img_mon.png")
    await ctx.send(embed=embed)


@bot.command(aliases=['Vip', 'vip', '사우나', 'VIP사우나'])
async def VIP(ctx, level_str):
    print(
        f"INFO: User ({ctx.author.id}) used command 'VIP' in channel {ctx.channel.id}. Level: {level_str}")
    try:
        level = int(level_str)
    except ValueError:
        await ctx.send("냥냥! 레벨은 숫자로 입력해달라냥!")
        return
    # ... (원본 로직 유지) ...
    await ctx.channel.send('냥냥! VIP사우나에서 푹 쉬었냥?')
    await ctx.send(f"어디보자냥~ {level}레벨에서 얼마나 경험치를 주는지 알아보겠다냥!")
    embed = discord.Embed(title=f"{level}레벨 때 VIP 사우나에서 시간 당 오르는 경험치량", description="" + str(VIPexp(int(level))) + "%",
                          color=0xFFFF00)
    embed.set_thumbnail(url="https://raw.githubusercontent.com/def-fault-self/Project-Nyan/main/img_vip.png")
    await ctx.send(embed=embed)


@bot.command(aliases=['여친확률'])
async def 여친생길확률(ctx):
    print(f"INFO: User ({ctx.author.id}) used command '여친생길확률' in channel {ctx.channel.id}")
    await ctx.channel.send('...')


@bot.command(aliases=['사귀자', '사랑해'])
async def 데이트(ctx):
    print(f"INFO: User ({ctx.author.id}) used command '데이트' in channel {ctx.channel.id}")
    code_lines = [  # 이미지 URL 리스트
        'https://raw.githubusercontent.com/201611043/NyanNyan/main/1.png',
        'https://raw.githubusercontent.com/201611043/NyanNyan/main/2.png',
        'https://raw.githubusercontent.com/201611043/NyanNyan/main/3.png',
        'https://raw.githubusercontent.com/201611043/NyanNyan/main/4.png'
    ]
    random_code = random.choice(code_lines)
    try:
        # 임시 파일 저장 후 전송
        urllib.request.urlretrieve(str(random_code), "emoticon_temp.png")
        image = discord.File("emoticon_temp.png", filename="image.png")
        await ctx.send(file=image)
        os.remove("emoticon_temp.png")  # 임시 파일 삭제
    except Exception as e:
        await ctx.send("냥냥... 이미지를 불러오는데 실패했다냥.")
        print(f"ERROR: '데이트' command image fetch for  failed. URL: {random_code}, Reason: {e}")


@bot.command(aliases=['유저', '조회'])
async def 캐릭터(ctx, Search: str):
    print(f"INFO: User ({ctx.author.id}) used command '캐릭터' in channel {ctx.channel.id}. Search: {Search}")
    await ctx.reply('냥냥! 요청한 유저의 정보를 조회하고 있다냥!')
    level, job, world, guild, union, floor, src = Character(Search)

    if src == "-":  # Character 함수에서 오류 발생 또는 유저 없음
        await ctx.send(f"냥냥... '{Search}' 유저 정보를 찾을 수 없거나 조회 중 오류가 발생했다냥.")
        return

    special_script = ""  # 특별 유저 스크립트
    if Search == "아ship":
        special_script = "싹씹싹씹! 으윽.. 누가 나를 해킹하고 있다냥!"
    elif Search == "Blurpoint":
        special_script = "멋진 우리 주인님이다냥!"
    # ... (다른 특별 유저 스크립트) ...

    embed = discord.Embed(title=str(Search), url="https://maple.gg/u/" + str(Search), description=special_script,
                          color=0x00ff40)
    embed.set_author(name="캐릭터 검색 결과")
    try:
        # 이미지 파일 직접 다운로드 후 BytesIO로 전달
        async with aiohttp.ClientSession() as session:
            async with session.get(src) as resp:
                if resp.status == 200:
                    image_data = await resp.read()
                    image_file = discord.File(io.BytesIO(image_data), filename="character_image.png")
                    embed.set_thumbnail(url="attachment://character_image.png")
                    embed.add_field(name="레벨", value=Erase(level), inline=True)
                    embed.add_field(name="직업", value=job, inline=True)
                    embed.add_field(name="월드", value=world, inline=True)
                    embed.add_field(name="길드", value=guild, inline=True)
                    embed.add_field(name="유니온", value=union, inline=True)
                    embed.add_field(name="무릉", value=floor, inline=True)
                    await ctx.send(embed=embed, file=image_file)
                else:
                    await ctx.send("캐릭터 이미지를 불러오는데 실패했다냥.")
                    print(f"ERROR: '캐릭터' - Failed to download image for {Search} from {src}. Status: {resp.status}")
    except Exception as e:
        await ctx.send("캐릭터 정보 조회 중 오류가 발생했다냥...")
        print(f"ERROR: '캐릭터' command processing for {Search} failed. Reason: {e}")


@bot.command(aliases=['환산스탯', '스탯', '스텟', '스펙'])
async def 환산(ctx, Search: str):
    print(f"INFO: User ({ctx.author.id}) used command '환산' in channel {ctx.channel.id}. Search: {Search}")
    await ctx.reply('냥냥! 환산 계산기를 두드리는 중이다냥!')
    combPW, convST, hexaST, src = Conversion(Search)

    if src == "-":  # Conversion 함수에서 오류 발생
        await ctx.send(f"냥냥... '{Search}' 유저 환산 정보를 조회하는데 실패했거나 시간이 너무 오래 걸렸다냥.")
        return

    special_script = ""
    if Search == "아ship": special_script = "십십 재입대 언제해?"

    await ctx.send('내 전투력은 530000이다냥! 그렇지만 물론 풀파워로 싸울 생각은 없으니 걱정하지 말라냥!')
    embed = discord.Embed(title=str(Search), url="https://maplescouter.com/info?name=" + str(Search),
                          description=special_script, color=0x00ff40)
    embed.set_author(name="전투력 조회 결과")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(src) as resp:
                if resp.status == 200:
                    image_data = await resp.read()
                    image_file = discord.File(io.BytesIO(image_data), filename="conversion_image.png")
                    embed.set_thumbnail(url="attachment://conversion_image.png")
                    embed.add_field(name="전투력", value=combPW, inline=True)
                    embed.add_field(name="환산", value=convST, inline=True)
                    embed.add_field(name="헥사", value=hexaST, inline=True)
                    await ctx.send(embed=embed, file=image_file)
                else:
                    await ctx.send("환산 캐릭터 이미지를 불러오는데 실패했다냥.")
                    print(f"ERROR: '환산' - Failed to download image for {Search} from {src}. Status: {resp.status}")
    except Exception as e:
        await ctx.send("환산 정보 조회 중 오류가 발생했다냥...")
        print(f"ERROR: '환산' command processing for {Search} failed. Reason: {e}")


@bot.command(aliases=['추가옵션', '무기'])
async def 추옵(ctx, Search: str):
    print(f"INFO: User ({ctx.author.id}) used command '추옵' in channel {ctx.channel.id}. Search: {Search}")
    await ctx.channel.send('냥냥! 무기에 붙는 추가옵션이 궁금한거냥?')
    df_option = Option(Search)
    if df_option.empty:
        await ctx.send(f"냥냥... '{Search}' 무기의 추가옵션 정보를 찾을 수 없다냥.")
        return

    # 데이터프레임 행 개수에 따라 유동적으로 body 생성 (최대 4개 행)
    body_data = []
    for i in range(min(len(df_option.index), 4)):
        body_data.append(remove_decimal_from_list(df_option.iloc[i].values.tolist())[1:])

    output = t2a(
        header=list(df_option.columns)[1:],
        body=body_data,
        first_col_heading=True
    )
    code_block_content = f"```{output}```"
    embed = discord.Embed(title=f"{Search}의 추가옵션표", description=code_block_content, color=0x00FF7F)
    await ctx.send(embed=embed)


@bot.command(aliases=['6차', 'HEXA', 'Hexa', 'hexa'])
async def 헥사(ctx, startlevel_str, endlevel_str="0"):
    print(
        f"INFO: User ({ctx.author.id}) used command '헥사' in channel {ctx.channel.id}. Start: {startlevel_str}, End: {endlevel_str}")
    try:
        startlevel = int(startlevel_str)
        endlevel = int(endlevel_str)
    except ValueError:
        await ctx.send("냥냥! 레벨은 숫자로 입력해달라냥!")
        return

    if not (0 <= startlevel <= 29 and 0 <= endlevel <= 29):  # 데이터 유효 범위 검사
        await ctx.send("냥냥! 헥사 정보는 0레벨부터 29레벨까지만 제공된다냥.")
        return

    await ctx.send('냥냥! 솔에르다를 모아온 거냥?')
    if (int(startlevel) > int(endlevel) and endlevel != 0):
        startlevel, endlevel = endlevel, startlevel

    Sol6, Piece6, Sol5, Piece5, Sol4, Piece4 = Hexa(int(startlevel), int(endlevel) if endlevel != 0 else 0)

    title_str = ""
    if (int(startlevel) == 0 and int(endlevel) == 0):  # 해금 비용
        Sol6, Piece6 = "-", "-"
        Sol5, Piece5 = 4, 75
        Sol4, Piece4 = 3, 50
        title_str = "해금에 필요한 솔에르다와 솔에르다 조각 갯수"
    elif endlevel == 0:
        title_str = f"{int(startlevel)}레벨에서 레벨업하기 위해 필요한 \n 솔에르다와 솔에르다 조각 갯수"
    else:
        title_str = f"{int(startlevel)}레벨에서 {endlevel}레벨까지 필요한 \n 솔에르다와 솔에르다 조각 갯수"

    d = [["Origin(6th)", Sol6, Piece6], ["Reinforce(5th)", Sol5, Piece5], ["Mastery(4th)", Sol4, Piece4]]
    df_display = pd.DataFrame(d, columns=['Kind', 'Sol Erda', 'Sol Piece'])
    output = t2a(header=list(df_display.columns), body=[row.values.tolist() for _, row in df_display.iterrows()],
                 first_col_heading=True)
    code_block_content = f"```{output}```"
    embed = discord.Embed(title=title_str, description=code_block_content, color=0x7b40e3)
    embed.set_thumbnail(url="https://raw.githubusercontent.com/def-fault-self/Project-Nyan/main/img_six.png")
    await ctx.send(embed=embed)


@bot.command(aliases=['명령어', '도움말', '도움'])
async def help(ctx):
    print(f"INFO: User ({ctx.author.id}) used command 'help' in channel {ctx.channel.id}")
    embed = discord.Embed(title="▶ 냥냥이 명령어 모음집", description="&명령어 &도움말 &도움 &help", color=0x00D4FF)
    # ... (도움말 내용은 원본 유지) ...
    embed.add_field(name="", value="", inline=False)
    embed.add_field(name="▶ 메이플 유틸리티", value="", inline=False)
    embed.add_field(name="&극성비 <레벨>", value="\n-  N레벨에 극성비로 오르는 경험치를 계산합니다.", inline=False)
    embed.add_field(name="&초성비 <레벨>", value="\n-  N레벨에 초성비로 오르는 경험치를 계산합니다.", inline=False)
    embed.add_field(name="&익몬 <레벨>", value="- N레벨에 익몬으로 오르는 경험치를 계산합니다.", inline=False)
    embed.add_field(name="&VIP <레벨>", value="- N레벨에 VIP 사우나 경험치를 계산합니다.", inline=False)
    embed.add_field(name="&EXP교환권 <시작레벨> [끝레벨]", value="- N레벨 필요 경험치 또는 N->M레벨 필요 경험치를 계산합니다.", inline=False)
    embed.add_field(name="&상급EXP교환권 <시작레벨> [끝레벨]", value="- N레벨 필요 상급 경험치 또는 N->M레벨 필요 상급 경험치를 계산합니다.", inline=False)
    embed.add_field(name="&헥사 <시작레벨> [끝레벨]", value="- N레벨 또는 N->M레벨 필요 헥사 재료를 검색합니다. (0 입력 시 해금 비용)", inline=False)
    embed.add_field(name="&추옵 <무기이름>", value="- 무기에 붙는 추가옵션 등급표를 검색합니다.", inline=False)
    embed.add_field(name="&캐릭터 <닉네임>", value="- 유저의 캐릭터 정보를 검색합니다.", inline=False)
    embed.add_field(name="&환산 <닉네임>", value="- 유저의 환산을 검색합니다.", inline=False)
    embed.add_field(name="&분배 <인원수> <총금액>", value="- N명에게 나눌 분배금을 계산합니다.", inline=False)
    embed.add_field(name="", value="", inline=False)
    embed.add_field(name="▶ 음성 채널 유틸리티", value="", inline=False)
    embed.add_field(name="&입장", value="- 냥냥이를 음성 채널에 들여보냅니다.", inline=False)
    embed.add_field(name="&퇴장", value="- 냥냥이를 음성 채널에서 내보냅니다.", inline=False)
    # embed.add_field(name="&재생 <유튜브링크/검색어>", value="- 해당 링크의 유튜브 음악을 재생합니다", inline=False) # 주석 처리된 부분은 그대로
    # embed.add_field(name="&볼륨 <0-100>", value="- 유튜브 음악 볼륨을 조절합니다.", inline=False)
    embed.add_field(name="&tts <할말>", value="- TTS기능으로 말합니다", inline=False)
    embed.add_field(name="", value="", inline=False)
    embed.add_field(name="▶ 이미지 생성 (NovelAI / Gemini / HuggingFace)", value="", inline=False)
    embed.add_field(name="&생성23 <프롬프트>", value="- 2023년 그림 모델로 이미지를 생성합니다. (v3)", inline=False)
    embed.add_field(name="&생성24 <프롬프트>", value="- 2024년 그림 모델로 이미지를 생성합니다. (v4)", inline=False)
    embed.add_field(name="&생성25 <프롬프트>", value="- 2025년 그림 모델로 이미지를 생성합니다. (v4.5)", inline=False)
    embed.add_field(
        name="&생성26 <프롬프트>",
        value="- 2026년 그림 모델로 이미지를 생성합니다. (v5, 생성26 전용 일일 200회)",
        inline=False
    )
    embed.add_field(name="&재생성", value="- 마지막 NovelAI 생성 프롬프트로 이미지를 다시 생성합니다.", inline=False)
    embed.add_field(name="&젬편집 <프롬프트>", value="- (Gemini) 첨부 이미지와 프롬프트를 기반으로 이미지를 편집/생성합니다.", inline=False)
    embed.add_field(name="&표정 <표정프롬프트>", value="- (NovelAI) 첨부 이미지의 표정을 변경합니다.", inline=False)
    embed.add_field(name="&제거", value="- (NovelAI) 첨부 이미지의 말풍선/텍스트 등을 제거합니다.", inline=False)
    embed.add_field(name="&편집 <프롬프트>", value="- (NovelAI) 첨부 이미지를 프롬프트 기반으로 채색/편집합니다.", inline=False)
    embed.add_field(name="&확대", value="- (HuggingFace) 첨부 이미지를 2배 확대합니다.", inline=False)
    embed.add_field(name="   ㄴ 생성 시 프롬프트에 `랜덤`, `네모`, `세로` 키워드 사용 가능", value="", inline=False)
    embed.add_field(name="", value="", inline=False)
    embed.add_field(name="▶ 기타", value="", inline=False)
    embed.add_field(name="&데이트", value="- 냥냥이에게 데이트를 신청합니다.", inline=False)
    embed.add_field(name="&여친생길확률", value="- 여자친구가 생길 확률을 계산합니다.", inline=False)
    embed.add_field(name="/forget [페르소나]", value="- (슬래시 명령어) 현재 채널 대화 기록을 잊습니다.", inline=False)
    embed.add_field(name="/createthread <스레드이름>", value="- (슬래시 명령어) 냥냥이가 모든 메시지에 답하는 스레드를 생성합니다.", inline=False)
    embed.add_field(name="/clear", value="- (슬래시 명령어, DM전용) DM 대화에서 냥냥이 메시지를 삭제합니다.", inline=False)
    embed.add_field(name="/wake", value="- (슬래시 명령어) 검냥이를 깨웁니다.", inline=False)
    await ctx.send(embed=embed)


@bot.command()
async def tts(ctx, *, text: str):
    print(
        f"INFO: User ({ctx.author.id}) used command 'tts' in channel {ctx.channel.id}. Text: '{text[:50]}...'")
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send('음성 채널에 먼저 입장해주세요.')
        return

    voice_client = ctx.voice_client
    if not voice_client:  # 봇이 음성 채널에 없으면 연결 시도
        try:
            voice_client = await ctx.author.voice.channel.connect()
        except Exception as e:
            await ctx.send(f"음성 채널 연결 중 오류 발생: {e}")
            print(f"ERROR: 'tts' command - Failed to connect to voice channel for . Reason: {e}")
            return

    try:
        tts_obj = gTTS(text=text, lang='ko')
        # 임시 파일 이름에 고유성을 부여하여 동시 사용 문제 완화 시도
        temp_tts_file = f'tts_temp_{ctx.message.id}.mp3'
        tts_obj.save(temp_tts_file)

        # 재생이 끝나면 파일을 삭제하는 콜백 함수 정의
        def after_playing(error):
            if error:
                print(f"ERROR: TTS playback error for : {error}")
            try:
                if os.path.exists(temp_tts_file):
                    os.remove(temp_tts_file)
            except Exception as e_del:
                print(f"Warning: Could not delete temp TTS file {temp_tts_file}: {e_del}")

        voice_client.play(discord.FFmpegPCMAudio(temp_tts_file), after=after_playing)
    except Exception as e:
        await ctx.send(f"TTS 생성 또는 재생 중 오류가 발생했다냥: {e}")
        print(f"ERROR: 'tts' command processing for  failed. Reason: {e}")


@bot.event
async def on_member_join(member):
    # fmt = '{0.mention}, {1.name} 에 온 것을 환영한다냥!'
    # channel_id_to_send = "507201204997062658" # 실제 채널 ID로 변경 필요
    # channel = member.guild.get_channel(int(channel_id_to_send))
    # if channel:
    #     await channel.send(fmt.format(member, member.guild)) # 원본 코드에서는 member.server 사용, guild로 변경
    # else:
    #     print(f"Warning: Welcome channel ID {channel_id_to_send} not found in server {member.guild.name}")
    print(f"INFO: Member {member} ({member.id}) joined server {member.guild.name} ({member.guild.id})")


async def _process_prompt_and_get_payload_parts(ctx: commands.Context, command_name: str, original_prompt: str,
                                                temp_messages_to_delete: list):
    # -----------------------------------------------------------
    # [수정됨 1] 프롬프트 분리 로직 추가 (&부정 키워드 처리)
    # -----------------------------------------------------------
    user_negative_prompt = ""
    # '&부정' 키워드가 있으면 분리
    if "&부정" in original_prompt:
        parts = original_prompt.split("&부정", 1)
        original_prompt = parts[0].strip()  # 앞부분은 긍정 프롬프트로 사용
        user_negative_prompt = parts[1].strip()  # 뒷부분은 부정 프롬프트로 저장

    api_prompt = original_prompt
    generated_random_tags_for_display = ""

    api_prompt, generated_random_tags_for_display = apply_random_prompt_tags(api_prompt)

    target_width, target_height = 0, 0
    model_id, base_caption_prefix, base_caption_suffix = "", "", ""

    # 기본값 설정 (초기화)
    negative_prompt_data = ""

    # -----------------------------------------------------------
    # [수정됨 2] 기본 네가티브 프롬프트들을 변수로 분리하고 조건문 적용
    # -----------------------------------------------------------

    # 1. 생성25(v4.5)용 기본 네가티브
    default_uc_v45 = "{{{{{{{{{{worst quality, bad quality, lowres}}}}}}}}}}, bad anatomy, {{{{bad hands}}}}, {artist:bkub}, displeasing, very displeasing, bad perspective, bad proportions, bad aspect ratio, bad face, long face, bad teeth, bad neck, long neck, bad arm, bad ass, bad leg, bad feet, bad reflection, bad shadow, bad link, bad source, wrong hand, wrong feet, missing limb, missing eye, missing tooth, missing ear, missing finger, extra faces, extra eyes, extra eyebrows, extra mouth, extra tongue, extra teeth, extra ears, extra breasts, extra arms, extra hands, extra legs, extra digits, fewer digits, cropped head, cropped torso, cropped shoulders, cropped arms, cropped legs, mutation, deformed, disfigured, unfinished, chromatic aberration, text, error, jpeg artifacts, watermark, scan, scan artifacts, ugly man}}}, {{bald}}, {{bald hair}}"

    # 2. 생성23(v3)용 기본 네가티브
    default_uc_v3 = "lowres, {bad}, error, fewer, extra, missing, worst quality, jpeg artifacts, bad quality, watermark, unfinished, displeasing, chromatic aberration, signature, extra digits, artistic error, username, scan, [abstract], ai-generated, normal quality, bad quality, low quality, worst quality, lowres, displeasing, bad anatomy, bad eyes, bad pupils, bad hands, text, blurry, error, missing finger, extra digits, fewer digits, cropped, JPEG artifacts, signature, watermark, username, artist name, bad face, duplicate, mutation, deformed, disfigured, long neck, bad proportions, fat, bad, missing, artistic error, chromatic aberration, scan, scan artifacts, Deviant art, bb (baalbuddy), lipstick, lips, jewelry"

    # 3. 생성24(v4)용 기본 네가티브
    default_uc_v4 = "ai-generated, normal quality, bad quality, low quality, worst quality, lowres, displeasing, bad anatomy, bad eyes, bad pupils, bad hands, text, blurry, error, missing finger, extra digits, fewer digits, cropped, JPEG artifacts, signature, watermark, username, artist name, bad face, duplicate, mutation, deformed, disfigured, long neck, bad proportions, fat, bad, missing, artistic error, chromatic aberration, scan, scan artifacts, Deviant art, bb (baalbuddy), lipstick, lips, jewelry"

    if command_name == '생성25':
        default_width, default_height, square_size = 1216, 832, 1024
        model_id = "nai-diffusion-4-5-full"
        base_caption_suffix = ",amazing quality, very aesthetic, absurdres, masterpiece, highres, hyper detailed"

        # 사용자가 입력한 부정 프롬프트가 있으면 그걸 쓰고, 없으면 기본값 사용
        final_uc = user_negative_prompt if user_negative_prompt else default_uc_v45

        negative_prompt_data = {
            "caption": {
                "base_caption": final_uc,
                "char_captions": []
            },
            "legacy_uc": False
        }

    elif command_name == '생성23':
        default_width, default_height, square_size = 1216, 832, 1024
        model_id = "nai-diffusion-3"
        base_caption_prefix = "best quality, masterpiece, "
        base_caption_suffix = " ,amazing quality, very aesthetic, absurdres"

        # 생성23(v3)는 문자열 그대로 들어감
        final_uc = user_negative_prompt if user_negative_prompt else default_uc_v3
        negative_prompt_data = final_uc

    elif command_name == '생성24':
        default_width, default_height, square_size = 1216, 832, 1024
        model_id = "nai-diffusion-4-full"
        base_caption_suffix = ",amazing quality, very aesthetic, absurdres, masterpiece, highres, hyper detailed"

        final_uc = user_negative_prompt if user_negative_prompt else default_uc_v4

        negative_prompt_data = {
            "caption": {
                "base_caption": final_uc,
                "char_captions": []
            },
            "legacy_uc": False
        }
    else:
        await ctx.send(f"알 수 없는 명령어 타입입니다: {command_name}", reference=ctx.message, mention_author=False)
        return None, None, None, ""

    # (이하 기존 크기 조정 로직 유지)
    target_width, target_height = default_width, default_height
    prompt_for_size_check = original_prompt  # 랜덤 태그 붙기 전, 원본(긍정부분)에서 키워드 체크

    if "네모" in prompt_for_size_check:
        target_width, target_height = square_size, square_size
        msg = await ctx.send("프롬프트에 '네모' 키워드가 감지되어 정사각형 이미지로 생성한다냥!", reference=ctx.message,
                             mention_author=False)
        temp_messages_to_delete.append(msg)
        api_prompt = re.sub(r'\s*네모\s*', ' ', api_prompt).strip()
        api_prompt = re.sub(r'\s{2,}', ' ', api_prompt).strip()
    elif "세로" in prompt_for_size_check:
        if command_name == '생성23':
            target_width, target_height = 832, 1216
            msg_text = "세로 이미지(832x1216)로 생성한다냥!"
        elif command_name in ['생성25', '생성24']:
            target_width, target_height = default_height, default_width
            msg_text = "세로 이미지로 생성한다냥!"
        else:
            target_width, target_height = default_height, default_width
            msg_text = "세로 이미지로 생성한다냥! (기본 설정)"

        msg = await ctx.send(f"프롬프트에 '세로' 키워드가 감지되어 {msg_text}", reference=ctx.message, mention_author=False)
        temp_messages_to_delete.append(msg)
        api_prompt = re.sub(r'\s*세로\s*', ' ', api_prompt).strip()
        api_prompt = re.sub(r'\s{2,}', ' ', api_prompt).strip()

    api_prompt = re.sub(r'^[\s,]+|[\s,]+$', '', api_prompt).strip()
    api_prompt = re.sub(r'(,\s*){2,}', ', ', api_prompt).strip()

    common_params = {
        "params_version": 3, "scale": 6, "sampler": "k_euler_ancestral", "steps": 28,
        "seed": random.randint(0, 2 ** 32 - 1), "n_samples": 1, "noise_schedule": "karras",
        "cfg_rescale": 0.3, "controlnet_strength": 1, "deliberate_euler_ancestral_bug": False,
        "dynamic_thresholding": False, "prefer_brownian": True, "skip_cfg_above_sigma": None,
        "legacy": False, "legacy_uc": False, "legacy_v3_extend": False, "use_coords": False,
        "qualityToggle": True, "autoSmea": True, "ucPreset": 0, "add_original_image": True
    }

    current_api_prompt_for_payload = api_prompt
    if not current_api_prompt_for_payload.strip():
        current_api_prompt_for_payload = "masterpiece"

    final_payload_structure = {}

    if command_name == '생성23':
        common_params.update({"scale": 6, "steps": 28, "cfg_rescale": 0.3, "sm": False, "sm_dyn": False,
                              "negative_prompt": negative_prompt_data})
        assembled_input = current_api_prompt_for_payload
        if base_caption_prefix.strip(): assembled_input = base_caption_prefix + assembled_input
        if base_caption_suffix.strip(): assembled_input += base_caption_suffix
        final_payload_structure = {"model": model_id, "input": assembled_input, "parameters": common_params}
    elif command_name in ['생성25', '생성24']:
        assembled_caption = current_api_prompt_for_payload + base_caption_suffix
        common_params.update({
            "v4_prompt": {"caption": {"base_caption": assembled_caption, "char_captions": []}, "use_coords": False,
                          "use_order": True},
            "v4_negative_prompt": negative_prompt_data, "characterPrompts": [],
            "reference_information_extracted_multiple": [], "reference_image_multiple": [],
            "reference_strength_multiple": []
        })
        final_payload_structure = {"model": model_id, "parameters": common_params}

    final_payload_structure["parameters"]["width"] = target_width
    final_payload_structure["parameters"]["height"] = target_height

    if command_name == '생성23':
        current_input = final_payload_structure.get("input", "")
        current_input = re.sub(r'^[\s,]+|[\s,]+$', '', current_input).strip()
        final_payload_structure["input"] = current_input if current_input else "masterpiece"
    elif command_name in ['생성25', '생성24']:
        base_caption = final_payload_structure["parameters"]["v4_prompt"]["caption"]["base_caption"]
        base_caption = re.sub(r'^[\s,]+|[\s,]+$', '', base_caption).strip()
        final_payload_structure["parameters"]["v4_prompt"]["caption"][
            "base_caption"] = base_caption if base_caption else "masterpiece"

    if not model_id:
        print(f"CRITICAL ERROR: model_id is not set before returning from _process_prompt_and_get_payload_parts!")
        return None, None, None, ""

    return model_id, api_prompt, final_payload_structure, generated_random_tags_for_display


# --- NovelAI Diffusion v5 (&생성26) ---
# 2026-08 NovelAI 웹 클라이언트에서 캡처한 v5 generate payload를 기준으로 구성.
V5_26_QUALITY_SUFFIX = ""
V5_26_DEFAULT_UC = (
    "lowres, artistic error, film grain, scan artifacts, worst quality, bad quality, jpeg artifacts, "
    "very displeasing, chromatic aberration, dithering, halftone, screentone, multiple views, logo, "
    "too many watermarks, negative space, blank page"
)


def _apply_generation_size_keywords(prompt_text: str) -> tuple[str, int, int, str]:
    """
    생성23~26 공통 크기 규칙.
    기본: 가로 1216x832 / '네모': 1024x1024 / '세로': 832x1216
    둘 다 들어오면 기존 규칙과 동일하게 '네모'를 우선한다.
    """
    cleaned = (prompt_text or "").strip()
    width, height, mode = 1216, 832, "가로"

    if "네모" in cleaned:
        width, height, mode = 1024, 1024, "네모"
        cleaned = re.sub(r'\s*네모\s*', ' ', cleaned)
        # 크기 키워드가 둘 다 프롬프트에 남는 상황 방지
        cleaned = re.sub(r'\s*세로\s*', ' ', cleaned)
    elif "세로" in cleaned:
        width, height, mode = 832, 1216, "세로"
        cleaned = re.sub(r'\s*세로\s*', ' ', cleaned)

    cleaned = re.sub(r'\s{2,}', ' ', cleaned).strip(' ,')
    return cleaned, width, height, mode


def _build_v5_26_payload(original_prompt: str) -> tuple[dict, str, str]:
    """&생성26용 NovelAI Diffusion v5 payload를 만든다.

    Returns:
        (payload, final_prompt, generated_random_tags)
    """
    prompt_text = (original_prompt or "").strip()
    user_negative_prompt = ""

    # 기존 생성 명령어와 동일하게 &부정 뒤의 내용을 사용자 UC로 사용할 수 있게 함.
    if "&부정" in prompt_text:
        positive, negative = prompt_text.split("&부정", 1)
        prompt_text = positive.strip()
        user_negative_prompt = negative.strip()

    # v5도 생성23~25와 똑같은 크기 규칙을 강제로 적용한다.
    prompt_text, width, height, _size_mode = _apply_generation_size_keywords(prompt_text)
    prompt_text, generated_random_tags = apply_random_prompt_tags(prompt_text)

    if not prompt_text:
        prompt_text = "masterpiece"

    # 웹 UI 캡처처럼 사용자가 입력한 프롬프트 뒤에 품질 태그를 붙인다.
    final_prompt = f"{prompt_text}, {V5_26_QUALITY_SUFFIX}"
    final_uc = user_negative_prompt if user_negative_prompt else V5_26_DEFAULT_UC

    parameters = {
        "params_version": 4,
        "width": width,
        "height": height,
        "scale": 7,
        "sampler": "k_euler_ancestral",
        "steps": 23,
        "seed": random.randint(0, 2 ** 32 - 1),
        "n_samples": 1,
        "ucPresetId": "heavy",
        "qualityPresetId": "standard",
        "autoSmea": False,
        "dynamic_thresholding": False,
        "controlnet_strength": 1,
        "legacy": False,
        "add_original_image": True,
        "cfg_rescale": 0,
        "legacy_v3_extend": False,
        "use_coords": False,
        "legacy_uc": False,
        "normalize_reference_strength_multiple": True,
        "inpaintImg2ImgStrength": 1,
        "characterPrompts": [],
        "straight_alpha": True,
        "tag_hint_qt": 1,
        "tag_hint_uc_preset": 2,
        "v4_prompt": {
            "caption": {
                "base_caption": final_prompt,
                "char_captions": []
            },
            "use_coords": False,
            "use_order": True
        },
        "v4_negative_prompt": {
            "caption": {
                "base_caption": final_uc,
                "char_captions": []
            },
            "legacy_uc": False
        },
        "negative_prompt": final_uc
    }

    payload = {
        "input": final_prompt,
        "model": "nai-diffusion-5-full",
        "action": "generate",
        "parameters": parameters
    }
    return payload, final_prompt, generated_random_tags


@bot.command(name='생성26')
async def generate_image_26(ctx: commands.Context, *, prompt: str):
    g_allowed, g_remain, g_reset = await check_and_increment_global_limit(ctx.author.id, command_name="생성26")
    if not g_allowed:
        await ctx.send(
            f"오늘 하루 전체 명령어 사용 한도({GLOBAL_DAILY_LIMIT}회)를 다 썼다냥!\n"
            f"초기화: {g_reset.strftime('%H시 %M분')} (KST)\n"
            f"사용량은 `&한도` 명령어로 확인해달라냥!",
            reference=ctx.message, mention_author=False
        )
        return

    global user_pending_requests, processing_lock, last_generation_data, NAI_API
    print(
        f"INFO: User ({ctx.author.id}) used command '생성26' in channel {ctx.channel.id}. Prompt: '{prompt}...'"
    )

    if not NAI_API:
        await ctx.send("봇 설정 오류: NAI_API 키가 설정되지 않았다냥!", reference=ctx.message, mention_author=False)
        print(f"FAIL: '생성26' for ({ctx.author.id}) - NAI_API key not set.")
        return

    user_id = ctx.author.id
    user_channel_key = (ctx.channel.id, user_id)
    current_pending = user_pending_requests.get(user_id, 0)

    if current_pending >= MAX_PENDING_PER_USER:
        active_req = 1 if processing_lock.locked() else 0
        await ctx.send(
            f"처리 대기 중인 내 요청이 이미 {current_pending}개 있다냥! (최대 {MAX_PENDING_PER_USER}개)\n"
            f"(현재 {active_req}개 요청 처리 중) 요청이 처리된 후 다시 시도해달라냥.",
            reference=ctx.message, mention_author=False
        )
        print(f"INFO: '생성26' for ({ctx.author.id}) - Request limit reached.")
        return

    generate26_allowed, generate26_remaining, generate26_reset = await check_and_increment_generate26_limit(
        user_id
    )
    if not generate26_allowed:
        generate26_cap = get_generate26_daily_limit()
        await ctx.send(
            f"오늘 &생성26은 {generate26_cap}회까지다냥!\n"
            f"초기화: {generate26_reset.strftime('%H시 %M분')} (KST)\n"
            f"사용량은 `&한도` 명령어로 확인해달라냥!",
            reference=ctx.message, mention_author=False
        )
        return

    user_pending_requests[user_id] = current_pending + 1
    processing_status = "다른 요청 처리 중, " if processing_lock.locked() else ""
    wait_msg = await ctx.send(
        f"요청 접수! ({processing_status}내 대기열: {user_pending_requests[user_id]}/{MAX_PENDING_PER_USER})\n"
        f"다른 작업 완료 후 순차적으로 처리된다냥.",
        reference=ctx.message, mention_author=False
    )

    try:
        async with processing_lock:
            if wait_msg:
                try:
                    await wait_msg.edit(
                        content=f"내 요청 처리 시작! (내 대기열: {user_pending_requests[user_id]}/{MAX_PENDING_PER_USER})"
                    )
                except discord.HTTPException:
                    pass

            payload, final_prompt, generated_random_tags_str = _build_v5_26_payload(prompt)
            v5_width = payload["parameters"]["width"]
            v5_height = payload["parameters"]["height"]
            print(f"DEBUG: 생성26 payload size = {v5_width}x{v5_height}")

            display_prompt_content = f"2026년(v5) 생성 기능을 사용한다냥! : `{prompt}`"
            if "랜덤" in prompt and generated_random_tags_str:
                display_prompt_content += f"\n랜덤으로 추가된 프롬프트 : `{generated_random_tags_str}`"
            await ctx.send(display_prompt_content, mention_author=False)

            # 캡처한 웹 요청과 동일하게 JSON을 multipart/form-data의 request(blob) 파트로 보낸다.
            headers = {
                'Authorization': f'Bearer {NAI_API}',
                'Accept': 'application/zip'
            }
            api_url = 'https://image.novelai.net/ai/generate-image'

            try:
                async with aiohttp.ClientSession() as session:
                    form = aiohttp.FormData()
                    form.add_field(
                        'request',
                        json.dumps(payload, ensure_ascii=False),
                        filename='blob',
                        content_type='application/json'
                    )
                    async with session.post(api_url, headers=headers, data=form) as response:
                        if response.status == 200:
                            zip_binary = await response.read()
                            with zipfile.ZipFile(io.BytesIO(zip_binary)) as zip_ref:
                                names = zip_ref.namelist()
                                if not names:
                                    await ctx.send(
                                        "생성 실패: API 응답 zip 파일이 비어있다냥!",
                                        reference=ctx.message, mention_author=False
                                    )
                                    return
                                image_binary = zip_ref.read(names[0])

                            image_file = discord.File(
                                io.BytesIO(image_binary), filename=f'generate26_{ctx.message.id}.png'
                            )
                            limit_notice = None
                            if generate26_remaining == 0:
                                limit_notice = (
                                    "오늘 &생성26 한도를 모두 사용했다냥! "
                                    "사용량은 `&한도` 명령어로 확인해달라냥!"
                                )
                            await ctx.send(content=limit_notice, file=image_file, mention_author=False)
                            print(f"SUCCESS: '생성26' for ({ctx.author.id}). Image sent.")

                            last_generation_data[user_channel_key] = {
                                'command_name': '생성26',
                                'original_discord_prompt': prompt,
                                'reference_data': {'base64': [], 'info': [], 'strength': []}
                            }
                        elif response.status == 429:
                            await ctx.send(
                                "생성 실패: API 동시 생성 제한(429)!",
                                reference=ctx.message, mention_author=False
                            )
                        else:
                            error_binary = await response.read()
                            error_text = error_binary.decode('utf-8', errors='ignore')
                            await ctx.send(
                                f'API 호출 실패! 상태코드: {response.status}\n```json\n{error_text[:500]}\n```',
                                reference=ctx.message, mention_author=False
                            )
                            print(
                                f"FAIL: '생성26' for ({ctx.author.id}) - API Error {response.status}: {error_text[:200]}"
                            )
            except aiohttp.ClientError as e:
                await ctx.send(
                    f"생성 실패: API 서버 연결 실패냥!: {e}",
                    reference=ctx.message, mention_author=False
                )
                traceback.print_exc()
            except Exception as e:
                await ctx.send(f'생성26 중 알 수 없는 오류 발생냥!: {e}', reference=ctx.message, mention_author=False)
                traceback.print_exc()
    finally:
        user_pending_requests[user_id] = user_pending_requests.get(user_id, 1) - 1
        if user_pending_requests[user_id] <= 0:
            user_pending_requests.pop(user_id, None)
        if wait_msg:
            try:
                await wait_msg.delete()
            except discord.HTTPException:
                pass


@bot.command(name='생성23')
async def generate_image_23(ctx: commands.Context, *, prompt: str):
    g_allowed, g_remain, g_reset = await check_and_increment_global_limit(ctx.author.id, command_name="생성23")
    if not g_allowed:
        await ctx.send(
            f"오늘 하루 전체 명령어 사용 한도({GLOBAL_DAILY_LIMIT}회)를 다 썼다냥!\n"
            f"초기화: {g_reset.strftime('%H시 %M분')} (KST)",
            reference=ctx.message, mention_author=False
        )
        return
    global user_pending_requests, last_generation_data, processing_lock, NAI_API
    # 명령어 사용 로그
    print(
        f"INFO: User ({ctx.author.id}) used command '생성23' in channel {ctx.channel.id}. Prompt: '{prompt}...'")

    if not NAI_API:  # NAI_API 키 확인
        await ctx.send("봇 설정 오류: NAI_API 키가 설정되지 않았다냥!", reference=ctx.message, mention_author=False)
        print(f"FAIL: '생성23' for ({ctx.author.id}) - NAI_API key not set.")
        return

    user_id = ctx.author.id
    user_channel_key = (ctx.channel.id, user_id)  # 사용자-채널별 마지막 생성 데이터 키
    current_pending = user_pending_requests.get(user_id, 0)

    if current_pending >= MAX_PENDING_PER_USER:  # 사용자별 동시 요청 제한
        active_req = 1 if processing_lock.locked() else 0
        await ctx.send(
            f"처리 대기 중인 내 요청이 이미 {current_pending}개 있다냥! (최대 {MAX_PENDING_PER_USER}개)\n"
            f"(현재 {active_req}개 요청 처리 중) 요청이 처리된 후 다시 시도해달라냥.",
            reference=ctx.message, mention_author=False)
        print(f"INFO: '생성23' for ({ctx.author.id}) - Request limit reached.")
        return

    user_pending_requests[user_id] = current_pending + 1
    processing_status = "다른 요청 처리 중, " if processing_lock.locked() else ""
    wait_msg = await ctx.send(
        f"요청 접수! ({processing_status}내 대기열: {user_pending_requests[user_id]}/{MAX_PENDING_PER_USER})\n"
        f"다른 작업 완료 후 순차적으로 처리된다냥.",
        reference=ctx.message, mention_author=False
    )
    temp_messages_to_delete: list[discord.Message] = [wait_msg] if wait_msg else []

    try:
        async with processing_lock:  # 한 번에 하나의 API 호출만 허용
            if wait_msg:
                try:
                    await wait_msg.edit(
                        content=f"내 요청 처리 시작! (내 대기열: {user_pending_requests[user_id]}/{MAX_PENDING_PER_USER})")
                except discord.HTTPException:
                    pass  # 메시지 수정 실패는 무시

            # 프롬프트 처리 및 페이로드 구성
            model_id_from_helper, api_prompt_for_payload, payload_structure, generated_random_tags_str = \
                await _process_prompt_and_get_payload_parts(ctx, ctx.command.name, prompt, temp_messages_to_delete)

            # print(f"--- DEBUG INFO from generate_image_23 ---") # 제거
            # print(f"Helper returned model_id: {model_id_from_helper}") # 제거
            # print(f"Helper returned api_prompt_for_payload: '{api_prompt_for_payload}'") # 제거
            # print(f"Helper returned generated_random_tags_str: '{generated_random_tags_str}'") # 제거
            if payload_structure is None:
                # print(f"CRITICAL DEBUG: payload_structure IS None!") # 제거
                await ctx.send("이미지 생성 설정에 실패했다냥! (내부 오류)", reference=ctx.message, mention_author=False)
                print(f"FAIL: '생성23' for ({ctx.author.id}) - Payload structure is None.")
                return
            # else: print(f"DEBUG: payload_structure IS NOT None.") # 제거

            # 사용자에게 보여줄 최종 프롬프트 (원본 프롬프트 + 랜덤 태그)
            display_prompt_content = f"2023년(v3) 생성 기능을 사용한다냥! : `{prompt}`"
            if "랜덤" in prompt and generated_random_tags_str:
                display_prompt_content += f"\n랜덤으로 추가된 프롬프트 : `{generated_random_tags_str}`"
            await ctx.send(display_prompt_content, mention_author=False)  # 이 메시지는 삭제하지 않음

            # 레퍼런스 이미지 처리
            FIRST_IMAGE_STRENGTH, FIRST_IMAGE_INFO = 0.9, 0.6
            SUBSEQUENT_IMAGE_STRENGTH, SUBSEQUENT_IMAGE_INFO = 0.4, 0.9
            reference_images_base64, reference_info, reference_strengths = [], [], []
            valid_image_count = 0
            attachments = ctx.message.attachments

            processing_attachments_msg = None
            if attachments:  # 첨부파일이 있는 경우에만 메시지 전송
                try:
                    processing_attachments_msg = await ctx.send("첨부 파일 처리 중...", reference=ctx.message,
                                                                mention_author=False)
                    temp_messages_to_delete.append(processing_attachments_msg)
                except discord.HTTPException:
                    pass

            for attachment in attachments:
                if attachment.content_type and attachment.content_type.startswith('image/'):
                    try:
                        image_bytes = await attachment.read()
                        if valid_image_count == 0:
                            save_shared_reference(user_id, "character", image_bytes)
                            save_shared_reference(user_id, "style", b"")
                        elif valid_image_count == 1:
                            save_shared_reference(user_id, "style", image_bytes)
                        base64_encoded = base64.b64encode(image_bytes).decode('utf-8')
                        reference_images_base64.append(base64_encoded)
                        if valid_image_count == 0:
                            reference_strengths.append(FIRST_IMAGE_STRENGTH);
                            reference_info.append(FIRST_IMAGE_INFO)
                        else:
                            reference_strengths.append(SUBSEQUENT_IMAGE_STRENGTH);
                            reference_info.append(SUBSEQUENT_IMAGE_INFO)
                        valid_image_count += 1
                    except Exception as e:
                        await ctx.send(f"첨부 파일 '{attachment.filename}' 처리 중 오류 발생냥!: {e}", reference=ctx.message,
                                       mention_author=False)
                        print(
                            f"FAIL: '생성' (attachment processing) for ({ctx.author.id}). File: {attachment.filename}, Reason: {e}")
                        return  # 오류 발생 시 함수 종료

            # 최종 페이로드에 레퍼런스 이미지 정보 추가
            payload = payload_structure
            if reference_images_base64:
                payload['parameters']['reference_image_multiple'] = reference_images_base64
                payload['parameters']['reference_information_extracted_multiple'] = reference_info
                payload['parameters']['reference_strength_multiple'] = reference_strengths
                payload['parameters']['add_original_image'] = False  # 레퍼런스 사용 시 원본 이미지 추가 안 함

            headers = {'Authorization': f'Bearer {NAI_API}', 'Content-Type': 'application/json',
                       'Accept': 'application/zip'}
            api_url = 'https://image.novelai.net/ai/generate-image'

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(api_url, headers=headers, json=payload) as response:
                        if response.status == 200:
                            zip_binary = await response.read()
                            with zipfile.ZipFile(io.BytesIO(zip_binary)) as zip_ref:
                                image_name = zip_ref.namelist()[0] if zip_ref.namelist() else None
                                if not image_name:
                                    await ctx.send("생성 실패: API 응답 zip 파일이 비어있다냥!", reference=ctx.message,
                                                   mention_author=False)
                                    print(f"FAIL: '생성23' for ({ctx.author.id}) - Empty zip from API.")
                                    return
                                image_binary = zip_ref.read(image_name)

                            filename = f'generate_{ctx.message.id}.png'  # 파일명에 명령어 타입 명시
                            image_file = discord.File(io.BytesIO(image_binary), filename=filename)

                            send_content_for_image = ""
                            if reference_images_base64:
                                send_content_for_image = f"(레퍼런스 {valid_image_count}개 사용, 순서별 설정 적용됨)"

                            await ctx.send(content=send_content_for_image if send_content_for_image else None,
                                           file=image_file, mention_author=False)
                            print(f"SUCCESS: '생성23' for ({ctx.author.id}). Image sent.")

                            # 마지막 생성 데이터 저장 (재생성용)
                            last_generation_data[user_channel_key] = {
                                'command_name': ctx.command.name,
                                'original_discord_prompt': prompt,  # API에 실제로 보낸 프롬프트 저장
                                'reference_data': {
                                    'base64': reference_images_base64,  # 사용된 레퍼런스 정보 저장
                                    'info': reference_info,
                                    'strength': reference_strengths
                                }
                            }
                        elif response.status == 429:  # API 동시 생성 제한
                            await ctx.send(f"생성 실패: API 동시 생성 제한(429)이 해제되지 않았다냥! 잠시 후 다시 시도해달라냥.",
                                           reference=ctx.message, mention_author=False)
                            print(f"FAIL: '생성23' for ({ctx.author.id}) - API Rate limit (429).")
                        else:  # 기타 API 오류
                            error_binary = await response.read();
                            error_text = error_binary.decode('utf-8', errors='ignore')
                            await ctx.send(f'생성 실패! 상태코드: {response.status}\n```json\n{error_text[:500]}\n```',
                                           reference=ctx.message, mention_author=False)
                            print(
                                f"FAIL: '생성23' for ({ctx.author.id}) - API Error {response.status}: {error_text[:200]}")
            except aiohttp.ClientError as e:  # API 서버 연결 실패
                await ctx.send(f"생성 실패: API 서버 연결 실패냥!: {e}", reference=ctx.message, mention_author=False)
                print(f"FAIL: '생성23' for ({ctx.author.id}) - aiohttp.ClientError: {e}")
                traceback.print_exc()
            except Exception as e:  # 그 외 예외
                await ctx.send(f'생성 중 알 수 없는 오류 발생냥!: {e}', reference=ctx.message, mention_author=False)
                print(f"FAIL: '생성23' for ({ctx.author.id}) - Unknown error: {e}")
                traceback.print_exc()
    finally:  # 사용자 요청 카운트 감소 및 임시 메시지 삭제
        user_pending_requests[user_id] = user_pending_requests.get(user_id, 1) - 1
        if user_pending_requests[user_id] <= 0:
            user_pending_requests.pop(user_id, None)
        for msg_to_delete in temp_messages_to_delete:
            try:
                if msg_to_delete: await msg_to_delete.delete()
            except discord.HTTPException:
                pass  # 삭제 실패는 무시


@bot.command(name='재생성')
async def regenerate_image(ctx: commands.Context):
    global user_pending_requests, last_generation_data, processing_lock, NAI_API, MAX_PENDING_PER_USER
    # 복제26는 저장된 참조 이미지로 전용 경로를 재사용한다. 한도는 그 경로에서 한 번만 계산한다.
    previous = dict(last_generation_data.get((ctx.channel.id, ctx.author.id)) or {})
    if previous.get("command_name") == "복제26":
        await _generate_clone26(
            ctx,
            prompt=previous.get("original_discord_prompt", "masterpiece"),
            regeneration_reference=dict(previous.get("reference_data") or {}),
        )
        return

    # 1. 원래 명령어로 분류하여 글로벌 한도와 디버그 통계를 한 번 기록한다.
    g_allowed, g_remain, g_reset = await check_and_increment_global_limit(
        ctx.author.id, command_name=previous.get("command_name", "")
    )
    if not g_allowed:
        await ctx.send(
            f"오늘 한도 끝났다냥! (초기화: {g_reset.strftime('%H:%M')})\n"
            f"사용량은 `&한도` 명령어로 확인해달라냥!",
            mention_author=False
        )
        return

    # 2. 저장된 데이터 확인 (여기가 핵심이다냥)
    user_channel_key = (ctx.channel.id, ctx.author.id)
    if not previous:
        await ctx.send("이 채널에서 기억된 생성 정보가 없다냥! &복제25나 &생성23~26을 먼저 써달라냥.", mention_author=False)
        return

    # 한도 체크 중 다른 요청이 완료되어도 집계한 명령어와 실제 재생성 대상이 같아야 한다.
    last_data = previous
    command_name_to_regen = last_data.get('command_name')
    original_prompt = last_data.get('original_discord_prompt', "")

    # 데이터가 꼬여서 프롬프트가 없을 경우 방지
    if not command_name_to_regen:
        await ctx.send("이전 명령어 정보를 불러올 수 없다냥. 다시 생성해달라냥.", mention_author=False)
        return

    # 대기열 체크
    user_id = ctx.author.id
    current_pending = user_pending_requests.get(user_id, 0)
    if current_pending >= 3:
        await ctx.send(f"대기열이 꽉 찼다냥! ({current_pending}/3)", mention_author=False)
        return

    user_pending_requests[user_id] = current_pending + 1
    wait_msg = await ctx.send("기억된 설정으로 재생성 중이다냥...", mention_author=False)

    try:
        async with processing_lock:
            payload = None
            specific_limit_notice = None
            api_url = 'https://image.novelai.net/ai/generate-image'
            headers = {'Authorization': f'Bearer {NAI_API}', 'Content-Type': 'application/json',
                       'Accept': 'application/zip'}

            # ==========================================
            # [복제25] 재생성 로직
            # ==========================================
            if command_name_to_regen == '복제25':
                allowed, remaining, reset_at = await check_and_increment_clone_limit(user_id)
                if not allowed:
                    await wait_msg.edit(
                        content=f"오늘 복제 공통 한도를 다 썼다냥! (초기화: {reset_at.strftime('%H:%M')})\n"
                                f"사용량은 `&한도` 명령어로 확인해달라냥!"
                    )
                    return
                if remaining == 0:
                    specific_limit_notice = (
                        "오늘 복제 공통 한도를 모두 사용했다냥! "
                        "사용량은 `&한도` 명령어로 확인해달라냥!"
                    )

                refpack = last_data.get('reference_data', {})
                char_b64 = refpack.get('character_ref_b64') or refpack.get('ref_b64')
                char_cache_key = refpack.get('character_ref_cache_key') or refpack.get('ref_cache_key')
                style_b64 = refpack.get('style_ref_b64')
                style_cache_key = refpack.get('style_ref_cache_key')

                if not char_b64:
                    await wait_msg.edit(content="오류: 저장된 캐릭터 레퍼런스 이미지가 날아갔다냥! 다시 &복제25를 써달라냥.")
                    return

                if not char_cache_key:
                    try:
                        char_cache_key = hashlib.sha256(base64.b64decode(char_b64)).hexdigest()
                    except Exception:
                        char_cache_key = hashlib.sha256(char_b64.encode('utf-8')).hexdigest()

                character_ref = {
                    'b64': char_b64,
                    'cache_key': char_cache_key,
                }

                style_ref = None
                if style_b64:
                    if not style_cache_key:
                        try:
                            style_cache_key = hashlib.sha256(base64.b64decode(style_b64)).hexdigest()
                        except Exception:
                            style_cache_key = hashlib.sha256(style_b64.encode('utf-8')).hexdigest()
                    style_ref = {
                        'b64': style_b64,
                        'cache_key': style_cache_key,
                    }

                api_prompt = original_prompt
                user_negative_prompt = None
                if "&부정" in api_prompt:
                    parts = api_prompt.split("&부정", 1)
                    api_prompt = parts[0].strip()
                    user_negative_prompt = parts[1].strip()

                width, height = 1216, 832
                ignore_style = False
                if "무시" in api_prompt:
                    ignore_style = True
                    api_prompt = api_prompt.replace("무시", " ").strip()
                if "네모" in api_prompt:
                    width, height = 1024, 1024
                    api_prompt = api_prompt.replace("네모", " ").strip()
                elif "세로" in api_prompt:
                    width, height = 832, 1216
                    api_prompt = api_prompt.replace("세로", " ").strip()

                api_prompt, _random_tags = apply_random_prompt_tags(api_prompt)

                DEFAULT_CLONE_UC = "nsfw, lowres, artistic error, film grain, scan artifacts, worst quality, bad quality, jpeg artifacts, very displeasing, chromatic aberration, dithering, halftone, screentone, multiple views, logo, too many watermarks, negative space, blank page, lowres, error, artistic error, bad, bad anatomy, bad perspective, bad proportions, bad aspect ratio, bad face, bad teeth, bad neck, "
                negative_prompt_data = {
                    "caption": {"base_caption": user_negative_prompt if user_negative_prompt else DEFAULT_CLONE_UC,
                                "char_captions": []},
                    "legacy_uc": False
                }

                director_block = build_director_reference(
                    ignore_style=ignore_style,
                    character_ref=character_ref,
                    style_ref=style_ref if (style_ref and not ignore_style) else None,
                )

                parameters = {
                    "params_version": 3,
                    "width": width, "height": height, "scale": 5, "sampler": "k_euler_ancestral", "steps": 23,
                    "n_samples": 1,
                    "ucPreset": 0, "qualityToggle": True, "cfg_rescale": 0.5, "controlnet_strength": 1,
                    "add_original_image": True,
                    "noise_schedule": "karras", "prefer_brownian": True, "normalize_reference_strength_multiple": True,
                    "v4_prompt": {"caption": {"base_caption": api_prompt, "char_captions": []}, "use_coords": False,
                                  "use_order": True},
                    "v4_negative_prompt": negative_prompt_data
                }
                parameters.update(director_block)

                payload = {
                    "action": "generate", "model": "nai-diffusion-4-5-full",
                    "input": api_prompt, "parameters": parameters
                }

                ref_notice = "1장=캐릭터&스타일 / 2장=스타일 레퍼런스 유지" if (style_ref and not ignore_style) else (
                    "1장=캐릭터 레퍼런스 유지" if ignore_style else "1장=캐릭터&스타일 레퍼런스 유지")
                info_msg = f"기억된 설정으로 복제 재생성! ({ref_notice}) (`{original_prompt}`)"
                await wait_msg.edit(content=info_msg)

            # ==========================================
            # [생성26 / NovelAI v5] 재생성 로직
            # ==========================================
            elif command_name_to_regen == '생성26':
                allowed, remaining, reset_at = await check_and_increment_generate26_limit(user_id)
                if not allowed:
                    await wait_msg.edit(
                        content=f"오늘 &생성26 한도를 다 썼다냥! (초기화: {reset_at.strftime('%H:%M')})\n"
                                f"사용량은 `&한도` 명령어로 확인해달라냥!"
                    )
                    return
                if remaining == 0:
                    specific_limit_notice = (
                        "오늘 &생성26 한도를 모두 사용했다냥! "
                        "사용량은 `&한도` 명령어로 확인해달라냥!"
                    )
                payload, _, generated_random_tags_str = _build_v5_26_payload(original_prompt)
                regen_notice = f"기억된 v5 프롬프트로 재생성! (`{original_prompt}`)"
                if "랜덤" in original_prompt and generated_random_tags_str:
                    regen_notice += f"\n랜덤으로 추가된 프롬프트 : `{generated_random_tags_str}`"
                await wait_msg.edit(content=regen_notice)

            # ==========================================
            # [일반] 재생성 로직 (생성23/24/25 등)
            # ==========================================
            else:
                # 헬퍼 함수가 'original_prompt'를 인자로 받아서 처리하도록 함
                model_id, api_prompt, payload_structure, _ = await _process_prompt_and_get_payload_parts(
                    ctx, command_name_to_regen, original_prompt, []
                )

                if not payload_structure:
                    await wait_msg.edit(content="재생성 데이터 구성 실패! (내부 오류)")
                    return

                payload = payload_structure
                await wait_msg.edit(content=f"기억된 프롬프트로 재생성! (`{original_prompt}`)")

            # 공통 API 호출
            async with aiohttp.ClientSession() as session:
                if command_name_to_regen == '생성26':
                    regen_headers = {
                        'Authorization': f'Bearer {NAI_API}',
                        'Accept': 'application/zip'
                    }
                    form = aiohttp.FormData()
                    form.add_field(
                        'request',
                        json.dumps(payload, ensure_ascii=False),
                        filename='blob',
                        content_type='application/json'
                    )
                    request_ctx = session.post(api_url, headers=regen_headers, data=form)
                else:
                    request_ctx = session.post(api_url, headers=headers, json=payload)

                async with request_ctx as response:
                    if response.status == 200:
                        zdata = await response.read()
                        with zipfile.ZipFile(io.BytesIO(zdata)) as z:
                            if not z.namelist():
                                await wait_msg.edit(content="결과 이미지가 없다냥!")
                                return
                            img_data = z.read(z.namelist()[0])

                        file = discord.File(io.BytesIO(img_data), filename=f"regen_{ctx.message.id}.png")
                        await ctx.send(
                            content=specific_limit_notice,
                            file=file,
                            reference=ctx.message,
                            mention_author=False
                        )
                        try:
                            await wait_msg.delete()
                        except:
                            pass
                    else:
                        err = await response.text()
                        await wait_msg.edit(content=f"오류 발생! {response.status}\n```\n{err[:500]}\n```")

    except Exception as e:
        traceback.print_exc()
        try:
            await wait_msg.edit(content=f"에러다냥: {e}")
        except:
            pass
    finally:
        user_pending_requests[user_id] = max(0, user_pending_requests.get(user_id, 1) - 1)
        if user_pending_requests[user_id] == 0:
            user_pending_requests.pop(user_id, None)


@bot.command(name='복제인페인트', aliases=['복제채우기', '클론인페인트'])
async def clone_inpaint_image(ctx: commands.Context, *, prompt: str):
    # 1) 글로벌 한도 체크
    g_allowed, g_remain, g_reset = await check_and_increment_global_limit(ctx.author.id)
    if not g_allowed:
        await ctx.send(
            f"오늘 하루 전체 명령어 사용 한도({GLOBAL_DAILY_LIMIT}회)를 다 썼다냥!\n"
            f"초기화: {g_reset.strftime('%H시 %M분')} (KST)\n"
            f"사용량은 `&한도` 명령어로 확인해달라냥!",
            reference=ctx.message, mention_author=False
        )
        return

    # 2) 복제 한도 체크 (복제 기능 사용)
    c_allowed, c_remain, c_reset = await check_and_increment_clone_limit(ctx.author.id)
    clone_cap = await get_clone_daily_cap(ctx.author.id)
    if not c_allowed:
        await ctx.send(
            f"오늘 복제 공통 한도({clone_cap}회)를 다 썼다냥! 복제인페인트도 복제 횟수를 소모한다냥.\n"
            f"사용량은 `&한도` 명령어로 확인해달라냥!",
            reference=ctx.message, mention_author=False
        )
        return

    from PIL import Image, ImageFilter, UnidentifiedImageError
    import io, base64, zipfile, random, traceback, aiohttp, math, hashlib, discord

    command_name = ctx.command.name
    print(f"INFO: User ({ctx.author.id}) used command '{command_name}'. Prompt: '{prompt[:80]}...'")

    global user_pending_requests, processing_lock, NAI_API, MAX_PENDING_PER_USER, last_generation_data

    if not NAI_API:
        await ctx.send("봇 설정 오류: NAI_API 키가 없다냥!", reference=ctx.message, mention_author=False)
        return

    # --------------------------
    # Helper
    # --------------------------
    def _b64_png(pil_img: Image.Image) -> str:
        buf = io.BytesIO()
        pil_img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("utf-8")

    def _has_transparency(img: Image.Image) -> bool:
        if img.mode == "P":
            transparent = img.info.get("transparency", -1)
            colors = img.getcolors()
            if colors:
                for _, index in colors:
                    if index == transparent:
                        return True
        elif img.mode in ("RGBA", "LA"):
            extrema = img.getchannel("A").getextrema()
            return extrema[0] < 255
        return False

    def _mask_from_alpha_rgba(img_rgba: Image.Image) -> Image.Image:
        alpha = img_rgba.getchannel("A")
        return alpha.point(lambda a: 255 if a < 255 else 0)

    def _snap_and_pad_mask(mask_l: Image.Image, pad_px: int, tile: int = 8) -> Image.Image:
        w, h = mask_l.size
        mw, mh = w // tile, h // tile
        if mw <= 0 or mh <= 0:
            return mask_l.point(lambda x: 255 if x > 0 else 0)

        m = mask_l.point(lambda x: 255 if x > 0 else 0)
        m_small = m.resize((mw, mh), resample=Image.NEAREST)
        m_small = m_small.point(lambda x: 255 if x > 0 else 0)

        pad_blocks = max(0, math.ceil(pad_px / tile))
        if pad_blocks > 0:
            k = 2 * pad_blocks + 1
            m_small = m_small.filter(ImageFilter.MaxFilter(k))
            m_small = m_small.point(lambda x: 255 if x > 0 else 0)

        m_big = m_small.resize((w, h), resample=Image.NEAREST)
        return m_big.point(lambda x: 255 if x > 0 else 0)

    def _prepare_ref_like_clone(char_img_bytes: bytes):
        """
        &복제25와 동일한 레퍼런스 규격:
        - 비율 유지 리사이즈 후 고정 캔버스(1536x1024 / 1024x1536 / 1472x1472)에 레터박스
        - JPEG 저장 (quality=92, subsampling=0)
        - sha256(cache_key) 는 JPEG bytes로 생성
        """
        MAX_REF_SIDE = 4000

        with Image.open(io.BytesIO(char_img_bytes)) as im:
            im = im.convert("RGB")
            w, h = im.size
            if w > MAX_REF_SIDE or h > MAX_REF_SIDE:
                raise ValueError("⚠️ 4000x4000 이상 이미지는 레퍼런스로 사용할 수 없다냥!")

            if w > h:
                target_w, target_h = 1536, 1024
            elif h > w:
                target_w, target_h = 1024, 1536
            else:
                target_w, target_h = 1472, 1472

            scale = min(target_w / w, target_h / h)
            new_w = max(1, int(w * scale))
            new_h = max(1, int(h * scale))

            im_resized = im.resize((new_w, new_h), Image.LANCZOS)
            canvas = Image.new("RGB", (target_w, target_h), (255, 255, 255))
            offset = ((target_w - new_w) // 2, (target_h - new_h) // 2)
            canvas.paste(im_resized, offset)

            buf = io.BytesIO()
            canvas.save(buf, format="JPEG", quality=92, optimize=True, progressive=True, subsampling=0)
            jpeg_bytes = buf.getvalue()

        ref_b64 = base64.b64encode(jpeg_bytes).decode("ascii")
        ref_cache_key = hashlib.sha256(jpeg_bytes).hexdigest()
        return ref_cache_key, ref_b64

    async def _post_nai(session: aiohttp.ClientSession, payload: dict):
        async with session.post(API_URL, headers=headers, json=payload) as resp:
            if resp.status == 200:
                return 200, await resp.read()
            else:
                try:
                    return resp.status, await resp.text()
                except:
                    return resp.status, "Failed to read error body."

    # --------------------------
    # Settings
    # --------------------------
    user_id = ctx.author.id
    user_channel_key = (ctx.channel.id, user_id)

    MODEL_INPAINT = "nai-diffusion-4-5-full-inpainting"
    API_URL = "https://image.novelai.net/ai/generate-image"
    headers = {
        "Authorization": f"Bearer {NAI_API}",
        "Content-Type": "application/json",
        "Accept": "application/zip",
    }

    ALLOWED_SIZES = {(1216, 832), (832, 1216), (1024, 1024)}
    PAD_PX = 8
    HOLE_BLUR = 16

    # --------------------------
    # Queue check
    # --------------------------
    current_pending = user_pending_requests.get(user_id, 0)
    if current_pending >= MAX_PENDING_PER_USER:
        await ctx.send(f"대기열이 꽉 찼다냥! ({current_pending}개)", reference=ctx.message, mention_author=False)
        return

    user_pending_requests[user_id] = current_pending + 1
    processing_status = "다른 작업 중, " if processing_lock.locked() else ""
    wait_msg = await ctx.send(
        f"🧬 복제+인페인트 요청 접수! (`{prompt}`) ({processing_status}대기열: {user_pending_requests[user_id]})",
        reference=ctx.message, mention_author=False
    )

    processing_msg = None

    try:
        async with processing_lock:
            # --------------------------
            # 0) 레퍼런스 준비
            #    - 첨부 2장이면: (불투명=ref, 투명=인페인트)
            #    - 첨부 1장/0장이면: 최근 &복제25 저장 레퍼런스 사용
            # --------------------------
            ref_cache_key = None
            ref_b64 = None

            last_data = last_generation_data.get(user_channel_key) or {}
            refpack = (last_data.get("reference_data") or {})
            shared_char = load_shared_reference(user_id, "character")
            if shared_char:
                shared_ref = process_reference_image_bytes(shared_char)
                refpack = dict(refpack, ref_b64=shared_ref["b64"], ref_cache_key=shared_ref["cache_key"])

            # --------------------------
            # 1) 인페인트 PNG 확보
            # --------------------------
            png_bytes = None
            char_bytes = None

            # 첨부 케이스 처리
            atts = list(ctx.message.attachments or [])
            if len(atts) > 2:
                await wait_msg.delete()
                await ctx.send("이미지는 최대 2장까지만 보내달라냥! (레퍼런스 1장 + 투명 PNG 1장)", reference=ctx.message,
                               mention_author=False)
                return

            if len(atts) == 2:
                # 2장: 투명/불투명 자동 분류
                raw1 = await atts[0].read()
                raw2 = await atts[1].read()

                try:
                    img1 = Image.open(io.BytesIO(raw1)).convert("RGBA")
                    img2 = Image.open(io.BytesIO(raw2)).convert("RGBA")
                except UnidentifiedImageError:
                    await wait_msg.delete()
                    await ctx.send("이미지 포맷을 읽을 수 없다냥! 다른 파일로 시도해달라냥!", reference=ctx.message, mention_author=False)
                    return

                t1 = _has_transparency(img1)
                t2 = _has_transparency(img2)

                if t1 and not t2:
                    png_bytes = raw1
                    char_bytes = raw2
                elif (not t1) and t2:
                    png_bytes = raw2
                    char_bytes = raw1
                else:
                    await wait_msg.delete()
                    await ctx.send(
                        "⚠️ 2장 보낼 때는 **한 장은 불투명(레퍼런스)**, **한 장은 투명 PNG(인페인트)** 여야 한다냥!",
                        reference=ctx.message, mention_author=False
                    )
                    return

                # 레퍼런스는 &복제25와 같은 규격으로 전처리해서 ref_b64/cache_key 생성
                try:
                    ref_cache_key, ref_b64 = _prepare_ref_like_clone(char_bytes)
                    save_shared_reference(user_id, "character", char_bytes)
                    save_shared_reference(user_id, "style", b"")
                except Exception as e:
                    await wait_msg.delete()
                    await ctx.send(f"레퍼런스 처리 실패냥: {e}", reference=ctx.message, mention_author=False)
                    return

            elif len(atts) == 1:
                # 1장: 인페인트 PNG로 간주
                if not atts[0].filename.lower().endswith(".png"):
                    await wait_msg.delete()
                    await ctx.send("인페인트는 **투명 배경 PNG**로 보내달라냥!", reference=ctx.message, mention_author=False)
                    return
                png_bytes = await atts[0].read()

                # 레퍼런스는 최근 저장된 것 사용
                ref_cache_key = refpack.get("ref_cache_key")
                ref_b64 = refpack.get("ref_b64")

            else:
                # 첨부 0장: 최근 인페인트 PNG 재사용(있으면) + 레퍼런스도 저장된 것
                ref_cache_key = refpack.get("ref_cache_key")
                ref_b64 = refpack.get("ref_b64")

                png_bytes = load_shared_reference(user_id, "inpaint")
                png_b64 = refpack.get("inpaint_png_b64")
                if not png_bytes and png_b64:
                    try:
                        png_bytes = base64.b64decode(png_b64)
                    except Exception:
                        png_bytes = None

            # 레퍼런스가 없으면 중단 (cached만 있으면 400 날 확률 큼)
            if not ref_cache_key or not ref_b64:
                await wait_msg.delete()
                await ctx.send(
                    "⚠️ 레퍼런스가 없다냥!\n"
                    "1) `&복제25`로 캐릭터 등록 후 다시 쓰거나\n"
                    "2) `&복제인페인트`에 **레퍼런스 1장(불투명) + 인페인트 PNG 1장(투명)** 같이 보내달라냥!",
                    reference=ctx.message, mention_author=False
                )
                return

            if png_bytes:
                save_shared_reference(user_id, "inpaint", png_bytes)
            if not png_bytes:
                await wait_msg.delete()
                await ctx.send(
                    "인페인트할 **투명 PNG**를 첨부해달라냥! (또는 직전에 쓴 PNG가 있어야 재사용 가능하다냥)",
                    reference=ctx.message, mention_author=False
                )
                return

            # 진행 메시지
            try:
                await wait_msg.edit(content=f"복제인페인트 처리 시작! (`{prompt}`)")
            except:
                pass

            processing_msg = await ctx.send("이미지 처리 중...", reference=ctx.message, mention_author=False)

            # --------------------------
            # 2) 인페인트 전처리 (마스크 + hole fill)
            # --------------------------
            try:
                with Image.open(io.BytesIO(png_bytes)) as img:
                    if img.mode != "RGBA":
                        img = img.convert("RGBA")

                    width, height = img.size
                    if (width, height) not in ALLOWED_SIZES:
                        try:
                            await processing_msg.delete()
                        except:
                            pass
                        allowed_str = ", ".join([f"{w}x{h}" for (w, h) in sorted(ALLOWED_SIZES)])
                        await ctx.send(
                            f"지원하지 않는 해상도다냥! 아래 크기만 가능하다냥:\n`{allowed_str}`",
                            reference=ctx.message, mention_author=False
                        )
                        return

                    original_rgba = img.copy()
                    mask_core = _mask_from_alpha_rgba(original_rgba)

                    if mask_core.getbbox() is None:
                        try:
                            await processing_msg.delete()
                        except:
                            pass
                        await ctx.send(
                            "투명한 영역이 없는 것 같다냥! 구멍 뚫린 PNG가 필요하다냥.",
                            reference=ctx.message, mention_author=False
                        )
                        return

                    mask_send = _snap_and_pad_mask(mask_core, pad_px=PAD_PX, tile=8)

                    original_rgb = original_rgba.convert("RGB")
                    blurred_rgb = original_rgb.filter(ImageFilter.GaussianBlur(HOLE_BLUR))
                    base_rgb = Image.composite(blurred_rgb, original_rgb, mask_send)

                    base64_image = _b64_png(base_rgb)
                    base64_mask = _b64_png(mask_send)

            except Exception as e:
                try:
                    await processing_msg.delete()
                except:
                    pass
                await ctx.send(f"이미지 전처리 실패냥: {e}", reference=ctx.message, mention_author=False)
                traceback.print_exc()
                return

            try:
                await processing_msg.delete()
            except:
                pass

            # --------------------------
            # 3) 프롬프트/네거티브
            # --------------------------
            api_prompt = (prompt or "").strip()
            user_negative_prompt = None
            if "&부정" in api_prompt:
                parts = api_prompt.split("&부정", 1)
                api_prompt = parts[0].strip()
                user_negative_prompt = parts[1].strip()

            api_prompt, _random_tags = apply_random_prompt_tags(api_prompt)
            base_caption_suffix = ",amazing quality, very aesthetic, absurdres, masterpiece, highres, hyper detailed"
            final_prompt = (api_prompt if api_prompt else "masterpiece") + base_caption_suffix

            default_uc = (
                "nsfw, lowres, artistic error, film grain, scan artifacts, worst quality, bad quality, jpeg artifacts, "
                "very displeasing, chromatic aberration, dithering, halftone, screentone, multiple views, logo, too many "
                "watermarks, negative space, blank page, lowres, error, artistic error, bad, bad anatomy, bad perspective, "
                "bad proportions, bad aspect ratio, bad face, bad teeth, bad neck, "
            )
            final_uc = user_negative_prompt if user_negative_prompt else default_uc

            seed = random.randint(0, 2 ** 32 - 1)

            # --------------------------
            # 4) Payload (1차: cached+data)
            #     - 여기서 "cache_secret_key만" 보내면 director refs 400 터질 수 있어서 절대 금지
            #     - 안전장치로 400 나오면 raw director_reference_images로 1회 재시도
            # --------------------------
            director_block_cached = {
                "director_reference_descriptions": [
                    {"caption": {"base_caption": "character", "char_captions": []}, "legacy_uc": False}
                ],
                "director_reference_images_cached": [
                    {"cache_secret_key": ref_cache_key, "data": ref_b64}
                ],
                "director_reference_strength_values": [1.2],
                "director_reference_secondary_strength_values": [0],
                "director_reference_information_extracted": [1],
                "normalize_reference_strength_multiple": True,
            }

            director_block_raw = {
                "director_reference_descriptions": [
                    {"caption": {"base_caption": "character", "char_captions": []}, "legacy_uc": False}
                ],
                "director_reference_images": [ref_b64],
                "director_reference_strength_values": [1.2],
                "director_reference_secondary_strength_values": [0],
                "director_reference_information_extracted": [1],
                "normalize_reference_strength_multiple": True,
            }

            base_params = {
                "width": width,
                "height": height,
                "params_version": 3,
                "scale": 5,
                "sampler": "k_euler_ancestral",
                "steps": 23,
                "seed": seed,
                "extra_noise_seed": seed,
                "n_samples": 1,
                "noise_schedule": "karras",
                "cfg_rescale": 0.5,
                "qualityToggle": True,
                "ucPreset": 0,

                "image": base64_image,
                "mask": base64_mask,
                "inpaintImg2ImgStrength": 1.0,
                "img2img": {"strength": 1.0, "color_correct": True},
                "add_original_image": False,

                "v4_prompt": {
                    "caption": {"base_caption": final_prompt, "char_captions": []},
                    "use_coords": False,
                    "use_order": True,
                },
                "v4_negative_prompt": {
                    "caption": {"base_caption": final_uc, "char_captions": []},
                    "legacy_uc": False,
                },
            }

            payload_1 = {"action": "infill", "model": MODEL_INPAINT, "parameters": dict(base_params)}
            payload_1["parameters"].update(director_block_cached)

            payload_2 = {"action": "infill", "model": MODEL_INPAINT, "parameters": dict(base_params)}
            payload_2["parameters"].update(director_block_raw)

            # --------------------------
            # 5) API Call (with retry)
            # --------------------------
            timeout = aiohttp.ClientTimeout(total=300)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                status, body = await _post_nai(session, payload_1)

                # director reference 인코딩 실패(400)면 raw 방식으로 1번 더
                if status == 400 and isinstance(body, str) and (
                        "director" in body.lower() or "reference" in body.lower()):
                    status, body = await _post_nai(session, payload_2)

            # wait_msg 정리
            if wait_msg:
                try:
                    await wait_msg.delete()
                    wait_msg = None
                except:
                    pass

            if status != 200:
                err_text = body if isinstance(body, str) else str(body)
                await ctx.send(
                    f"실패했다냥! 상태코드: {status}\n```json\n{err_text[:1200]}\n```",
                    reference=ctx.message, mention_author=False
                )
                return

            zip_binary = body

            # --------------------------
            # 6) 결과 압축 해제 + 전송
            # --------------------------
            with zipfile.ZipFile(io.BytesIO(zip_binary)) as zip_ref:
                names = [n for n in zip_ref.namelist() if n.lower().endswith(".png")]
                if not names:
                    await ctx.send("결과 이미지가 없다냥!", reference=ctx.message, mention_author=False)
                    return

                best_name, best_data, best_size = None, None, -1
                for n in names:
                    data = zip_ref.read(n)
                    if len(data) > best_size:
                        best_size = len(data)
                        best_name = n
                        best_data = data

            final_buffer = io.BytesIO(best_data)
            filename = f"nai_clone_inpaint_{ctx.message.id}.png"

            await ctx.send(
                content=(
                    f"🧬 복제 인페인트 완료! (`{prompt}`)"
                    + (
                        "\n오늘 복제 공통 한도를 모두 사용했다냥! "
                        "사용량은 `&한도` 명령어로 확인해달라냥!"
                        if c_remain == 0 else ""
                    )
                ),
                file=discord.File(final_buffer, filename=filename),
                reference=ctx.message,
                mention_author=False
            )

            # --------------------------
            # 7) 데이터 갱신 (중요: ref_b64도 저장)
            # --------------------------
            last_generation_data[user_channel_key] = {
                "command_name": "복제인페인트",
                "original_discord_prompt": prompt,
                "reference_data": {
                    "ref_cache_key": ref_cache_key,
                    "ref_b64": ref_b64,  # ✅ 다음에 cached-only로 400 나는 걸 방지
                    "inpaint_png_b64": base64.b64encode(png_bytes).decode("utf-8"),
                }
            }

    except Exception as e:
        if wait_msg:
            try:
                await wait_msg.delete()
            except:
                pass
        await ctx.send(f"알 수 없는 오류냥: {e}", reference=ctx.message, mention_author=False)
        traceback.print_exc()

    finally:
        if user_id in user_pending_requests:
            user_pending_requests[user_id] -= 1
            if user_pending_requests[user_id] <= 0:
                user_pending_requests.pop(user_id, None)


@bot.command(name='생성25')
async def generate_image_25(ctx, *, prompt: str):
    g_allowed, g_remain, g_reset = await check_and_increment_global_limit(ctx.author.id, command_name="생성25")
    if not g_allowed:
        await ctx.send(
            f"오늘 하루 전체 명령어 사용 한도({GLOBAL_DAILY_LIMIT}회)를 다 썼다냥!\n"
            f"초기화: {g_reset.strftime('%H시 %M분')} (KST)",
            reference=ctx.message, mention_author=False
        )
        return
    global user_pending_requests, processing_lock, last_generation_data, NAI_API
    print(
        f"INFO: User ({ctx.author.id}) used command '생성25' in channel {ctx.channel.id}. Prompt: '{prompt}...'")

    if not NAI_API:
        await ctx.send("봇 설정 오류: NAI_API 키가 설정되지 않았다냥!", reference=ctx.message, mention_author=False)
        print(f"FAIL: '생성25' for ({ctx.author.id}) - NAI_API key not set.")
        return

    user_id = ctx.author.id
    user_channel_key = (ctx.channel.id, user_id)
    current_pending = user_pending_requests.get(user_id, 0)

    if current_pending >= MAX_PENDING_PER_USER:
        active_req = 1 if processing_lock.locked() else 0
        await ctx.send(
            f"처리 대기 중인 내 요청이 이미 {current_pending}개 있다냥! (최대 {MAX_PENDING_PER_USER}개)\n"
            f"(현재 {active_req}개 요청 처리 중) 요청이 처리된 후 다시 시도해달라냥.",
            reference=ctx.message, mention_author=False)
        print(f"INFO: '생성25' for ({ctx.author.id}) - Request limit reached.")
        return

    user_pending_requests[user_id] = current_pending + 1
    processing_status = "다른 요청 처리 중, " if processing_lock.locked() else ""
    wait_msg = await ctx.send(
        f"요청 접수! ({processing_status}내 대기열: {user_pending_requests[user_id]}/{MAX_PENDING_PER_USER})\n"
        f"다른 작업 완료 후 순차적으로 처리된다냥.",
        reference=ctx.message, mention_author=False
    )
    temp_messages_to_delete: list[discord.Message] = [wait_msg] if wait_msg else []

    try:
        async with processing_lock:
            if wait_msg:
                try:
                    await wait_msg.edit(
                        content=f"내 요청 처리 시작! (내 대기열: {user_pending_requests[user_id]}/{MAX_PENDING_PER_USER})")
                except discord.HTTPException:
                    pass

            model_id_from_helper, api_prompt_for_payload, payload_structure, generated_random_tags_str = \
                await _process_prompt_and_get_payload_parts(ctx, ctx.command.name, prompt, temp_messages_to_delete)

            # print(f"--- DEBUG INFO from generate_image_25 ---") # 제거
            # print(f"Helper returned model_id: {model_id_from_helper}") # 제거
            # print(f"Helper returned api_prompt_for_payload: '{api_prompt_for_payload}'") # 제거
            # print(f"Helper returned generated_random_tags_str: '{generated_random_tags_str}'") # 제거
            if payload_structure is None:
                # print(f"CRITICAL DEBUG: payload_structure IS None!") # 제거
                await ctx.send("이미지 생성 설정에 실패했다냥! (내부 오류)", reference=ctx.message, mention_author=False)
                print(f"FAIL: '생성25' for ({ctx.author.id}) - Payload structure is None.")
                return
            # else: print(f"DEBUG: payload_structure IS NOT None.") # 제거

            display_prompt_content = f"2025년(v4.5) 생성 기능을 사용한다냥! : `{prompt}`"
            if "랜덤" in prompt and generated_random_tags_str:
                display_prompt_content += f"\n랜덤으로 추가된 프롬프트 : `{generated_random_tags_str}`"
                # ▼ [수정됨] 보낸 메시지를 변수(prompt_msg)에 담고, 삭제 리스트에 추가
                prompt_msg = await ctx.send(display_prompt_content, mention_author=False)
                temp_messages_to_delete.append(prompt_msg)

            headers = {'Authorization': f'Bearer {NAI_API}', 'Content-Type': 'application/json',
                       'Accept': 'application/zip'}
            payload = payload_structure  # 생성25, 생성24은 레퍼런스 기능 기본적으로 미지원 (현재 로직)
            api_url = 'https://image.novelai.net/ai/generate-image'

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(api_url, headers=headers, json=payload) as response:
                        if response.status == 200:
                            zip_binary = await response.read()
                            with zipfile.ZipFile(io.BytesIO(zip_binary)) as zip_ref:
                                image_name = zip_ref.namelist()[0]
                                image_binary = zip_ref.read(image_name)

                            image_file = discord.File(io.BytesIO(image_binary),
                                                      filename=f'latest_{ctx.message.id}.png')
                            await ctx.send(file=image_file, mention_author=False)
                            print(f"SUCCESS: '생성25' for ({ctx.author.id}). Image sent.")

                            last_generation_data[user_channel_key] = {
                                'command_name': ctx.command.name,
                                'original_discord_prompt': prompt,
                                'reference_data': {'base64': [], 'info': [], 'strength': []}  # 레퍼런스 없음
                            }
                        elif response.status == 429:
                            await ctx.send(f"생성 실패: API 동시 생성 제한(429)!", reference=ctx.message, mention_author=False)
                            print(f"FAIL: '생성25' for ({ctx.author.id}) - API Rate limit (429).")
                        else:
                            error_binary = await response.read();
                            error_text = error_binary.decode('utf-8', errors='ignore')
                            await ctx.send(f'API 호출 실패! 상태코드: {response.status}\n```json\n{error_text[:500]}\n```',
                                           reference=ctx.message, mention_author=False)
                            print(
                                f"FAIL: '생성25' for ({ctx.author.id}) - API Error {response.status}: {error_text[:200]}")
            except aiohttp.ClientError as e:
                await ctx.send(f"생성 실패: API 서버 연결 실패냥!: {e}", reference=ctx.message, mention_author=False)
                print(f"FAIL: '생성25' for ({ctx.author.id}) - aiohttp.ClientError: {e}")
                traceback.print_exc()
            except Exception as e:
                await ctx.send(f'오류 발생: {e}', reference=ctx.message, mention_author=False)
                print(f"FAIL: '생성25' for ({ctx.author.id}) - Unknown error: {e}")
                traceback.print_exc()
    finally:
        user_pending_requests[user_id] = user_pending_requests.get(user_id, 1) - 1
        if user_pending_requests[user_id] <= 0:
            user_pending_requests.pop(user_id, None)
        for msg_to_delete in temp_messages_to_delete:
            try:
                if msg_to_delete: await msg_to_delete.delete()
            except discord.HTTPException:
                pass


# 필요한 모듈들 (프로젝트 전역 어딘가에 이미 있으면 중복 import 무시됨)
import aiohttp, base64, io, zipfile, random, re, traceback
import discord
from discord.ext import commands

import aiohttp, base64, io, zipfile, random, re, traceback
from PIL import Image
import discord
from discord.ext import commands

MAX_SIDE = 1280  # 참조 이미지 긴 변 제한 (디코더 안정화용)


def _sanitize_ref_image(image_bytes: bytes) -> str:
    """이미지를 RGB PNG로 재인코딩하며 EXIF 제거, 긴 변 제한."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    w, h = img.size
    scale = min(1.0, MAX_SIDE / float(max(w, h)))
    if scale < 1.0:
        img = img.resize((int(w * scale), int(h * scale)))
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def _mk_params_base(width, height):
    return {
        "width": width,
        "height": height,
        "scale": 5,
        "sampler": "k_euler_ancestral",
        "steps": 23,
        "seed": random.randint(0, 2 ** 32 - 1),
        "n_samples": 1,
        "ucPreset": 0,
        "qualityToggle": True,
        # 간섭 가능성 있는 옵션들 최소화: noise_schedule, add_original_image, params_version 등 제외
    }


def _mk_director_fields(b64_image: str, info_val: int, with_v4: bool, prompt_text: str):
    # director 배열 4개는 길이 1, 빈 값 금지
    fields = {
        "director_reference_images": [b64_image],
        "director_reference_strength_values": [1.0],  # float
        "director_reference_information_extracted": [info_val],  # int 0/1
        "director_reference_descriptions": [{
            "caption": {"base_caption": "character", "char_captions": []},
            "legacy_uc": False
        }],
    }
    if with_v4:
        fields.update({
            "v4_prompt": {"caption": {"base_caption": prompt_text}},
            # 최소 충돌화를 위해 v4_negative_prompt는 일단 제외
        })
    return fields


async def _try_generate(session, nai_key: str, model: str, payload: dict):
    headers = {
        "Authorization": f"Bearer {nai_key}",
        "Content-Type": "application/json",
        "Accept": "application/zip",
    }
    url = "https://image.novelai.net/ai/generate-image"
    async with session.post(url, headers=headers, json=payload, timeout=300) as resp:
        ok = (resp.status == 200)
        text = None
        data = None
        if ok:
            data = await resp.read()
        else:
            try:
                text = await resp.text()
            except Exception:
                text = f"(status {resp.status}, body read failed)"
        return ok, resp.status, data, text


# --- clone_character 함수와 함께 사용할 헬퍼 함수들 ---

def _sanitize_ref_image(raw_bytes: bytes) -> str:
    """PNG로 재인코딩하고, 크기를 제한하며, EXIF 데이터를 제거합니다."""
    MAX_DIM = 2048
    with Image.open(io.BytesIO(raw_bytes)) as img:
        if img.format == 'PNG' and max(img.width, img.height) <= MAX_DIM:
            # 이미 조건에 맞으면 그대로 사용
            return base64.b64encode(raw_bytes).decode('utf-8')

        if max(img.width, img.height) > MAX_DIM:
            ratio = MAX_DIM / max(img.width, img.height)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            img = img.resize(new_size, Image.LANCZOS)

        # RGBA가 아니면 변환 (투명도 유지)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode('utf-8')


# --- 최종 clone_character 명령어 ---

def _sanitize_ref_image(raw_bytes: bytes) -> str:
    """이미지를 안전한 PNG로 변환하고 크기를 제한합니다."""
    MAX_DIM = 2048
    try:
        with Image.open(io.BytesIO(raw_bytes)) as img:
            if max(img.width, img.height) > MAX_DIM:
                ratio = MAX_DIM / max(img.width, img.height)
                new_size = (int(img.width * ratio), int(img.height * ratio))
                img = img.resize(new_size, Image.LANCZOS)

            if img.mode != 'RGBA':
                img = img.convert('RGBA')

            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except Exception:
        # Pillow 처리 실패 시 원본 반환
        return base64.b64encode(raw_bytes).decode('utf-8')


MAX_REF_SIZE = 4000  # 최대 허용 크기


def validate_reference_image(file: discord.File) -> bool:
    try:
        with Image.open(file.fp) as img:
            width, height = img.size
            if width > MAX_REF_SIZE or height > MAX_REF_SIZE:
                return False
        return True
    except UnidentifiedImageError:
        return False


def process_reference_image_bytes(raw: bytes):
    """Precise Reference 권장 캔버스에 맞춰 레퍼런스 이미지를 정규화한다."""
    MAX_REF_SIDE = 4000

    with Image.open(io.BytesIO(raw)) as chk:
        chk = chk.convert("RGB")
        w, h = chk.size

        if w > MAX_REF_SIDE or h > MAX_REF_SIDE:
            raise ValueError("4000x4000 이상 이미지는 레퍼런스로 사용할 수 없다냥!")

        if w > h:
            target_w, target_h = 1536, 1024
        elif h > w:
            target_w, target_h = 1024, 1536
        else:
            target_w, target_h = 1472, 1472

        scale = min(target_w / w, target_h / h)
        new_w = max(1, int(w * scale))
        new_h = max(1, int(h * scale))

        im_resized = chk.resize((new_w, new_h), Image.LANCZOS)
        canvas = Image.new("RGB", (target_w, target_h), (255, 255, 255))
        offset = ((target_w - new_w) // 2, (target_h - new_h) // 2)
        canvas.paste(im_resized, offset)

        buf = io.BytesIO()
        canvas.save(buf, format="JPEG", quality=92, optimize=True, progressive=True, subsampling=0)
        jpeg_bytes = buf.getvalue()

    return {
        "b64": base64.b64encode(jpeg_bytes).decode("ascii"),
        "cache_key": hashlib.sha256(jpeg_bytes).hexdigest(),
        "size": (target_w, target_h),
    }


def build_director_reference(
        *,
        ignore_style: bool,
        character_ref: dict,
        style_ref: Optional[dict] = None,
):
    """
    - ignore_style == True  → 첫 이미지를 character 로만 사용 (두 번째 스타일 레퍼런스도 무시)
    - ignore_style == False and style_ref 없음 → 첫 이미지를 character&style 로 사용
    - ignore_style == False and style_ref 있음 → 첫 이미지는 character&style, 두 번째 이미지는 style 로 사용
    """

    if ignore_style or not style_ref:
        base_caption = "character" if ignore_style else "character&style"
        return {
            "director_reference_descriptions": [
                {
                    "caption": {
                        "base_caption": base_caption,
                        "char_captions": []
                    },
                    "legacy_uc": False
                }
            ],
            "director_reference_images_cached": [
                {
                    "cache_secret_key": character_ref["cache_key"],
                    "data": character_ref["b64"]
                }
            ],
            "director_reference_strength_values": [1.2],
            "director_reference_secondary_strength_values": [0],
            "director_reference_information_extracted": [1],
        }

    return {
        "director_reference_descriptions": [
            {
                "caption": {
                    "base_caption": "character&style",
                    "char_captions": []
                },
                "legacy_uc": False
            },
            {
                "caption": {
                    "base_caption": "style",
                    "char_captions": []
                },
                "legacy_uc": False
            }
        ],
        "director_reference_images_cached": [
            {
                "cache_secret_key": character_ref["cache_key"],
                "data": character_ref["b64"]
            },
            {
                "cache_secret_key": style_ref["cache_key"],
                "data": style_ref["b64"]
            }
        ],
        "director_reference_strength_values": [1.2, 1.0],
        "director_reference_secondary_strength_values": [0, 0],
        "director_reference_information_extracted": [1, 1],
    }


@bot.command(name='복제25')
async def clone_character(ctx: commands.Context, *, prompt: str):
    print(f"INFO: User ({ctx.author.id}) used command '복제25' in channel {ctx.channel.id}. Prompt: '{prompt[:50]}...'")
    import re, io, zipfile, base64, random, traceback, aiohttp, discord, hashlib
    from discord.ext import commands
    from PIL import Image, UnidentifiedImageError

    global user_pending_requests, processing_lock, NAI_API, MAX_PENDING_PER_USER, last_generation_data, RANDOM_TAG_CONFIG

    if not NAI_API:
        await ctx.send("봇 설정 오류: NAI_API 키가 설정되지 않았다냥!", reference=ctx.message, mention_author=False)
        return

    user_id = ctx.author.id
    pend = user_pending_requests.get(user_id, 0)
    limit = MAX_PENDING_PER_USER if 'MAX_PENDING_PER_USER' in globals() else 3
    if pend >= limit:
        await ctx.send(f"처리 대기 중인 내 요청이 이미 {pend}개 있다냥!", reference=ctx.message, mention_author=False)
        return

    g_allowed, g_remain, g_reset = await check_and_increment_global_limit(ctx.author.id, command_name="복제25")
    if not g_allowed:
        await ctx.send(
            f"오늘 하루 전체 명령어 사용 한도({GLOBAL_DAILY_LIMIT}회)를 다 썼다냥!\n"
            f"초기화: {g_reset.strftime('%H시 %M분')} (KST)\n"
            f"사용량은 `&한도` 명령어로 확인해달라냥!",
            reference=ctx.message, mention_author=False
        )
        return

    allowed, remaining, reset_at = await check_and_increment_clone_limit(user_id)
    clone_cap = await get_clone_daily_cap(user_id)
    if not allowed:
        await ctx.send(
            f"오늘 &복제25 / &복제26의 복제 공통 한도는 {clone_cap}회다냥!\n"
            f"남은 횟수: 0\n"
            f"초기화: {reset_at.strftime('%H시 %M분')} (KST)\n"
            f"사용량은 `&한도` 명령어로 확인해달라냥!",
            reference=ctx.message, mention_author=False
        )
        return

    user_pending_requests[user_id] = pend + 1
    wait_msg = await ctx.send("복제 준비 중이다냥... (레퍼런스 확인 중)", reference=ctx.message, mention_author=False)

    try:
        async with processing_lock:
            image_attachments = [
                a for a in ctx.message.attachments
                if a.content_type and a.content_type.startswith('image/')
            ]

            character_ref = None
            style_ref = None
            using_split_refs = False

            if image_attachments:
                try:
                    char_raw = await image_attachments[0].read()
                    character_ref = process_reference_image_bytes(char_raw)
                    save_shared_reference(user_id, "character", char_raw)
                    save_shared_reference(user_id, "style", b"")

                    if len(image_attachments) >= 2:
                        style_raw = await image_attachments[1].read()
                        style_ref = process_reference_image_bytes(style_raw)
                        save_shared_reference(user_id, "style", style_raw)
                        using_split_refs = True
                except UnidentifiedImageError:
                    await wait_msg.edit(content="이미지 포맷을 읽을 수 없다냥! 다른 파일로 시도해달라냥!")
                    return
                except ValueError as e:
                    await wait_msg.edit(content=f"⚠️ {e}")
                    return
                except Exception as e:
                    await wait_msg.edit(content=f"레퍼런스 처리 중 오류 발생냥!: {e}")
                    return
            else:
                user_channel_key = (ctx.channel.id, user_id)
                last_data = last_generation_data.get(user_channel_key)
                refpack = (last_data or {}).get('reference_data', {})

                char_b64 = refpack.get('character_ref_b64') or refpack.get('ref_b64')
                char_cache_key = refpack.get('character_ref_cache_key') or refpack.get('ref_cache_key')
                style_b64 = refpack.get('style_ref_b64')
                style_cache_key = refpack.get('style_ref_cache_key')

                shared_char = load_shared_reference(user_id, "character")
                shared_style = load_shared_reference(user_id, "style")
                if shared_char:
                    character_ref = process_reference_image_bytes(shared_char)
                    style_ref = process_reference_image_bytes(shared_style) if shared_style else None
                    using_split_refs = bool(style_ref)
                elif not char_b64:
                    await wait_msg.edit(content="레퍼런스 이미지를 찾을 수 없다냥! 이미지를 첨부해달라냥!")
                    return

                if not shared_char:
                    if not char_cache_key:
                        try:
                            char_cache_key = hashlib.sha256(base64.b64decode(char_b64)).hexdigest()
                        except Exception:
                            char_cache_key = hashlib.sha256(char_b64.encode('utf-8')).hexdigest()
                    character_ref = {'b64': char_b64, 'cache_key': char_cache_key}

                if style_b64 and not shared_char:
                    if not style_cache_key:
                        try:
                            style_cache_key = hashlib.sha256(base64.b64decode(style_b64)).hexdigest()
                        except Exception:
                            style_cache_key = hashlib.sha256(style_b64.encode('utf-8')).hexdigest()
                    style_ref = {
                        'b64': style_b64,
                        'cache_key': style_cache_key,
                    }
                    using_split_refs = True

            api_prompt = prompt.strip()
            user_negative_prompt = None

            parts = api_prompt.split("&부정", 1)
            if len(parts) == 2:
                api_prompt = parts[0].strip()
                user_negative_prompt = parts[1].strip()

            width, height = 1216, 832
            ignore_style = False

            if "무시" in api_prompt:
                ignore_style = True
                api_prompt = re.sub(r'\s*무시\s*', ' ', api_prompt)

            if "네모" in api_prompt:
                width, height = 1024, 1024
                api_prompt = re.sub(r'\s*네모\s*', ' ', api_prompt)
            elif "세로" in api_prompt:
                width, height = 832, 1216
                api_prompt = re.sub(r'\s*세로\s*', ' ', api_prompt)

            api_prompt, random_tags_added = apply_random_prompt_tags(api_prompt)

            api_prompt = re.sub(r"\s{2,}", " ", api_prompt).strip()

            await wait_msg.edit(content="복제 생성 중이다냥...")

            DEFAULT_NEGATIVE_PROMPT = (
                "nsfw, lowres, artistic error, film grain, scan artifacts, worst quality, bad quality, jpeg artifacts, very displeasing, chromatic aberration, dithering, halftone, screentone, multiple views, logo, too many watermarks, negative space, blank page, lowres, error, artistic error, bad, bad anatomy, bad perspective, bad proportions, bad aspect ratio, bad face, bad teeth, bad neck, "
            )

            negative_prompt_data = {
                "caption": {"base_caption": user_negative_prompt if user_negative_prompt else DEFAULT_NEGATIVE_PROMPT,
                            "char_captions": []},
                "legacy_uc": False
            }

            director_ref_block = build_director_reference(
                ignore_style=ignore_style,
                character_ref=character_ref,
                style_ref=style_ref if (using_split_refs and not ignore_style) else None,
            )

            parameters = {
                "params_version": 3,
                "width": width,
                "height": height,
                "scale": 5,
                "sampler": "k_euler_ancestral",
                "steps": 23,
                "n_samples": 1,
                "qualityToggle": True,
                "cfg_rescale": 0.5,
                "controlnet_strength": 1,
                "add_original_image": True,
                "noise_schedule": "karras",
                "prefer_brownian": True,
                "normalize_reference_strength_multiple": True,
                "legacy": False,
                "legacy_uc": False,
                "ucPreset": 0,
                "v4_prompt": {
                    "caption": {"base_caption": api_prompt, "char_captions": []},
                    "use_coords": False, "use_order": True
                },
                "v4_negative_prompt": negative_prompt_data,
            }
            parameters.update(director_ref_block)

            payload = {
                "action": "generate",
                "model": "nai-diffusion-4-5-full",
                "input": api_prompt,
                "parameters": parameters,
            }

            headers = {
                "Authorization": f"Bearer {NAI_API}",
                "Content-Type": "application/json",
                "Accept": "application/zip",
            }
            url = "https://image.novelai.net/ai/generate-image"

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as resp:
                    if resp.status == 200:
                        zdata = await resp.read()
                        with zipfile.ZipFile(io.BytesIO(zdata)) as z:
                            img_names = [n for n in z.namelist() if
                                         n.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))]
                            if not img_names:
                                await wait_msg.edit(content="복제는 성공한 것 같은데, 이미지가 없다냥?!")
                                return
                            out_name = img_names[0]
                            out_bytes = z.read(out_name)

                        user_channel_key = (ctx.channel.id, user_id)
                        last_generation_data[user_channel_key] = {
                            'command_name': '복제25',
                            'original_discord_prompt': prompt,
                            'reference_data': {
                                'character_ref_b64': character_ref['b64'],
                                'character_ref_cache_key': character_ref['cache_key'],
                                'style_ref_b64': style_ref['b64'] if style_ref else None,
                                'style_ref_cache_key': style_ref['cache_key'] if style_ref else None,
                                'using_split_refs': bool(style_ref),
                                'ref_b64': character_ref['b64'],
                                'ref_cache_key': character_ref['cache_key'],
                            }
                        }

                        timestamp = datetime.now(_KST).strftime("%Y%m%d_%H%M%S")
                        file = discord.File(io.BytesIO(out_bytes), filename=f"clone_{timestamp}_{ctx.message.id}.png")
                        await wait_msg.delete()

                        ref_notice = "1장=캐릭터&스타일 / 2장=스타일 레퍼런스 적용" if (style_ref and not ignore_style) else (
                            "1장=캐릭터 레퍼런스 적용" if ignore_style else "1장=캐릭터&스타일 레퍼런스 적용")
                        await ctx.send(
                            content=(
                                (f"랜덤 추가: `{random_tags_added}`\n" if random_tags_added else "")
                                + f"✅ 복제 완료다냥! ({ref_notice}, 남은 복제 공통: {remaining}/{clone_cap})"
                                + (
                                    "\n오늘 복제 공통 한도를 모두 사용했다냥! "
                                    "사용량은 `&한도` 명령어로 확인해달라냥!"
                                    if remaining == 0 else ""
                                )
                            ),
                            file=file,
                            reference=ctx.message,
                            mention_author=False
                        )
                    else:
                        body = await resp.text()
                        await wait_msg.edit(
                            content=f"복제 실패! 상태코드: {resp.status}\n```json\n{body[:1800]}\n```"
                        )

    except Exception as e:
        try:
            await wait_msg.edit(content=f"복제 중 알 수 없는 오류 발생냥!: {e}")
        except Exception:
            pass
        traceback.print_exc()
    finally:
        user_pending_requests[user_id] = max(0, user_pending_requests.get(user_id, 1) - 1)
        if user_pending_requests[user_id] == 0:
            user_pending_requests.pop(user_id, None)


@bot.command(name='생성24')
async def generate_image_24(ctx, *, prompt: str):
    g_allowed, g_remain, g_reset = await check_and_increment_global_limit(ctx.author.id, command_name="생성24")
    if not g_allowed:
        await ctx.send(
            f"오늘 하루 전체 명령어 사용 한도({GLOBAL_DAILY_LIMIT}회)를 다 썼다냥!\n"
            f"초기화: {g_reset.strftime('%H시 %M분')} (KST)",
            reference=ctx.message, mention_author=False
        )
        return
    global user_pending_requests, processing_lock, last_generation_data, NAI_API
    print(
        f"INFO: User ({ctx.author.id}) used command '생성24' in channel {ctx.channel.id}. Prompt: '{prompt}...'")

    if not NAI_API:
        await ctx.send("봇 설정 오류: NAI_API 키가 설정되지 않았다냥!", reference=ctx.message, mention_author=False)
        print(f"FAIL: '생성24' for ({ctx.author.id}) - NAI_API key not set.")
        return

    user_id = ctx.author.id
    user_channel_key = (ctx.channel.id, user_id)
    current_pending = user_pending_requests.get(user_id, 0)

    if current_pending >= MAX_PENDING_PER_USER:
        active_req = 1 if processing_lock.locked() else 0
        await ctx.send(
            f"처리 대기 중인 내 요청이 이미 {current_pending}개 있다냥! (최대 {MAX_PENDING_PER_USER}개)\n"
            f"(현재 {active_req}개 요청 처리 중) 요청이 처리된 후 다시 시도해달라냥.",
            reference=ctx.message, mention_author=False)
        print(f"INFO: '생성24' for ({ctx.author.id}) - Request limit reached.")
        return

    user_pending_requests[user_id] = current_pending + 1
    processing_status = "다른 요청 처리 중, " if processing_lock.locked() else ""
    wait_msg = await ctx.send(
        f"요청 접수! ({processing_status}내 대기열: {user_pending_requests[user_id]}/{MAX_PENDING_PER_USER})\n"
        f"다른 작업 완료 후 순차적으로 처리된다냥.",
        reference=ctx.message, mention_author=False
    )
    temp_messages_to_delete: list[discord.Message] = [wait_msg] if wait_msg else []

    try:
        async with processing_lock:
            if wait_msg:
                try:
                    await wait_msg.edit(
                        content=f"내 요청 처리 시작! (내 대기열: {user_pending_requests[user_id]}/{MAX_PENDING_PER_USER})")
                except discord.HTTPException:
                    pass

            model_id_from_helper, api_prompt_for_payload, payload_structure, generated_random_tags_str = \
                await _process_prompt_and_get_payload_parts(ctx, ctx.command.name, prompt, temp_messages_to_delete)

            # print(f"--- DEBUG INFO from generate_image_24 ---") # 제거
            # print(f"Helper returned model_id: {model_id_from_helper}") # 제거
            # print(f"Helper returned api_prompt_for_payload: '{api_prompt_for_payload}'") # 제거
            # print(f"Helper returned generated_random_tags_str: '{generated_random_tags_str}'") # 제거
            if payload_structure is None:
                # print(f"CRITICAL DEBUG: payload_structure IS None!") # 제거
                await ctx.send("이미지 생성 설정에 실패했다냥! (내부 오류)", reference=ctx.message, mention_author=False)
                print(f"FAIL: '생성24' for ({ctx.author.id}) - Payload structure is None.")
                return
            # else: print(f"DEBUG: payload_structure IS NOT None.") # 제거

            display_prompt_content = f"2024년(v4) 생성 기능을 사용한다냥! : `{prompt}`"
            if "랜덤" in prompt and generated_random_tags_str:
                display_prompt_content += f"\n랜덤으로 추가된 프롬프트 : `{generated_random_tags_str}`"
            await ctx.send(display_prompt_content, mention_author=False)

            headers = {'Authorization': f'Bearer {NAI_API}', 'Content-Type': 'application/json',
                       'Accept': 'application/zip'}
            payload = payload_structure  # 생성24도 레퍼런스 미지원
            api_url = 'https://image.novelai.net/ai/generate-image'

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(api_url, headers=headers, json=payload) as response:
                        if response.status == 200:
                            zip_binary = await response.read()
                            with zipfile.ZipFile(io.BytesIO(zip_binary)) as zip_ref:
                                image_name = zip_ref.namelist()[0]
                                image_binary = zip_ref.read(image_name)

                            image_file = discord.File(io.BytesIO(image_binary),
                                                      filename=f'full_{ctx.message.id}.png')
                            await ctx.send(file=image_file, mention_author=False)
                            print(f"SUCCESS: '생성24' for ({ctx.author.id}). Image sent.")

                            last_generation_data[user_channel_key] = {
                                'command_name': ctx.command.name,
                                'original_discord_prompt': prompt,
                                'reference_data': {'base64': [], 'info': [], 'strength': []}
                            }
                        elif response.status == 429:
                            await ctx.send(f"생성 실패: API 동시 생성 제한(429)!", reference=ctx.message, mention_author=False)
                            print(f"FAIL: '생성24' for ({ctx.author.id}) - API Rate limit (429).")
                        else:
                            error_binary = await response.read();
                            error_text = error_binary.decode('utf-8', errors='ignore')
                            await ctx.send(f'API 호출 실패! 상태코드: {response.status}\n```json\n{error_text[:500]}\n```',
                                           reference=ctx.message, mention_author=False)
                            print(
                                f"FAIL: '생성24' for ({ctx.author.id}) - API Error {response.status}: {error_text[:200]}")
            except aiohttp.ClientError as e:
                await ctx.send(f"생성 실패: API 서버 연결 실패냥!: {e}", reference=ctx.message, mention_author=False)
                print(f"FAIL: '생성24' for ({ctx.author.id}) - aiohttp.ClientError: {e}")
                traceback.print_exc()
            except Exception as e:
                await ctx.send(f'오류 발생: {e}', reference=ctx.message, mention_author=False)
                print(f"FAIL: '생성24' for ({ctx.author.id}) - Unknown error: {e}")
                traceback.print_exc()
    finally:
        user_pending_requests[user_id] = user_pending_requests.get(user_id, 1) - 1
        if user_pending_requests[user_id] <= 0:
            user_pending_requests.pop(user_id, None)
        for msg_to_delete in temp_messages_to_delete:
            try:
                if msg_to_delete: await msg_to_delete.delete()
            except discord.HTTPException:
                pass


try:
    from sd_parsers import ParserManager, Eagerness

    parser_manager = ParserManager(eagerness=Eagerness.EAGER)
    SD_PARSERS_AVAILABLE = True
except Exception:
    parser_manager = None
    SD_PARSERS_AVAILABLE = False

SUPPORTED_EXTS = ('.jpg', '.jpeg', '.png', '.tiff', '.webp')


# 공통: 모델 태그 뽑는 함수
def detect_model_tag_from_metadata(meta: dict) -> str:
    """
    sd-parsers가 주는 metadata/raw_params에서 모델 이름을 추측해서
    네가 쓰던 태그 (**[생성25]** 같은 것)를 돌려준다.
    잘 모르겠으면 '' 반환.
    """
    if not meta:
        return ""

    text_blob = json.dumps(meta).lower()

    if 'nai diffusion v5' in text_blob or 'nai-diffusion-5' in text_blob:
        return "**[생성26]** "
    if 'nai diffusion v4.5' in text_blob or 'nai-diffusion-4-5' in text_blob:
        return "**[생성25]** "
    if 'nai diffusion v4' in text_blob or 'nai-diffusion-4' in text_blob:
        return "**[생성24]** "
    if 'nai diffusion v3' in text_blob or 'nai-diffusion-3' in text_blob:
        return "**[생성23]** "

    return ""


async def process_image_bytes(ctx: commands.Context, filename: str, image_bytes: bytes):
    """
    이미지 메타데이터를 분석하여 프롬프트 정보를 보여주는 함수
    - 파일 전송 기능 제거 -> 무조건 메시지로 분리 전송
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        print(f"[DEBUG] 이미지 열기 실패: {e}")
        return

    main_prompt_content = None
    negative_prompt_content = None
    detected_model_tag = ""

    # [핵심] JSON 데이터에서 정보를 추출하는 로직 (V4 구조 완벽 대응)
    def extract_from_json(json_data):
        m_prompt, n_prompt, tag = None, None, ""

        # [A] 긍정 프롬프트 (V4 & V3)
        if 'v4_prompt' in json_data and 'caption' in json_data['v4_prompt']:
            caption_obj = json_data['v4_prompt']['caption']
            base = caption_obj.get('base_caption', "")
            # 캐릭터 캡션 병합
            char_list = caption_obj.get('char_captions', [])
            char_text = ""
            if char_list:
                for idx, char_data in enumerate(char_list, 1):
                    if 'char_caption' in char_data:
                        char_text += f"\n**[Character {idx}]** {char_data['char_caption']}"
            m_prompt = base + char_text
        elif 'prompt' in json_data:
            m_prompt = json_data['prompt']

        # [B] 부정 프롬프트 (우선순위: v4_negative_prompt > uc > negative_prompt)
        if 'v4_negative_prompt' in json_data:
            v4_neg = json_data['v4_negative_prompt']
            if isinstance(v4_neg, dict) and 'caption' in v4_neg:
                n_prompt = v4_neg['caption'].get('base_caption', "")
            elif isinstance(v4_neg, str):
                n_prompt = v4_neg

        if not n_prompt and 'uc' in json_data:
            n_prompt = json_data['uc']

        if not n_prompt and 'negative_prompt' in json_data:
            n_prompt = json_data['negative_prompt']

        # [C] 모델 태그
        has_ref = False
        refs = json_data.get('director_reference_images') or json_data.get('reference_image_multiple')
        if isinstance(refs, list) and len(refs) > 0:
            has_ref = True

        if has_ref:
            tag = "**[복제]** "
        else:
            mid = json_data.get('model', '')
            if isinstance(mid, str):
                mid_low = mid.lower()
                if 'nai-diffusion-5' in mid_low:
                    tag = "**[생성26]** "
                elif 'nai-diffusion-4-5' in mid_low:
                    tag = "**[생성25]** "
                elif 'nai-diffusion-4' in mid_low:
                    tag = "**[생성24]** "
                elif 'nai-diffusion-3' in mid_low:
                    tag = "**[생성23]** "

        return m_prompt, n_prompt, tag

    print(f"\n--- [DEBUG] 이미지 분석 시작: {filename} ---")

    # ===== 1. PIL 파싱 =====
    if isinstance(image, PngImagePlugin.PngImageFile):
        for key, value in image.info.items():
            value_str = str(value)
            if isinstance(value, bytes):
                try:
                    value_str = value.decode('utf-8', errors='ignore').strip('\x00').strip()
                except:
                    pass

            if key in ('Comment', 'Raw Parameters') and value_str.startswith('{') and value_str.endswith('}'):
                try:
                    json_data = json.loads(value_str)
                    p, n, t = extract_from_json(json_data)
                    if p:
                        main_prompt_content, negative_prompt_content, detected_model_tag = p, n, t
                        break
                except:
                    pass

            elif key == 'parameters' and not main_prompt_content:
                if "Negative prompt:" in value_str:
                    parts = value_str.split("Negative prompt:", 1)
                    main_prompt_content = parts[0].strip()
                    remaining = parts[1]
                    if "Steps:" in remaining:
                        negative_prompt_content = remaining.split("Steps:", 1)[0].strip()
                    else:
                        negative_prompt_content = remaining.strip()
                break

    # ===== 2. sd-parsers 처리 =====
    if not main_prompt_content and SD_PARSERS_AVAILABLE:
        try:
            prompt_info = parser_manager.parse(image)
            if prompt_info:
                raw_metadata = getattr(prompt_info, "metadata", None)
                if isinstance(raw_metadata, dict):
                    p_raw, n_raw, t_raw = extract_from_json(raw_metadata)
                    if p_raw: main_prompt_content = p_raw
                    if n_raw: negative_prompt_content = n_raw
                    if t_raw: detected_model_tag = t_raw

                if not main_prompt_content:
                    if getattr(prompt_info, "full_prompt", None):
                        main_prompt_content = prompt_info.full_prompt
                    elif prompt_info.prompts and hasattr(prompt_info.prompts[0], "value"):
                        main_prompt_content = prompt_info.prompts[0].value

                if not negative_prompt_content:
                    if getattr(prompt_info, "negative_prompt", None):
                        negative_prompt_content = prompt_info.negative_prompt
                    elif prompt_info.prompts and hasattr(prompt_info.prompts[0], "negative_prompt"):
                        negative_prompt_content = prompt_info.prompts[0].negative_prompt

                if not detected_model_tag:
                    detected_model_tag = detect_model_tag_from_metadata(getattr(prompt_info, "metadata", None))
        except Exception:
            pass

    # ===== 3. 최종 출력 (메시지 분리 전송 로직) =====
    if not main_prompt_content:
        await ctx.send(f"'{filename}'에서 프롬프트를 찾을 수 없다냥!", reference=ctx.message, mention_author=False)
        return

    # [1] 첫 번째 메시지: 파일 정보 + 긍정 프롬프트
    header_text = f"📄 {detected_model_tag}**{filename}의 생성 정보** 📄\n**[Prompt]**"
    prompt_text = f"```\n{main_prompt_content}\n```"

    # 긍정 프롬프트가 너무 길 경우를 대비해 안전하게 전송
    if len(header_text) + len(prompt_text) > 1900:
        await ctx.send(header_text, reference=ctx.message, mention_author=False)
        # 내용이 2000자를 넘어가면 나눠서 보냄
        for i in range(0, len(prompt_text), 1900):
            await ctx.send(prompt_text[i:i + 1900], mention_author=False)
    else:
        await ctx.send(header_text + "\n" + prompt_text, reference=ctx.message, mention_author=False)

    # [2] 두 번째 메시지: 부정 프롬프트 (있을 경우에만)
    if negative_prompt_content:
        neg_header = "\n🚫 **Negative Prompt**"
        neg_text = f"```\n{negative_prompt_content}\n```"

        if len(neg_header) + len(neg_text) > 1900:
            await ctx.send(neg_header, mention_author=False)
            for i in range(0, len(neg_text), 1900):
                await ctx.send(neg_text[i:i + 1900], mention_author=False)
        else:
            await ctx.send(neg_header + "\n" + neg_text, mention_author=False)


@bot.command(name='데이터')
async def extract_main_prompt_with_tag(ctx: commands.Context):
    g_allowed, g_remain, g_reset = await check_and_increment_global_limit(ctx.author.id)
    if not g_allowed:
        await ctx.send(
            f"오늘 하루 전체 명령어 사용 한도({GLOBAL_DAILY_LIMIT}회)를 다 썼다냥!\n"
            f"초기화: {g_reset.strftime('%H시 %M분')} (KST)",
            reference=ctx.message, mention_author=False
        )
        return
    print(f"INFO: User ({ctx.author.id}) used command '데이터' in channel {ctx.channel.id}")

    if not ctx.message.attachments:
        await ctx.send("생성 프롬프트를 분석할 이미지를 함께 첨부해달라냥!", reference=ctx.message, mention_author=False)
        return

    for attachment in ctx.message.attachments:
        filename = attachment.filename

        # ZIP이면 안에 있는 이미지 전부 처리
        if filename.lower().endswith('.zip'):
            zip_bytes = await attachment.read()
            try:
                with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
                    found_any = False
                    for name in zf.namelist():
                        if not name.lower().endswith(SUPPORTED_EXTS):
                            continue
                        found_any = True
                        img_bytes = zf.read(name)
                        await process_image_bytes(ctx, name, img_bytes)
                    if not found_any:
                        await ctx.send(f"'{filename}' 안에 처리할 이미지가 없다냥!", reference=ctx.message, mention_author=False)
            except zipfile.BadZipFile:
                await ctx.send(f"'{filename}'는 zip 파일이 아니라서 열 수 없다냥!", reference=ctx.message, mention_author=False)
            continue

        # 일반 이미지
        if not filename.lower().endswith(SUPPORTED_EXTS):
            await ctx.send(f"'{filename}' 파일은 분석할 수 있는 이미지 형식이 아니다냥. (jpg, png, tiff, webp만 지원)",
                           reference=ctx.message, mention_author=False)
            continue

        img_bytes = await attachment.read()
        await process_image_bytes(ctx, filename, img_bytes)


@bot.command(name='표정')
async def change_emotion(ctx: commands.Context, *, emotion_prompt: str):
    # print(f"--- 표정 명령어 시작:  ---") # 제거
    command_name = ctx.command.name
    print(
        f"INFO: User ({ctx.author.id}) used command '{command_name}' in channel {ctx.channel.id}. Emotion: '{emotion_prompt}'")

    NOVELAI_EDIT_ENDPOINT = 'https://image.novelai.net/ai/augment-image'
    user_id = ctx.author.id
    wait_msg = None

    VALID_EMOTIONS = ["playful", "hurt", "determined", "love", "worried", "embarrassed", "aroused", "happy", "sad",
                      "angry", "confused", "tired", "scared", "surprised", "shy", "excited", "disgusted", "nervous",
                      "thinking", "laughing", "bored", "neutral", "smug"]
    VALID_EMOTIONS_SET = set(VALID_EMOTIONS)

    try:
        # print("DEBUG: NAI_API 확인 중") # 제거
        if not NAI_API:
            # print("DEBUG: NAI_API 없음") # 제거
            await ctx.send("봇 설정 오류: NAI_API 키가 설정되지 않았다냥!", reference=ctx.message, mention_author=False)
            print(f"FAIL: '{command_name}' for ({ctx.author.id}) - NAI_API key not set.")
            return

        if emotion_prompt.lower() not in VALID_EMOTIONS_SET:
            # print(f"DEBUG: 유효하지 않은 표정 프롬프트: {emotion_prompt}") # 제거
            valid_emotions_str = ", ".join(VALID_EMOTIONS)
            await ctx.send(f"표정 변경 실패: 지원하지 않는 표정이다냥! 다음 표정만 사용 가능: {valid_emotions_str}", reference=ctx.message,
                           mention_author=False)
            print(f"FAIL: '{command_name}' for ({ctx.author.id}) - Invalid emotion: {emotion_prompt}")
            return

        current_pending = user_pending_requests.get(user_id, 0)
        # print(f"DEBUG: 현재 대기열: {current_pending}") # 제거
        if current_pending >= MAX_PENDING_PER_USER:
            active_req = 1 if processing_lock.locked() else 0
            # print(f"DEBUG: 대기열 초과 ({current_pending}/{MAX_PENDING_PER_USER}), Lock: {processing_lock.locked()}") # 제거
            await ctx.send(
                f"처리 대기 중인 내 요청이 이미 {current_pending}개 있다냥! (최대 {MAX_PENDING_PER_USER}개)\n"
                f"(현재 {active_req}개 요청 처리 중) 요청이 처리된 후 다시 시도해달라냥.",
                reference=ctx.message, mention_author=False)
            print(f"INFO: '{command_name}' for ({ctx.author.id}) - Request limit reached.")
            return

        # print("DEBUG: 첨부파일 확인 중") # 제거
        if not ctx.message.attachments:
            # print("DEBUG: 첨부파일 없음") # 제거
            await ctx.send("표정을 바꿀 이미지를 첨부해달라냥!", reference=ctx.message, mention_author=False)
            print(f"FAIL: '{command_name}' for ({ctx.author.id}) - No attachment provided.")
            return
        if len(ctx.message.attachments) > 1:
            # print("DEBUG: 첨부파일 1개 초과") # 제거
            await ctx.send("표정 변경은 한 번에 하나의 이미지만 가능하다냥!", reference=ctx.message, mention_author=False)
            print(f"FAIL: '{command_name}' for ({ctx.author.id}) - Too many attachments.")
            return

        attachment = ctx.message.attachments[0]
        # print(f"DEBUG: 첨부파일 정보: {attachment.filename}, {attachment.content_type}") # 제거

        # print("DEBUG: 이미지 타입 확인 중") # 제거
        allowed_extensions = ('.png', '.jpg', '.jpeg', '.webp')
        is_image_type = attachment.content_type and attachment.content_type.startswith('image/')
        is_image_extension = attachment.filename.lower().endswith(allowed_extensions)
        if not (is_image_type or is_image_extension):
            # print(f"DEBUG: 지원하지 않는 파일 타입 ({attachment.content_type}, {attachment.filename})") # 제거
            await ctx.send(f"첨부된 파일 '{attachment.filename}'은 지원하는 이미지 형식이 아니다냥! (png, jpg, webp 등)",
                           reference=ctx.message, mention_author=False)
            print(
                f"FAIL: '{command_name}' for ({ctx.author.id}) - Unsupported file type: {attachment.filename}")
            return

        user_pending_requests[user_id] = current_pending + 1
        # print(f"DEBUG: 대기열 카운트 증가 후: {user_pending_requests.get(user_id)}") # 제거
        processing_status = "다른 요청 처리 중, " if processing_lock.locked() else ""
        # print(f"DEBUG: 요청 접수 메시지 보내기 시도 (Lock: {processing_lock.locked()})") # 제거
        wait_msg = await ctx.send(
            f"표정 변경 요청 접수! (`{emotion_prompt}`) ({processing_status}내 대기열: {user_pending_requests[user_id]}/{MAX_PENDING_PER_USER})\n"
            f"다른 작업 완료 후 순차적으로 처리된다냥.",
            reference=ctx.message, mention_author=False
        )
        # print("DEBUG: 요청 접수 메시지 보냄") # 제거

        # print("DEBUG: 락 획득 시도") # 제거
        async with processing_lock:
            # print("DEBUG: 락 획득 완료") # 제거
            if wait_msg:
                try:
                    await wait_msg.edit(
                        content=f"내 표정 변경 요청 처리 시작! (`{emotion_prompt}`) (내 대기열: {user_pending_requests[user_id]}/{MAX_PENDING_PER_USER})")
                    # print("DEBUG: 대기 메시지 수정 완료") # 제거
                except discord.HTTPException:
                    # print("DEBUG: 대기 메시지 수정 실패 (무시)") # 제거
                    pass

            image_bytes, width, height, base64_encoded_image = None, 0, 0, None
            processing_attachments_msg = None

            try:  # 이미지 처리 블록
                # print("DEBUG: 첨부 파일 처리 메시지 보내기 시도") # 제거
                processing_attachments_msg = await ctx.send("첨부 파일 처리 중...", reference=ctx.message,
                                                            mention_author=False)
                # print("DEBUG: 첨부 파일 읽기 시도") # 제거
                image_bytes = await attachment.read()
                # print(f"DEBUG: 첨부 파일 읽기 완료 ({len(image_bytes)} bytes)") # 제거

                try:  # Pillow 처리 블록
                    # print("DEBUG: Pillow로 이미지 열기 시도") # 제거
                    with Image.open(io.BytesIO(image_bytes)) as img:
                        width, height = img.size
                        # print(f"DEBUG: 이미지 크기 확인 완료: {width}x{height}") # 제거

                        MAX_DIMENSION_LIMIT = 2560  # 최대 허용 이미지 크기
                        if width > MAX_DIMENSION_LIMIT or height > MAX_DIMENSION_LIMIT:
                            # print(f"DEBUG: 이미지 크기 제한 초과 ({width}x{height} > {MAX_DIMENSION_LIMIT}px)") # 제거
                            if processing_attachments_msg: await processing_attachments_msg.delete()
                            await ctx.send(f"이미지 크기가 너무 크다냥! (최대 {MAX_DIMENSION_LIMIT}px, 현재: {width}x{height})",
                                           reference=ctx.message, mention_author=False)
                            print(
                                f"FAIL: '{command_name}' for ({ctx.author.id}) - Image too large: {width}x{height}")
                            return

                        MAX_IMAGE_SIZE_SQUARE, MAX_IMAGE_SIZE_NON_SQUARE = 1024, 1216
                        MAX_IMAGE_SIZE = MAX_IMAGE_SIZE_SQUARE if width == height else MAX_IMAGE_SIZE_NON_SQUARE
                        # print(f"DEBUG: 적용된 (리사이징 기준) 최대 이미지 크기: {MAX_IMAGE_SIZE}") # 제거

                        if width > MAX_IMAGE_SIZE or height > MAX_IMAGE_SIZE:  # API 최대 크기 초과 시 리사이즈
                            # print(f"DEBUG: API 이미지 크기 제한({MAX_IMAGE_SIZE}px) 초과, 리사이즈 필요") # 제거
                            if wait_msg:
                                try:
                                    await wait_msg.edit(
                                        content=f"{wait_msg.content}\n이미지 리사이징 중 (최대 {MAX_IMAGE_SIZE}px)...")
                                # print("DEBUG: 대기 메시지에 리사이징 알림 추가") # 제거
                                except discord.HTTPException:
                                    pass  # print("DEBUG: 대기 메시지 수정 실패 (리사이징 알림)") # 제거

                            # print("DEBUG: 리사이즈 시작") # 제거
                            ratio = MAX_IMAGE_SIZE / max(width, height)  # 더 긴 쪽을 기준으로 비율 계산
                            new_width, new_height = int(width * ratio), int(height * ratio)
                            img = img.resize((new_width, new_height), Image.LANCZOS)
                            # print(f"DEBUG: 이미지 리사이즈 완료: {new_width}x{new_height}") # 제거
                            width, height = new_width, new_height

                            if wait_msg:  # 대기 메시지 원상 복구
                                try:
                                    await wait_msg.edit(
                                        content=f"내 표정 변경 요청 처리 시작! (`{emotion_prompt}`) (내 대기열: {user_pending_requests[user_id]}/{MAX_PENDING_PER_USER})")
                                # print("DEBUG: 대기 메시지 리사이징 알림 제거") # 제거
                                except discord.HTTPException:
                                    pass  # print("DEBUG: 대기 메시지 수정 실패 (리사이징 알림 제거)") # 제거

                        resized_image_bytes_io = io.BytesIO()
                        img.save(resized_image_bytes_io, format='PNG')  # PNG로 통일
                        image_bytes = resized_image_bytes_io.getvalue()
                        # print(f"DEBUG: 최종 이미지 bytes 업데이트 완료 ({len(image_bytes)} bytes, format=PNG)") # 제거

                except Exception as img_err:  # Pillow 처리 실패
                    # print(f"DEBUG: Pillow 처리 오류: {img_err}") # 제거
                    if processing_attachments_msg: await processing_attachments_msg.delete()
                    error_msg = f"첨부된 이미지를 처리하는 중 오류가 발생했다냥: {img_err}"
                    if "killed" in str(img_err).lower(): error_msg += "\n(메모리 부족일 수 있다냥!)"
                    await ctx.send(error_msg, reference=ctx.message, mention_author=False)
                    print(
                        f"FAIL: '{command_name}' (Pillow processing) for ({ctx.author.id}). Reason: {img_err}")
                    return

                # print("DEBUG: Base64 인코딩 시도") # 제거
                base64_encoded_image = base64.b64encode(image_bytes).decode('utf-8')
                # print("DEBUG: Base64 인코딩 완료") # 제거
                if processing_attachments_msg: await processing_attachments_msg.delete()  # print("DEBUG: 첨부 파일 처리 메시지 삭제 완료") # 제거

            except discord.HTTPException as e:  # 디스코드 HTTP 오류 (첨부파일 다운로드 등)
                # print(f"DEBUG: 첨부 파일 처리 중 discord.HTTPException: {e}") # 제거
                if processing_attachments_msg: await processing_attachments_msg.delete()
                if wait_msg: await wait_msg.delete(); wait_msg = None
                await ctx.send(f"첨부 파일 처리 중 오류 발생냥!: {e}", reference=ctx.message, mention_author=False)
                print(f"FAIL: '{command_name}' (attachment processing) for ({ctx.author.id}). Reason: {e}")
                return
            except Exception as e:  # 그 외 이미지 처리 오류
                # print(f"DEBUG: 첨부 파일 처리/인코딩 중 기타 오류: {e}") # 제거
                if processing_attachments_msg: await processing_attachments_msg.delete()
                if wait_msg: await wait_msg.delete(); wait_msg = None
                await ctx.send(f"첨부 파일 처리 중 알 수 없는 오류 발생냥!: {e}", reference=ctx.message, mention_author=False)
                print(f"FAIL: '{command_name}' (attachment/encoding) for ({ctx.author.id}). Reason: {e}")
                traceback.print_exc()
                return

            # print("DEBUG: 페이로드 구성 시도") # 제거
            headers = {'Authorization': f'Bearer {NAI_API}', 'Content-Type': 'application/json',
                       'Accept': 'application/zip'}
            payload = {"req_type": "emotion", "prompt": f"{emotion_prompt};;", "defry": 0, "width": width,
                       "height": height, "image": base64_encoded_image}
            # print("DEBUG: 페이로드 구성 완료") # 제거

            try:  # API 요청 및 결과 처리
                # print("DEBUG: aiohttp 세션 생성 시도") # 제거
                async with aiohttp.ClientSession() as session:
                    # print(f"DEBUG: API 요청 시도: {NOVELAI_EDIT_ENDPOINT}") # 제거
                    async with session.post(NOVELAI_EDIT_ENDPOINT, headers=headers, json=payload) as response:
                        # print(f"DEBUG: API 응답 수신: {response.status}") # 제거
                        if wait_msg: await wait_msg.delete(); wait_msg = None  # print("DEBUG: 대기 메시지 삭제 완료 (API 응답 후)") # 제거

                        if response.status == 200:
                            # print("DEBUG: API 응답 성공 (200)") # 제거
                            zip_binary = await response.read()
                            # print(f"DEBUG: 응답 데이터 읽기 완료 ({len(zip_binary)} bytes)") # 제거
                            try:
                                # print("DEBUG: Zip 파일 처리 시도") # 제거
                                with zipfile.ZipFile(io.BytesIO(zip_binary)) as zip_ref:
                                    image_name = zip_ref.namelist()[0] if zip_ref.namelist() else None
                                    if not image_name:
                                        # print("DEBUG: Zip 파일이 비어 있음") # 제거
                                        await ctx.send("표정 변경 실패: API 응답 zip 파일이 비어있다냥!", reference=ctx.message,
                                                       mention_author=False)
                                        print(
                                            f"FAIL: '{command_name}' for ({ctx.author.id}) - Empty zip from API.")
                                        return
                                    image_binary = zip_ref.read(image_name)
                                    # print(f"DEBUG: 이미지 파일 추출 완료: {image_name}") # 제거
                                filename = f'nai_emotion_{ctx.message.id}.png'
                                image_file = discord.File(io.BytesIO(image_binary), filename=filename)
                                send_content = f"이미지 표정 변경 완료! (`{emotion_prompt}`)"
                                # print("DEBUG: 결과 전송 시도") # 제거
                                await ctx.send(content=send_content, file=image_file, reference=ctx.message,
                                               mention_author=False)
                                print(f"SUCCESS: '{command_name}' for ({ctx.author.id}). Image sent.")
                            except zipfile.BadZipFile:
                                # print("DEBUG: 잘못된 Zip 파일 오류") # 제거
                                await ctx.send("표정 변경 실패: API가 유효한 zip 파일을 반환하지 않았다냥!", reference=ctx.message,
                                               mention_author=False)
                                print(
                                    f"FAIL: '{command_name}' (zip processing) for ({ctx.author.id}) - BadZipFile.")
                                return
                            except Exception as zip_err:
                                # print(f"DEBUG: Zip 처리 중 오류: {zip_err}") # 제거
                                await ctx.send(f"표정 변경 실패: 응답 처리 중 오류 발생냥! {zip_err}", reference=ctx.message,
                                               mention_author=False)
                                print(
                                    f"FAIL: '{command_name}' (zip processing) for ({ctx.author.id}). Reason: {zip_err}")
                                return
                        elif response.status == 401:  # 인증 실패
                            # print("DEBUG: API 인증 실패 (401)") # 제거
                            await ctx.send(f"표정 변경 실패: API 인증 실패(401). API 키를 확인해달라냥.", reference=ctx.message,
                                           mention_author=False)
                            print(f"FAIL: '{command_name}' for ({ctx.author.id}) - API Auth Error (401).")
                            return
                        elif response.status == 429:  # 동시 처리 제한
                            # print("DEBUG: API 속도 제한 (429)") # 제거
                            await ctx.send(f"표정 변경 실패: API 동시 처리 제한(429) 같다냥! 잠시 후 다시 시도해달라냥.", reference=ctx.message,
                                           mention_author=False)
                            print(f"FAIL: '{command_name}' for ({ctx.author.id}) - API Rate Limit (429).")
                            return
                        elif response.status == 500:  # 서버 내부 오류
                            # print("DEBUG: API 서버 내부 오류 (500)") # 제거
                            error_binary = await response.read();
                            error_text = error_binary.decode('utf-8', errors='ignore')
                            await ctx.send(f'표정 변경 실패: NovelAI 서버 내부 오류(500) 발생냥!\n```\n{error_text[:1000]}\n```',
                                           reference=ctx.message, mention_author=False)
                            print(
                                f"FAIL: '{command_name}' for ({ctx.author.id}) - API Server Error (500): {error_text[:200]}")
                            return
                        else:  # 기타 API 오류
                            # print(f"DEBUG: API 기타 오류 ({response.status})") # 제거
                            error_binary = await response.read();
                            error_text = error_binary.decode('utf-8', errors='ignore')
                            await ctx.send(f'표정 변경 실패! 상태코드: {response.status}\n```\n{error_text[:1000]}\n```',
                                           reference=ctx.message, mention_author=False)
                            print(
                                f"FAIL: '{command_name}' for ({ctx.author.id}) - API Error {response.status}: {error_text[:200]}")
                            return
            except aiohttp.ClientError as e:  # API 서버 연결 실패
                # print(f"DEBUG: aiohttp.ClientError: {e}") # 제거
                if wait_msg: await wait_msg.delete()
                await ctx.send(f"표정 변경 실패: API 서버 연결 실패냥!: {e}", reference=ctx.message, mention_author=False)
                print(f"FAIL: '{command_name}' for ({ctx.author.id}) - aiohttp.ClientError: {e}")
                traceback.print_exc()
                return
            except Exception as e:  # 그 외 API 요청/처리 중 오류
                # print(f"DEBUG: API 요청/처리 중 기타 오류: {e}") # 제거
                if wait_msg: await wait_msg.delete()
                await ctx.send(f'표정 변경 중 알 수 없는 오류 발생냥!: {e}', reference=ctx.message, mention_author=False)
                print(f"FAIL: '{command_name}' for ({ctx.author.id}) - Unknown API processing error: {e}")
                traceback.print_exc()
                return
            # print("DEBUG: 락 해제됨") # 제거
    except Exception as e:  # 락 획득 전 최상위 예외
        # print(f"!!!!!! 명령어 처리 중 예상치 못한 상위 레벨 예외 발생: {type(e).__name__}: {e} !!!!!!") # 제거
        print(f"CRITICAL FAIL: '{command_name}' for ({ctx.author.id}) - Top-level pre-lock error: {e}")
        traceback.print_exc()
        if wait_msg: await wait_msg.delete()
        try:
            await ctx.send(f"명령어 처리 중 예상치 못한 오류 발생냥!: {e}", reference=ctx.message, mention_author=False)
        except Exception as send_err:
            print(f"CRITICAL FAIL: Could not send error message for '{command_name}'. Reason: {send_err}")
    finally:  # 사용자 요청 카운트 감소
        if user_pending_requests.get(user_id, 0) > 0:
            # current_count_before_decrement = user_pending_requests.get(user_id, 0) # 제거
            # print(f"DEBUG: finally - 사용자 {user_id} 대기 카운트 감소 전: {current_count_before_decrement}") # 제거
            user_pending_requests[user_id] -= 1
            if user_pending_requests[user_id] <= 0:
                user_pending_requests.pop(user_id, None)
                # print(f"DEBUG: finally - 사용자 {user_id} 대기 카운트 0 이하, 제거됨") # 제거
            # else: # current_count_after_decrement = user_pending_requests.get(user_id); print(f"DEBUG: finally - 사용자 {user_id} 대기 카운트 감소 후: {current_count_after_decrement}") # 제거
        # else: print(f"DEBUG: finally - 사용자 {user_id} 대기열에 없거나 이미 0 이하, 카운트 변경 없음") # 제거


@bot.command(name='제거')
async def declutter(ctx: commands.Context):
    g_allowed, g_remain, g_reset = await check_and_increment_global_limit(ctx.author.id)
    if not g_allowed:
        await ctx.send(
            f"오늘 하루 전체 명령어 사용 한도({GLOBAL_DAILY_LIMIT}회)를 다 썼다냥!\n"
            f"초기화: {g_reset.strftime('%H시 %M분')} (KST)",
            reference=ctx.message, mention_author=False
        )
        return
    command_name = ctx.command.name
    print(f"INFO: User ({ctx.author.id}) used command '{command_name}' in channel {ctx.channel.id}.")
    NOVELAI_EDIT_ENDPOINT = 'https://image.novelai.net/ai/augment-image'
    user_id = ctx.author.id
    wait_msg = None
    try:
        if not NAI_API:
            await ctx.send("봇 설정 오류: NAI_API 키가 설정되지 않았다냥!", reference=ctx.message, mention_author=False)
            print(f"FAIL: '{command_name}' for ({ctx.author.id}) - NAI_API key not set.")
            return
        current_pending = user_pending_requests.get(user_id, 0)
        if current_pending >= MAX_PENDING_PER_USER:
            active_req = 1 if processing_lock.locked() else 0
            await ctx.send(
                f"처리 대기 중인 내 요청이 이미 {current_pending}개 있다냥! (최대 {MAX_PENDING_PER_USER}개)\n(현재 {active_req}개 요청 처리 중)",
                reference=ctx.message, mention_author=False)
            print(f"INFO: '{command_name}' for ({ctx.author.id}) - Request limit reached.")
            return
        if not ctx.message.attachments or len(ctx.message.attachments) > 1:
            await ctx.send("효과를 제거할 이미지를 하나만 첨부해달라냥!", reference=ctx.message, mention_author=False)
            print(f"FAIL: '{command_name}' for ({ctx.author.id}) - Incorrect attachment count.")
            return
        attachment = ctx.message.attachments[0]
        allowed_extensions = ('.png', '.jpg', '.jpeg', '.webp')
        if not ((attachment.content_type and attachment.content_type.startswith(
                'image/')) or attachment.filename.lower().endswith(allowed_extensions)):
            await ctx.send(f"첨부된 파일 '{attachment.filename}'은 지원하는 이미지 형식이 아니다냥!", reference=ctx.message,
                           mention_author=False)
            print(
                f"FAIL: '{command_name}' for ({ctx.author.id}) - Unsupported file type: {attachment.filename}")
            return
        user_pending_requests[user_id] = current_pending + 1
        processing_status = "다른 요청 처리 중, " if processing_lock.locked() else ""
        wait_msg = await ctx.send(
            f"제거 요청 접수! ({processing_status}내 대기열: {user_pending_requests[user_id]}/{MAX_PENDING_PER_USER})",
            reference=ctx.message, mention_author=False)
        async with processing_lock:
            if wait_msg:
                try:
                    await wait_msg.edit(
                        content=f"내 제거 요청 처리 시작! (내 대기열: {user_pending_requests[user_id]}/{MAX_PENDING_PER_USER})")
                except discord.HTTPException:
                    pass
            processing_attachments_msg = await ctx.send("첨부 파일 처리 중...", reference=ctx.message, mention_author=False)
            image_bytes = await attachment.read()
            try:
                with Image.open(io.BytesIO(image_bytes)) as img:
                    width, height = img.size
                    MAX_DIMENSION_LIMIT = 2560
                    if width > MAX_DIMENSION_LIMIT or height > MAX_DIMENSION_LIMIT:
                        if processing_attachments_msg: await processing_attachments_msg.delete()
                        await ctx.send(f"이미지 크기가 너무 크다냥! (최대 {MAX_DIMENSION_LIMIT}px, 현재: {width}x{height})",
                                       reference=ctx.message, mention_author=False)
                        print(
                            f"FAIL: '{command_name}' for ({ctx.author.id}) - Image too large: {width}x{height}")
                        return
                    MAX_API_SIZE = 1024 if width == height else 1216
                    if width > MAX_API_SIZE or height > MAX_API_SIZE:
                        if wait_msg:
                            try:
                                await wait_msg.edit(content=f"{wait_msg.content}\n이미지 리사이징 중 (최대 {MAX_API_SIZE}px)...")
                            except discord.HTTPException:
                                pass
                        ratio = MAX_API_SIZE / max(width, height)
                        new_width, new_height = int(width * ratio), int(height * ratio)
                        img = img.resize((new_width, new_height), Image.LANCZOS)
                        width, height = new_width, new_height
                        if wait_msg:
                            try:
                                await wait_msg.edit(
                                    content=f"내 제거 요청 처리 시작! (내 대기열: {user_pending_requests[user_id]}/{MAX_PENDING_PER_USER})")
                            except discord.HTTPException:
                                pass
                    img_byte_arr = io.BytesIO();
                    img.save(img_byte_arr, format='PNG');
                    image_bytes = img_byte_arr.getvalue()
            except Exception as img_err:
                if processing_attachments_msg: await processing_attachments_msg.delete()
                await ctx.send(f"이미지 처리 중 오류 발생: {img_err}", reference=ctx.message, mention_author=False)
                print(
                    f"FAIL: '{command_name}' (Pillow processing) for ({ctx.author.id}). Reason: {img_err}")
                return
            base64_encoded_image = base64.b64encode(image_bytes).decode('utf-8')
            if processing_attachments_msg: await processing_attachments_msg.delete()
            headers = {'Authorization': f'Bearer {NAI_API}', 'Content-Type': 'application/json',
                       'Accept': 'application/zip'}
            payload = {"req_type": "declutter", "width": width, "height": height, "image": base64_encoded_image}
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(NOVELAI_EDIT_ENDPOINT, headers=headers, json=payload) as response:
                        if wait_msg: await wait_msg.delete(); wait_msg = None
                        if response.status == 200:
                            zip_binary = await response.read()
                            with zipfile.ZipFile(io.BytesIO(zip_binary)) as zip_ref:
                                image_name = zip_ref.namelist()[0] if zip_ref.namelist() else None
                                if not image_name:
                                    await ctx.send("제거 실패: API 응답 zip 파일이 비어있다냥!", reference=ctx.message,
                                                   mention_author=False)
                                    print(
                                        f"FAIL: '{command_name}' for ({ctx.author.id}) - Empty zip from API.")
                                    return
                                image_binary = zip_ref.read(image_name)
                            filename = f'nai_declutter_{ctx.message.id}.png'
                            image_file = discord.File(io.BytesIO(image_binary), filename=filename)
                            await ctx.send(content="효과 제거 완료!", file=image_file, reference=ctx.message,
                                           mention_author=False)
                            print(f"SUCCESS: '{command_name}' for ({ctx.author.id}). Image sent.")
                        else:  # API 오류 처리
                            error_text = (await response.read()).decode('utf-8', errors='ignore')
                            await ctx.send(f'제거 실패! 상태코드: {response.status}\n```json\n{error_text[:500]}\n```',
                                           reference=ctx.message, mention_author=False)
                            print(
                                f"FAIL: '{command_name}' for ({ctx.author.id}) - API Error {response.status}: {error_text[:200]}")
            except Exception as e:  # API 요청/처리 중 예외
                if wait_msg: await wait_msg.delete(); wait_msg = None
                await ctx.send(f'제거 중 알 수 없는 오류 발생냥!: {e}', reference=ctx.message, mention_author=False)
                print(f"FAIL: '{command_name}' for ({ctx.author.id}) - Unknown API processing error: {e}")
                traceback.print_exc()
    except Exception as e:  # 최상위 예외
        print(f"CRITICAL FAIL: '{command_name}' for ({ctx.author.id}) - Top-level pre-lock error: {e}")
        traceback.print_exc();
        if wait_msg: await wait_msg.delete()
        try:
            await ctx.send(f"명령어 처리 중 예상치 못한 오류 발생냥!: {e}", reference=ctx.message, mention_author=False)
        except Exception as send_err:
            print(f"CRITICAL FAIL: Could not send error message for '{command_name}'. Reason: {send_err}")
    finally:
        if user_pending_requests.get(user_id, 0) > 0:
            user_pending_requests[user_id] -= 1
            if user_pending_requests[user_id] <= 0: user_pending_requests.pop(user_id, None)


@bot.command(name='편집')  # NovelAI의 colorize 기능을 사용하는 편집
async def edit_image_nai(ctx: commands.Context, *, edit_prompt: str):  # 함수명 변경하여 젬편집과 구분
    g_allowed, g_remain, g_reset = await check_and_increment_global_limit(ctx.author.id)
    if not g_allowed:
        await ctx.send(
            f"오늘 하루 전체 명령어 사용 한도({GLOBAL_DAILY_LIMIT}회)를 다 썼다냥!\n"
            f"초기화: {g_reset.strftime('%H시 %M분')} (KST)",
            reference=ctx.message, mention_author=False
        )
        return
    command_name = ctx.command.name
    print(
        f"INFO: User ({ctx.author.id}) used command '{command_name}' in channel {ctx.channel.id}. Prompt: '{edit_prompt[:50]}...'")
    NOVELAI_EDIT_ENDPOINT = 'https://image.novelai.net/ai/augment-image'
    user_id = ctx.author.id
    wait_msg = None
    try:
        if not NAI_API:
            await ctx.send("봇 설정 오류: NAI_API 키가 설정되지 않았다냥!", reference=ctx.message, mention_author=False)
            print(f"FAIL: '{command_name}' for ({ctx.author.id}) - NAI_API key not set.")
            return
        current_pending = user_pending_requests.get(user_id, 0)
        if current_pending >= MAX_PENDING_PER_USER:
            active_req = 1 if processing_lock.locked() else 0
            await ctx.send(
                f"처리 대기 중인 내 요청이 이미 {current_pending}개 있다냥! (최대 {MAX_PENDING_PER_USER}개)\n(현재 {active_req}개 요청 처리 중)",
                reference=ctx.message, mention_author=False)
            print(f"INFO: '{command_name}' for ({ctx.author.id}) - Request limit reached.")
            return
        if not ctx.message.attachments or len(ctx.message.attachments) > 1:
            await ctx.send("이미지를 하나만 첨부해달라냥!", reference=ctx.message, mention_author=False)
            print(f"FAIL: '{command_name}' for ({ctx.author.id}) - Incorrect attachment count.")
            return
        attachment = ctx.message.attachments[0]
        allowed_extensions = ('.png', '.jpg', '.jpeg', '.webp')
        if not ((attachment.content_type and attachment.content_type.startswith(
                'image/')) or attachment.filename.lower().endswith(allowed_extensions)):
            await ctx.send(f"첨부된 파일 '{attachment.filename}'은 지원하는 이미지 형식이 아니다냥!", reference=ctx.message,
                           mention_author=False)
            print(
                f"FAIL: '{command_name}' for ({ctx.author.id}) - Unsupported file type: {attachment.filename}")
            return
        user_pending_requests[user_id] = current_pending + 1
        processing_status = "다른 요청 처리 중, " if processing_lock.locked() else ""
        wait_msg = await ctx.send(
            f"편집 요청 접수! (`{edit_prompt}`) ({processing_status}내 대기열: {user_pending_requests[user_id]}/{MAX_PENDING_PER_USER})",
            reference=ctx.message, mention_author=False)
        async with processing_lock:
            if wait_msg:
                try:
                    await wait_msg.edit(
                        content=f"내 편집 요청 처리 시작! (`{edit_prompt}`) (내 대기열: {user_pending_requests[user_id]}/{MAX_PENDING_PER_USER})")
                except discord.HTTPException:
                    pass
            processing_attachments_msg = await ctx.send("첨부 파일 처리 중...", reference=ctx.message, mention_author=False)
            image_bytes = await attachment.read()
            try:
                with Image.open(io.BytesIO(image_bytes)) as img:
                    width, height = img.size
                    MAX_DIMENSION_LIMIT = 2560
                    if width > MAX_DIMENSION_LIMIT or height > MAX_DIMENSION_LIMIT:
                        if processing_attachments_msg: await processing_attachments_msg.delete()
                        await ctx.send(f"이미지 크기가 너무 크다냥! (최대 {MAX_DIMENSION_LIMIT}px, 현재: {width}x{height})",
                                       reference=ctx.message, mention_author=False)
                        print(
                            f"FAIL: '{command_name}' for ({ctx.author.id}) - Image too large: {width}x{height}")
                        return
                    MAX_API_SIZE = 1024 if width == height else 1216
                    if width > MAX_API_SIZE or height > MAX_API_SIZE:
                        if wait_msg:
                            try:
                                await wait_msg.edit(content=f"{wait_msg.content}\n이미지 리사이징 중 (최대 {MAX_API_SIZE}px)...")
                            except discord.HTTPException:
                                pass
                        ratio = MAX_API_SIZE / max(width, height)
                        new_width, new_height = int(width * ratio), int(height * ratio)
                        img = img.resize((new_width, new_height), Image.LANCZOS)
                        width, height = new_width, new_height
                        # 편집 명령어는 wait_msg 복구 로직 없음 (원본 기준)
                    img_byte_arr = io.BytesIO();
                    img.save(img_byte_arr, format='PNG');
                    image_bytes = img_byte_arr.getvalue()
            except Exception as img_err:
                if processing_attachments_msg: await processing_attachments_msg.delete()
                await ctx.send(f"이미지 처리 중 오류 발생: {img_err}", reference=ctx.message, mention_author=False)
                print(
                    f"FAIL: '{command_name}' (Pillow processing) for ({ctx.author.id}). Reason: {img_err}")
                return
            base64_encoded_image = base64.b64encode(image_bytes).decode('utf-8')
            if processing_attachments_msg: await processing_attachments_msg.delete()
            headers = {'Authorization': f'Bearer {NAI_API}', 'Content-Type': 'application/json',
                       'Accept': 'application/zip'}
            payload = {"req_type": "colorize", "prompt": edit_prompt, "defry": 5, "width": width, "height": height,
                       "image": base64_encoded_image}
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(NOVELAI_EDIT_ENDPOINT, headers=headers, json=payload) as response:
                        if wait_msg: await wait_msg.delete(); wait_msg = None
                        if response.status == 200:
                            zip_binary = await response.read()
                            with zipfile.ZipFile(io.BytesIO(zip_binary)) as zip_ref:
                                image_name = zip_ref.namelist()[0] if zip_ref.namelist() else None
                                if not image_name:
                                    await ctx.send("편집 실패: API 응답 zip 파일이 비어있다냥!", reference=ctx.message,
                                                   mention_author=False)
                                    print(
                                        f"FAIL: '{command_name}' for ({ctx.author.id}) - Empty zip from API.")
                                    return
                                image_binary = zip_ref.read(image_name)
                            filename = f'nai_edit_{ctx.message.id}.png'
                            image_file = discord.File(io.BytesIO(image_binary), filename=filename)
                            await ctx.send(content=f"이미지 편집 완료! (`{edit_prompt}`)", file=image_file,
                                           reference=ctx.message, mention_author=False)
                            print(f"SUCCESS: '{command_name}' for ({ctx.author.id}). Image sent.")
                        else:
                            error_text = (await response.read()).decode('utf-8', errors='ignore')
                            await ctx.send(f'편집 실패! 상태코드: {response.status}\n```json\n{error_text[:500]}\n```',
                                           reference=ctx.message, mention_author=False)
                            print(
                                f"FAIL: '{command_name}' for ({ctx.author.id}) - API Error {response.status}: {error_text[:200]}")
            except Exception as e:
                if wait_msg: await wait_msg.delete(); wait_msg = None
                await ctx.send(f'편집 중 알 수 없는 오류 발생냥!: {e}', reference=ctx.message, mention_author=False)
                print(f"FAIL: '{command_name}' for ({ctx.author.id}) - Unknown API processing error: {e}")
                traceback.print_exc()
    except Exception as e:
        print(f"CRITICAL FAIL: '{command_name}' for ({ctx.author.id}) - Top-level pre-lock error: {e}")
        traceback.print_exc();
        if wait_msg: await wait_msg.delete()
        try:
            await ctx.send(f"명령어 처리 중 예상치 못한 오류 발생냥!: {e}", reference=ctx.message, mention_author=False)
        except Exception as send_err:
            print(f"CRITICAL FAIL: Could not send error message for '{command_name}'. Reason: {send_err}")
    finally:
        if user_pending_requests.get(user_id, 0) > 0:
            user_pending_requests[user_id] -= 1
            if user_pending_requests[user_id] <= 0: user_pending_requests.pop(user_id, None)


# --- NovelAI Diffusion v5 Precise Reference (&복제26) ---
CLONE26_MODEL = "nai-diffusion-5-curated"
CLONE26_REFERENCE_STRENGTH = 1.0


def _process_v5_reference_image_bytes(raw: bytes) -> dict:
    """이미지를 자르지 않고 Precise Reference 캔버스에 맞춘다."""
    with Image.open(io.BytesIO(raw)) as source:
        oriented = ImageOps.exif_transpose(source)
        rgba = oriented.convert("RGBA")
        # 투명 배경의 캐릭터는 흰 바탕에 합성하고, 비율 차이는 검은 패딩으로 채운다.
        rgb = Image.new("RGB", rgba.size, "white")
        rgb.paste(rgba, (0, 0), rgba.getchannel("A"))
        width, height = rgb.size
        if width > height:
            target_size = (1536, 1024)
        elif height > width:
            target_size = (1024, 1536)
        else:
            target_size = (1472, 1472)

        # 공식 API 규격: 1024x1536 / 1536x1024 / 1472x1472, black padding.
        # https://image.novelai.net/docs/doc.json (director_reference_images)
        resized = ImageOps.contain(rgb, target_size, method=Image.LANCZOS)
        canvas = Image.new("RGB", target_size, "black")
        offset = ((target_size[0] - resized.width) // 2,
                  (target_size[1] - resized.height) // 2)
        canvas.paste(resized, offset)
        buffer = io.BytesIO()
        canvas.save(buffer, format="JPEG", quality=92, optimize=True, subsampling=0)
        image_bytes = buffer.getvalue()

    return {
        "b64": base64.b64encode(image_bytes).decode("ascii"),
        "cache_key": hashlib.sha256(image_bytes).hexdigest(),
        "size": target_size,
    }


def _v5_reference_from_record(reference_data: dict) -> Optional[dict]:
    """재생성용 정규화 이미지와 이전 임시 복제26 기록을 모두 읽는다."""
    image_b64 = reference_data.get("character_ref_b64") or reference_data.get("ref_b64")
    if image_b64:
        image_bytes = base64.b64decode(image_b64, validate=True)
        # 이미 처리된 이미지는 다시 JPEG로 압축하지 않아 재생성 시 그대로 사용된다.
        return {
            "b64": image_b64,
            "cache_key": hashlib.sha256(image_bytes).hexdigest(),
        }

    legacy_b64 = reference_data.get("ssalmuk_input_b64")
    if legacy_b64:
        return _process_v5_reference_image_bytes(base64.b64decode(legacy_b64, validate=True))
    return None


def _build_v5_clone26_payload(original_prompt: str, character_ref: dict) -> tuple[dict, str, str]:
    """2026-11 v5 웹 UI의 Precise Reference 설정으로 생성 요청을 만든다."""
    positive, separator, negative = (original_prompt or "").partition("&부정")
    ignore_style = "무시" in positive
    if ignore_style:
        positive = re.sub(r"\s*무시\s*", " ", positive).strip()
    prompt_for_builder = positive + (f" &부정 {negative}" if separator else "")

    # 크기 키워드, 랜덤 태그, 사용자 부정 프롬프트는 기존 v5 생성 규칙을 공유한다.
    payload, final_prompt, random_tags = _build_v5_26_payload(prompt_for_builder)
    final_prompt = final_prompt.strip(" ,") or "masterpiece"
    payload["input"] = final_prompt
    payload["model"] = CLONE26_MODEL
    parameters = payload["parameters"]
    parameters["v4_prompt"]["caption"]["base_caption"] = final_prompt
    parameters.update({
        "director_reference_descriptions": [{
            "caption": {
                "base_caption": "character" if ignore_style else "character&style",
                "char_captions": [],
            },
            "legacy_uc": False,
        }],
        # 웹 UI의 cache_secret_key는 그 세션에서 업로드한 이미지의 키다.
        # 봇은 문서화된 raw 이미지 필드로 실제 첨부 데이터를 매번 전달한다.
        "director_reference_images": [character_ref["b64"]],
        "director_reference_information_extracted": [1],
        "director_reference_strength_values": [CLONE26_REFERENCE_STRENGTH],
        "director_reference_secondary_strength_values": [0],
        "deliberate_euler_ancestral_bug": False,
        "prefer_brownian": True,
        "noise_schedule": "karras",
        "image_format": "webp",
    })
    # /ai/generate-image의 ZIP 응답을 사용하므로 stream="msgpack"은 넣지 않는다.
    # 브라우저용 recaptcha_token / use_new_shared_trial도 API 토큰 인증에는 넣지 않는다.
    return payload, final_prompt, random_tags


def _extract_v5_clone26_image(zip_binary: bytes, expected_size: tuple[int, int]) -> tuple[bytes, str]:
    """ZIP에서 요청 크기의 생성 이미지를 골라 실제 포맷과 함께 반환한다."""
    format_extensions = {"PNG": "png", "WEBP": "webp", "JPEG": "jpg"}
    with zipfile.ZipFile(io.BytesIO(zip_binary)) as archive:
        names = [name for name in archive.namelist()
                 if name.lower().endswith((".png", ".webp", ".jpg", ".jpeg"))]
        # 메타데이터/원본 이미지가 함께 들어와도 생성 결과를 먼저 찾는다.
        names.sort(key=lambda name: not os.path.basename(name).lower().startswith("image_0."))
        for name in names:
            if os.path.basename(name).lower().startswith(("original", "reference", "input")):
                continue
            image_binary = archive.read(name)
            try:
                with Image.open(io.BytesIO(image_binary)) as generated:
                    extension = format_extensions.get(generated.format)
                    if not extension or generated.size != expected_size:
                        continue
                    generated.verify()
                return image_binary, extension
            except (UnidentifiedImageError, OSError):
                continue
    raise ValueError("응답 ZIP에 요청 해상도의 생성 이미지(PNG/WebP/JPG)가 없다냥!")


async def _generate_clone26(ctx: commands.Context, *, prompt: str,
                            regeneration_reference: Optional[dict] = None):
    """복제26와 재생성이 공유하는 v5 Precise Reference 실행 경로."""
    print(f"INFO: User ({ctx.author.id}) used command '복제26' in channel {ctx.channel.id}.")
    if not NAI_API:
        await ctx.send("봇 설정 오류: NAI_API 키가 없다냥!", reference=ctx.message, mention_author=False)
        return

    # 재생성은 다른 채널에서 바뀐 공유 이미지가 아니라 완료된 요청의 이미지를 사용한다.
    attachments = [] if regeneration_reference is not None else ctx.message.attachments
    if len(attachments) > 1:
        await ctx.send("복제26에는 참조 이미지 한 장만 첨부해달라냥! (PNG/JPG/WebP)",
                       reference=ctx.message, mention_author=False)
        return
    attachment = attachments[0] if attachments else None
    if attachment and not ((attachment.content_type or "").startswith("image/") or
                           attachment.filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))):
        await ctx.send("이미지 파일만 사용할 수 있다냥!", reference=ctx.message, mention_author=False)
        return

    user_id = ctx.author.id
    user_channel_key = (ctx.channel.id, user_id)
    current_pending = user_pending_requests.get(user_id, 0)
    if current_pending >= MAX_PENDING_PER_USER:
        await ctx.send(
            f"처리 대기 중인 내 요청이 이미 {current_pending}개 있다냥! (최대 {MAX_PENDING_PER_USER}개)\n"
            "요청이 처리된 후 다시 시도해달라냥.",
            reference=ctx.message, mention_author=False,
        )
        return

    user_pending_requests[user_id] = current_pending + 1
    wait_msg = None
    try:
        processing_status = "다른 요청 처리 중, " if processing_lock.locked() else ""
        wait_msg = await ctx.send(
            f"복제26 요청 접수! ({processing_status}내 대기열: "
            f"{user_pending_requests[user_id]}/{MAX_PENDING_PER_USER})",
            reference=ctx.message, mention_author=False,
        )
        async with processing_lock:
            raw_image = None
            if regeneration_reference is not None:
                character_ref = _v5_reference_from_record(regeneration_reference)
            elif attachment:
                raw_image = await attachment.read()
                character_ref = _process_v5_reference_image_bytes(raw_image)
            else:
                shared_raw = load_shared_reference(user_id, "character")
                if shared_raw:
                    character_ref = _process_v5_reference_image_bytes(shared_raw)
                else:
                    previous = last_generation_data.get(user_channel_key) or {}
                    character_ref = _v5_reference_from_record(previous.get("reference_data") or {})

            if character_ref is None:
                await wait_msg.edit(content=(
                    "참조 이미지가 없다냥! 처음에는 이미지 한 장을 첨부해서 &복제26을 사용해달라냥.\n"
                    "그 다음부터는 첨부 없이 저장된 캐릭터 이미지를 재사용할 수 있다냥!"
                ))
                return

            # 입력 검증 후 전체 한도 + 복제25/복제26 공통 한도를 한 번씩 적용한다.
            g_allowed, _, g_reset = await check_and_increment_global_limit(user_id, command_name="복제26")
            if not g_allowed:
                await wait_msg.edit(content=(
                    f"오늘 하루 전체 명령어 사용 한도({GLOBAL_DAILY_LIMIT}회)를 다 썼다냥!\n"
                    f"초기화: {g_reset.strftime('%H시 %M분')} (KST)"
                ))
                return
            allowed, remaining, reset_at = await check_and_increment_clone_limit(
                user_id, command_name="복제26"
            )
            cap = await get_clone_daily_cap(user_id)
            if not allowed:
                await wait_msg.edit(content=(
                    f"오늘 &복제25 / &복제26의 복제 공통 한도({cap}회)를 다 썼다냥!\n"
                    f"초기화: {reset_at.strftime('%H시 %M분')} (KST)\n"
                    "사용량은 `&한도` 명령어로 확인해달라냥!"
                ))
                return

            payload, _, random_tags = _build_v5_clone26_payload(prompt, character_ref)
            parameters = payload["parameters"]
            output_size = (parameters["width"], parameters["height"])
            reference_type = parameters["director_reference_descriptions"][0]["caption"]["base_caption"]
            reference_notice = "캐릭터" if reference_type == "character" else "캐릭터 + 그림체"
            await wait_msg.edit(content=(
                f"v5 Precise Reference로 복제 중이다냥! ({reference_notice}, "
                f"{output_size[0]}×{output_size[1]})"
            ))

            # multipart의 boundary/Content-Type은 aiohttp가 request(blob)에 맞춰 지정한다.
            headers = {"Authorization": f"Bearer {NAI_API}", "Accept": "application/zip"}
            form = aiohttp.FormData()
            form.add_field("request", json.dumps(payload, ensure_ascii=False),
                           filename="blob", content_type="application/json")
            timeout = aiohttp.ClientTimeout(total=300)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post("https://image.novelai.net/ai/generate-image",
                                        headers=headers, data=form) as response:
                    if response.status not in (200, 201):
                        if response.status == 429:
                            await wait_msg.edit(content="복제26 실패: API 동시 생성 제한(429)이다냥!")
                        else:
                            error_text = await response.text()
                            await wait_msg.edit(content=(
                                f"복제26 생성 실패냥! 상태코드: {response.status}\n"
                                f"```json\n{error_text[:800]}\n```"
                            ))
                        return
                    zip_binary = await response.read()

            image_binary, extension = _extract_v5_clone26_image(zip_binary, output_size)
            completion_notice = (
                (f"랜덤으로 추가된 프롬프트 : `{random_tags}`\n" if random_tags else "")
                + f"✅ v5 복제 완료다냥! ({reference_notice}, 남은 복제 공통: {remaining}/{cap})"
            )
            if remaining == 0:
                completion_notice += "\n오늘 복제 공통 한도를 모두 사용했다냥! `&한도`로 확인해달라냥!"
            await ctx.send(
                content=completion_notice,
                file=discord.File(io.BytesIO(image_binary), filename=f"clone26_{ctx.message.id}.{extension}"),
                reference=ctx.message, mention_author=False,
            )

            # 완료된 요청만 기억한다. API 실패 시 이전 이미지/재생성 기록을 보존한다.
            if attachment:
                save_shared_reference(user_id, "character", raw_image)
                save_shared_reference(user_id, "style", b"")
            last_generation_data[user_channel_key] = {
                "command_name": "복제26",
                "original_discord_prompt": prompt,
                "reference_data": {
                    "character_ref_b64": character_ref["b64"],
                    "character_ref_cache_key": character_ref["cache_key"],
                    "ref_b64": character_ref["b64"],
                    "ref_cache_key": character_ref["cache_key"],
                    "using_split_refs": False,
                },
            }
            try:
                await wait_msg.delete()
            except discord.HTTPException:
                pass
            print(f"SUCCESS: '복제26' for ({user_id}).")
    except Exception as error:
        traceback.print_exc()
        try:
            message = f"복제26 처리 중 오류가 발생했다냥!: {error}"[:1900]
            if wait_msg:
                await wait_msg.edit(content=message)
            else:
                await ctx.send(message, reference=ctx.message, mention_author=False)
        except discord.HTTPException:
            pass
    finally:
        pending = max(0, user_pending_requests.get(user_id, 1) - 1)
        if pending:
            user_pending_requests[user_id] = pending
        else:
            user_pending_requests.pop(user_id, None)


@bot.command(name='복제26')
async def clone_character_v5(ctx: commands.Context, *, prompt: str = ""):
    """첨부 이미지 한 장의 캐릭터/그림체를 v5 Precise Reference로 복제한다."""
    await _generate_clone26(ctx, prompt=prompt)

@bot.command(name='인페인트', aliases=['채우기'])
async def inpaint_image_nai(ctx: commands.Context, *, prompt: str):
    g_allowed, g_remain, g_reset = await check_and_increment_global_limit(ctx.author.id)
    if not g_allowed:
        await ctx.send(
            f"오늘 하루 전체 명령어 사용 한도({GLOBAL_DAILY_LIMIT}회)를 다 썼다냥!\n"
            f"초기화: {g_reset.strftime('%H시 %M분')} (KST)",
            reference=ctx.message, mention_author=False
        )
        return
    from PIL import Image, ImageFilter, ImageOps
    import io, base64, zipfile, random, traceback, aiohttp, math

    command_name = ctx.command.name
    print(f"INFO: User ({ctx.author.id}) used command '{command_name}'. Prompt: '{prompt[:80]}...'")

    # 전역 상태
    global user_pending_requests, processing_lock, NAI_API, MAX_PENDING_PER_USER, last_generation_data

    if not NAI_API:
        await ctx.send("봇 설정 오류: NAI_API 키가 없다냥!", reference=ctx.message, mention_author=False)
        return

    MODEL_INPAINT = "nai-diffusion-4-5-full-inpainting"
    API_URL = "https://image.novelai.net/ai/generate-image"
    headers = {
        "Authorization": f"Bearer {NAI_API}",
        "Content-Type": "application/json",
        "Accept": "application/zip",
    }

    ALLOWED_SIZES = {(1216, 832), (832, 1216), (1024, 1024)}

    default_uc_v45 = "{{{{{{{{{{worst quality, bad quality, lowres}}}}}}}}}}, bad anatomy, {{{{bad hands}}}}, {artist:bkub}, displeasing, very displeasing, bad perspective, bad proportions, bad aspect ratio, bad face, long face, bad teeth, bad neck, long neck, bad arm, bad ass, bad leg, bad feet, bad reflection, bad shadow, bad link, bad source, wrong hand, wrong feet, missing limb, missing eye, missing tooth, missing ear, missing finger, extra faces, extra eyes, extra eyebrows, extra mouth, extra tongue, extra teeth, extra ears, extra breasts, extra arms, extra hands, extra legs, extra digits, fewer digits, cropped head, cropped torso, cropped shoulders, cropped arms, cropped legs, mutation, deformed, disfigured, unfinished, chromatic aberration, text, error, jpeg artifacts, watermark, scan, scan artifacts, ugly man}}}, {{bald}}, {{bald hair}}"
    base_caption_suffix = ",amazing quality, very aesthetic, absurdres, masterpiece, highres, hyper detailed"

    user_negative_prompt = ""
    if "&부정" in prompt:
        parts = prompt.split("&부정", 1)
        prompt = parts[0].strip()
        user_negative_prompt = parts[1].strip()

    final_uc = user_negative_prompt if user_negative_prompt else default_uc_v45
    prompt, _random_tags = apply_random_prompt_tags(prompt)
    assembled_caption = (prompt.strip() if prompt.strip() else "masterpiece") + base_caption_suffix

    def _b64_png(pil_img: Image.Image) -> str:
        buf = io.BytesIO()
        pil_img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("utf-8")

    def _b64_bytes(raw: bytes) -> str:
        return base64.b64encode(raw).decode("utf-8")

    def _bytes_from_b64(b64s: str) -> bytes:
        return base64.b64decode(b64s.encode("utf-8"))

    # --- 핵심: 마스크 = (투명/반투명 전부) + 8px 그리드 스냅 + pad(px→block dilation) ---
    def _mask_from_alpha_rgba(img_rgba: Image.Image) -> Image.Image:
        alpha = img_rgba.getchannel("A")
        # alpha < 255 이면 전부 인페인트 대상(0.1이라도 투명/반투명 포함)
        mask = alpha.point(lambda a: 255 if a < 255 else 0)
        return mask  # mode 'L'

    def _snap_and_pad_mask(mask_l: Image.Image, pad_px: int, tile: int = 8) -> Image.Image:
        w, h = mask_l.size
        mw, mh = w // tile, h // tile
        if mw <= 0 or mh <= 0:
            return mask_l.point(lambda x: 255 if x > 0 else 0)

        # 1) 이진화
        m = mask_l.point(lambda x: 255 if x > 0 else 0)

        # 2) 8px 블록으로 스냅 (down/up NEAREST)
        m_small = m.resize((mw, mh), resample=Image.NEAREST)
        m_small = m_small.point(lambda x: 255 if x > 0 else 0)

        # 3) 패딩: px→block
        pad_blocks = max(0, math.ceil(pad_px / tile))
        if pad_blocks > 0:
            k = 2 * pad_blocks + 1
            m_small = m_small.filter(ImageFilter.MaxFilter(k))
            m_small = m_small.point(lambda x: 255 if x > 0 else 0)

        # 4) 원본 크기로 복원
        m_big = m_small.resize((w, h), resample=Image.NEAREST)
        m_big = m_big.point(lambda x: 255 if x > 0 else 0)
        return m_big

    user_id = ctx.author.id
    user_channel_key = (ctx.channel.id, user_id)

    wait_msg = None

    # ---- 튜닝 파라미터 ----
    PAD_PX = 8  # ✅ (투명/반투명) + 8px 이상 패딩
    HOLE_BLUR = 16  # 베이스 이미지 구멍 채움용 블러(검정/투명 구멍 방지)
    FEATHER = 0  # 후처리 합성 블렌딩(원하면 2~4). 지금은 생성본 그대로 전달.
    # ----------------------

    # 첨부 없을 때 재사용 여부
    reused_reference = False

    try:
        current_pending = user_pending_requests.get(user_id, 0)
        if current_pending >= MAX_PENDING_PER_USER:
            await ctx.send(f"대기열이 꽉 찼다냥! ({current_pending}개)", reference=ctx.message, mention_author=False)
            return

        user_pending_requests[user_id] = current_pending + 1

        processing_status = "다른 작업 중, " if processing_lock.locked() else ""
        wait_msg = await ctx.send(
            f"인페인트 요청 접수! (`{prompt}`) ({processing_status}대기열: {user_pending_requests[user_id]})",
            reference=ctx.message, mention_author=False
        )

        async with processing_lock:
            if wait_msg:
                try:
                    await wait_msg.edit(content=f"인페인트 처리 시작! (`{prompt}`)")
                except:
                    pass

            processing_msg = await ctx.send("이미지 처리 중...", reference=ctx.message, mention_author=False)

            # ─────────────────────────────────────────
            # 0) 입력 PNG 확보: (A) 첨부 or (B) 최근 인페인트 입력 재사용
            # ─────────────────────────────────────────
            png_bytes: bytes | None = None

            attachment = None
            if ctx.message.attachments:
                # PNG 하나만 허용
                if len(ctx.message.attachments) > 1:
                    await processing_msg.delete()
                    await ctx.send("PNG 이미지는 하나만 보내달라냥!", reference=ctx.message, mention_author=False)
                    return
                attachment = ctx.message.attachments[0]

            if attachment:
                if not attachment.filename.lower().endswith(".png"):
                    await processing_msg.delete()
                    await ctx.send("꼭 **PNG 파일**이어야 한다냥!", reference=ctx.message, mention_author=False)
                    return
                png_bytes = await attachment.read()
            else:
                # ✅ 복제처럼: 첨부 없으면 최근 레퍼런스(=인페인트 입력 PNG) 재사용
                last_data = last_generation_data.get(user_channel_key)
                b64 = None
                shared_inpaint = load_shared_reference(user_id, "inpaint")
                if last_data and isinstance(last_data, dict):
                    ref = last_data.get("reference_data") or {}
                    b64 = ref.get("inpaint_png_b64")
                if not b64 and not shared_inpaint:
                    await processing_msg.delete()
                    await ctx.send(
                        "이번엔 첨부된 PNG가 없다냥! 처음 한 번은 투명/반투명 PNG를 첨부해줘야 하고,\n"
                        "그 다음부터는 첨부 없이 이전 레퍼런스를 재사용할 수 있다냥!",
                        reference=ctx.message, mention_author=False
                    )
                    return
                png_bytes = shared_inpaint or _bytes_from_b64(b64)
                reused_reference = True

            # ─────────────────────────────────────────
            # 1) PNG 전처리 + 마스크 생성
            # ─────────────────────────────────────────
            try:
                with Image.open(io.BytesIO(png_bytes)) as img:
                    if img.mode != "RGBA":
                        img = img.convert("RGBA")

                    width, height = img.size
                    if (width, height) not in ALLOWED_SIZES:
                        await processing_msg.delete()
                        allowed_str = ", ".join([f"{w}x{h}" for (w, h) in sorted(ALLOWED_SIZES)])
                        await ctx.send(
                            f"이 인페인트는 아래 해상도만 지원한다냥!\n`{allowed_str}`\n현재: `{width}x{height}`",
                            reference=ctx.message, mention_author=False
                        )
                        return

                    original_rgba = img.copy()

                    mask_core = _mask_from_alpha_rgba(original_rgba)
                    if mask_core.getbbox() is None:
                        await processing_msg.delete()
                        await ctx.send("인페인트할(투명/반투명) 영역이 없는 PNG 같다냥!", reference=ctx.message, mention_author=False)
                        return

                    # 서버로 보낼 마스크 = (투명/반투명) + PAD + 8px 스냅
                    mask_send = _snap_and_pad_mask(mask_core, pad_px=PAD_PX, tile=8)

                    # 베이스 이미지: 마스크 영역을 블러로 채워서 '검정/투명 구멍' 컨디션 제거
                    original_rgb = original_rgba.convert("RGB")
                    blurred_rgb = original_rgb.filter(ImageFilter.GaussianBlur(HOLE_BLUR))
                    base_rgb = Image.composite(blurred_rgb, original_rgb, mask_send)

                    base64_image = _b64_png(base_rgb)
                    base64_mask = _b64_png(mask_send)

                    save_shared_reference(user_id, "inpaint", png_bytes)
                    # ✅ 여기서 "최근 인페인트 입력 PNG" 저장(다음에 첨부 없이 재사용 가능)
                    last_generation_data[user_channel_key] = {
                        "command_name": "인페인트",
                        "original_discord_prompt": prompt,
                        "reference_data": {
                            "inpaint_png_b64": _b64_bytes(png_bytes)
                        }
                    }

            except Exception as e:
                await processing_msg.delete()
                await ctx.send(f"이미지 전처리 실패냥: {e}", reference=ctx.message, mention_author=False)
                return
            finally:
                try:
                    await processing_msg.delete()
                except:
                    pass

            # ─────────────────────────────────────────
            # 2) NAI 인페인트 요청
            # ─────────────────────────────────────────
            seed = random.randint(0, 2 ** 32 - 1)

            payload = {
                "action": "infill",
                "model": MODEL_INPAINT,
                "parameters": {
                    "width": width,
                    "height": height,

                    "params_version": 3,
                    "scale": 6,
                    "sampler": "k_euler_ancestral",
                    "steps": 28,
                    "seed": seed,
                    "extra_noise_seed": seed,
                    "n_samples": 1,

                    "noise_schedule": "karras",
                    "cfg_rescale": 0.3,
                    "qualityToggle": True,
                    "ucPreset": 0,

                    "image": base64_image,
                    "mask": base64_mask,

                    "inpaintImg2ImgStrength": 1.0,
                    "img2img": {"strength": 1.0, "color_correct": True},

                    "add_original_image": True,

                    "v4_prompt": {
                        "caption": {"base_caption": assembled_caption, "char_captions": []},
                        "use_coords": False,
                        "use_order": True,
                    },
                    "v4_negative_prompt": {
                        "caption": {"base_caption": final_uc, "char_captions": []},
                        "legacy_uc": False,
                    },
                }
            }

            try:
                timeout = aiohttp.ClientTimeout(total=300)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(API_URL, headers=headers, json=payload) as response:
                        if wait_msg:
                            try:
                                await wait_msg.delete()
                            except:
                                pass
                            wait_msg = None

                        if response.status != 200:
                            error_text = await response.text()
                            await ctx.send(
                                f"실패했다냥! 상태코드: {response.status}\n```json\n{error_text[:800]}\n```",
                                reference=ctx.message, mention_author=False
                            )
                            return

                        zip_binary = await response.read()

                # zip에서 가장 큰 PNG를 결과로 선택 (add_original_image 섞여와도 안전)
                with zipfile.ZipFile(io.BytesIO(zip_binary)) as zip_ref:
                    names = [n for n in zip_ref.namelist() if n.lower().endswith(".png")]
                    if not names:
                        await ctx.send("인페인트 실패: 응답 zip에 PNG가 없다냥!", reference=ctx.message, mention_author=False)
                        return

                    best_name, best_data, best_size = None, None, -1
                    for n in names:
                        data = zip_ref.read(n)
                        if len(data) > best_size:
                            best_size = len(data)
                            best_name = n
                            best_data = data

                generated_rgba = Image.open(io.BytesIO(best_data)).convert("RGBA")

                # 기본 방침: 생성본 그대로 보내기(원본 강제합성이 경계 문제를 만들었던 케이스가 많음)
                if FEATHER and FEATHER > 0:
                    blend_mask = mask_send.filter(ImageFilter.GaussianBlur(FEATHER))
                    final_img = Image.composite(generated_rgba, original_rgba, blend_mask)
                else:
                    final_img = generated_rgba

                final_buffer = io.BytesIO()
                final_img.save(final_buffer, format="PNG")
                final_buffer.seek(0)

                filename = f"nai_inpaint_{ctx.message.id}.png"
                extra = " (이전 레퍼런스 재사용)" if reused_reference else ""
                await ctx.send(
                    content=f"인페인트 완료!{extra} (`{prompt}`)",
                    file=discord.File(final_buffer, filename=filename),
                    reference=ctx.message,
                    mention_author=False
                )
                print(f"SUCCESS: '인페인트' for ({ctx.author.id}).")

            except Exception as e:
                await ctx.send(f"API/후처리 오류냥!: {e}", reference=ctx.message, mention_author=False)
                traceback.print_exc()

    except Exception as e:
        if wait_msg:
            try:
                await wait_msg.delete()
            except:
                pass
        await ctx.send(f"알 수 없는 오류냥: {e}", reference=ctx.message, mention_author=False)
        traceback.print_exc()

    finally:
        if user_id in user_pending_requests:
            user_pending_requests[user_id] -= 1
            if user_pending_requests[user_id] <= 0:
                user_pending_requests.pop(user_id, None)


@bot.command(name='한도', aliases=['잔여', '횟수'])
async def check_limits(ctx):
    print(f"INFO: User ({ctx.author.id}) used command '한도'")

    clone_used, generate26_used, global_used, reset_at = await get_user_limits(ctx.author.id)

    clone_cap = await get_clone_daily_cap(ctx.author.id)
    clone_remain = max(0, clone_cap - clone_used)
    generate26_cap = get_generate26_daily_limit()
    generate26_remain = max(0, generate26_cap - generate26_used)
    global_remain = max(0, GLOBAL_DAILY_LIMIT - global_used)
    reset_str = reset_at.strftime('%H시 %M분')

    embed = discord.Embed(title="📊 일일 사용량 한도 조회", color=0xFFFFFF)
    embed.add_field(name="전체 명령어", value=f"{global_remain} / {GLOBAL_DAILY_LIMIT}회 남음\n(사용: {global_used}회)",
                    inline=True)
    embed.add_field(
        name="복제25 / 복제26 공통",
        value=f"{clone_remain} / {clone_cap}회 남음\n(사용: {clone_used}회, 복제인페인트 포함)",
        inline=True
    )
    embed.add_field(
        name="생성26 전용",
        value=f"{generate26_remain} / {generate26_cap}회 남음\n(사용: {generate26_used}회)",
        inline=True
    )
    embed.set_footer(text=f"※ 매일 자정 {reset_str} (KST)에 초기화된다냥!")

    await ctx.reply(embed=embed, mention_author=False)


@bot.command(name='디버그', aliases=['debug', '총사용량', '주간통계'])
async def debug_usage(ctx):
    print(f"INFO: User ({ctx.author.id}) used command '디버그'")
    stats, started_at = await get_weekly_usage_stats()
    embed = discord.Embed(title="📊 명령어 사용량 통계 (최근 7일)", color=0xFFFFFF)
    groups = (
        ("global", "1. 전체 명령어 사용량"),
        ("clone", "2. 복제 사용량 (복제25/복제26)"),
        ("generate", "3. 생성 사용량 (생성23~생성26)"),
    )
    today = next(iter(stats))
    for field, title in groups:
        lines = []
        for date_str, counts in stats.items():
            prefix = "👉" if date_str == today else "▪️"
            count = counts[field]
            value = "— (집계 전)" if count is None else f"`{count}`회"
            lines.append(f"{prefix} **{date_str}**: {value}")
        embed.add_field(name=title, value="\n".join(lines), inline=False)
    embed.set_footer(text=(
        f"집계 시작: {started_at.strftime('%Y-%m-%d %H:%M:%S')} (KST) · 시작일은 해당 시각 이후 집계\n"
        "전체 한도가 차감된 요청 기준 · 재생성은 원래 명령어에 합산"
    ))
    await ctx.reply(embed=embed, mention_author=False)


async def get_image_attachment_data(attachments: List[discord.Attachment]) -> List[Dict[str, any]]:
    """Gemini용 첨부파일 다운로더 (MIME 타입에 좀 더 관대함)"""
    result = []
    supported_image_mimes = ["image/png", "image/jpeg", "image/webp", "image/heic", "image/heif"]
    async with aiohttp.ClientSession() as session:
        for attachment in attachments:
            # print(f"Checking attachment for image editing: {attachment.filename} ({attachment.content_type})") # 제거
            file_ext = os.path.splitext(attachment.filename.lower())[1]
            is_image = attachment.content_type in supported_image_mimes or \
                       (attachment.content_type is None and file_ext in ['.png', '.jpg', '.jpeg', '.webp', '.heic',
                                                                         '.heif'])

            if attachment.size > 20 * 1024 * 1024:
                # print(f"  -> Skipped: File too large ({attachment.size / (1024 * 1024):.2f} MB)") # 제거
                continue
            if not is_image:
                # print(f"  -> Skipped: Not a supported image type ({attachment.content_type or file_ext})") # 제거
                continue
            if not attachment.url:
                # print(f"  -> Skipped: No URL found for {attachment.filename}") # 제거
                continue

            try:
                async with session.get(attachment.url) as resp:
                    if resp.status == 200:
                        attachment_data = await resp.read()
                        mime_type = attachment.content_type if attachment.content_type in supported_image_mimes else f"image/{file_ext.strip('.')}"
                        if mime_type == "image/": mime_type = "application/octet-stream"  # 매우 일반적인 폴백
                        # print(f"  -> Success: Downloaded {attachment.filename} ({mime_type}, {len(attachment_data)} bytes)") # 제거
                        result.append({"mime_type": mime_type, "data": attachment_data})
                    # else: print(f"  -> Failed: Download failed (HTTP status: {resp.status}) for {attachment.filename}") # 제거
            except Exception as e:
                print(f"Warning: Error processing attachment {attachment.filename} for Gemini: {e}")  # 실패 시 로그
    return result


def generate_upload_id(length=10):
    return secrets.token_hex(length // 2 + length % 2)[:length]


async def upload_file_to_gradio(session: aiohttp.ClientSession, file_bytes: bytes, original_filename: str,
                                mime_type: str) -> dict | None:
    upload_id = generate_upload_id()
    upload_url_with_id = f"{SPACE_BASE}{UPLOAD_BASE_ENDPOINT}?upload_id={upload_id}"
    form_data = aiohttp.FormData()
    form_data.add_field('files', file_bytes, filename=original_filename, content_type=mime_type)
    # print(f"Attempting file upload to: {upload_url_with_id} (filename: {original_filename})") # 제거
    try:
        async with session.post(upload_url_with_id, data=form_data, headers=HEADERS_BASE, timeout=60) as r:
            # response_text = await r.text() # 제거 (필요 시 에러 로깅에 포함)
            # print(f"Upload URL: {upload_url_with_id}, Status: {r.status}, Response: {response_text[:500]}") # 제거
            if r.status == 200:
                json_response = await r.json(content_type=None)
                if isinstance(json_response, list) and len(json_response) > 0:
                    uploaded_file_path_on_server = None
                    if isinstance(json_response[0], str):
                        uploaded_file_path_on_server = json_response[0]
                    elif isinstance(json_response[0], dict) and "path" in json_response[0]:
                        uploaded_file_path_on_server = json_response[0]["path"]

                    if uploaded_file_path_on_server:
                        file_info_object = {"meta": {"_type": "gradio.FileData"}, "mime_type": mime_type,
                                            "orig_name": original_filename, "path": uploaded_file_path_on_server,
                                            "size": len(file_bytes),
                                            "url": f"{SPACE_BASE}/file={uploaded_file_path_on_server}"}
                        # print(f"Constructed file_info_object: {str(file_info_object)[:300]}") # 제거
                        return file_info_object
                # print(f"Unexpected format in /upload response list: {json_response}") # 제거 (에러 로깅으로 대체)
                print(
                    f"ERROR: Gradio upload failed - Unexpected response format. Status: {r.status}, Response: {await r.text()[:200]}")
                return None
            print(f"ERROR: Gradio upload failed - Status: {r.status}, Response: {await r.text()[:200]}")
            return None
    except Exception as e:
        print(f"ERROR: Gradio file upload to {upload_url_with_id} failed. Reason: {e}")
        traceback.print_exc()
        return None


def make_api_payload(uploaded_file_object: dict, session_hash_to_use: str) -> dict:
    """Gradio /queue/join API 호출용 페이로드 생성 (업스케일용)"""
    payload = {"data": [uploaded_file_object, "2x"], "event_data": None, "fn_index": 0,
               "session_hash": session_hash_to_use, "trigger_id": 12}  # trigger_id는 Gradio 앱 설정에 따라 다를 수 있음
    # print(f"Generated API payload for {API_JOIN_QUEUE_ENDPOINT}: {str(payload)[:300]}...") # 제거
    return payload


async def call_upscale_api_with_queue(session: aiohttp.ClientSession, initial_payload_data: dict) -> tuple[
                                                                                                         bytes, str] | None:
    join_payload = initial_payload_data
    session_hash_for_sse = join_payload.get("session_hash")
    if not session_hash_for_sse: raise ValueError("session_hash is missing in the payload for queue join.")

    join_url = SPACE_BASE + API_JOIN_QUEUE_ENDPOINT
    data_url = f"{SPACE_BASE}{API_QUEUE_DATA_ENDPOINT}?session_hash={session_hash_for_sse}"

    # print(f"Attempting to join queue: {join_url}") # 제거
    async with session.post(join_url, headers=HEADERS_BASE, json=join_payload, timeout=30) as r_join:
        # response_text_join = await r_join.text() # 제거
        # print(f"Join Queue URL: {join_url}, Status: {r_join.status}, Response: {response_text_join[:500]}") # 제거
        if r_join.status != 200:
            raise RuntimeError(
                f"Failed to join Gradio queue. Status: {r_join.status}, Response: {await r_join.text()[:200]}")

    # print(f"Listening for SSE data from: {data_url}") # 제거
    timeout = aiohttp.ClientTimeout(total=300, connect=30, sock_read=270)
    async with session.get(data_url, headers=SSE_HEADERS, timeout=timeout) as r_data:
        if r_data.status != 200:
            raise RuntimeError(
                f"Failed to connect to SSE data stream. Status: {r_data.status}, Response: {await r_data.text()[:200]}")

        async for line_bytes in r_data.content:
            line = line_bytes.decode('utf-8').strip()
            if not line: continue
            # print(f"SSE Received line: {line}") # 너무 상세하므로 제거
            if line.startswith("data:"):
                message_data_str = line[len("data:"):].strip()
                try:
                    message_json = json.loads(message_data_str)
                    msg_type = message_json.get("msg")
                    if msg_type == "process_completed":
                        # print("SSE: Processing completed!") # 제거
                        output_data = message_json.get("output", {}).get("data")
                        if output_data and isinstance(output_data, list) and len(output_data) > 0:
                            result_item = output_data[0]
                            if isinstance(result_item, str) and result_item.startswith("data:image"):  # Base64 데이터
                                # print("SSE: Result is Base64 image data.") # 제거
                                header_part, b64_image_data = result_item.split(",", 1)
                                result_mime_type = header_part.split(":")[1].split(";")[0]
                                image_bytes = base64.b64decode(b64_image_data)
                                return image_bytes, result_mime_type
                            elif isinstance(result_item, dict) and "url" in result_item:  # 파일 URL 객체
                                image_file_url = result_item["url"]
                                # print(f"SSE: Result is a file object. URL: {image_file_url}") # 제거
                                if not image_file_url.startswith("http"):  # 상대 URL 처리
                                    image_file_url = f"{SPACE_BASE}{'/file=' if not image_file_url.startswith('/') else ''}{image_file_url.lstrip('/')}"
                                # print(f"SSE: Attempting to download image from resolved URL: {image_file_url}") # 제거
                                async with session.get(image_file_url, headers=HEADERS_BASE, timeout=60) as img_r:
                                    if img_r.status == 200:
                                        # print("SSE: Image downloaded successfully.") # 제거
                                        downloaded_image_bytes = await img_r.read()
                                        result_mime_type = img_r.headers.get('Content-Type', 'image/webp')
                                        if "mime_type" in result_item and result_item["mime_type"]:
                                            result_mime_type = result_item["mime_type"]
                                        elif "name" in result_item and isinstance(result_item["name"], str):
                                            if result_item["name"].lower().endswith(".png"):
                                                result_mime_type = "image/png"
                                            elif result_item["name"].lower().endswith((".jpg", ".jpeg")):
                                                result_mime_type = "image/jpeg"
                                        # print(f"SSE: Downloaded image MIME type: {result_mime_type}") # 제거
                                        return downloaded_image_bytes, result_mime_type
                                    else:
                                        raise RuntimeError(
                                            f"Failed to download result image from {image_file_url}. Status: {img_r.status}, Response: {await img_r.text()[:200]}")
                            else:
                                raise ValueError(f"Unexpected result format in process_completed: {result_item}")
                        else:
                            raise ValueError("No data found in process_completed output.")
                except json.JSONDecodeError:
                    print(f"SSE: Failed to decode JSON from message: {message_data_str}")  # 에러만 로깅
                except Exception as e:
                    print(f"SSE: Error processing message: {e}")  # 에러만 로깅
                    if msg_type == "process_completed": raise  # 완료 메시지 처리 중 오류 시 재발생
    raise asyncio.TimeoutError(f"Did not receive 'process_completed' message from SSE stream within timeout.")


# ===================================================================
#      [ &확대 ] 4배 업스케일 (자동 축소 기능 포함, 최종)
# ===================================================================
@bot.command(name='확대')
async def upscale_nai_image_attached(ctx: commands.Context):
    g_allowed, g_remain, g_reset = await check_and_increment_global_limit(ctx.author.id)
    if not g_allowed:
        await ctx.send(
            f"오늘 하루 전체 명령어 사용 한도({GLOBAL_DAILY_LIMIT}회)를 다 썼다냥!\n"
            f"초기화: {g_reset.strftime('%H시 %M분')} (KST)",
            reference=ctx.message, mention_author=False
        )
        return
    """
    첨부된 이미지를 '4배' 업스케일합니다. API의 곱셈 로직과
    사용자가 요청한 '자동 축소' 기능을 모두 포함합니다.
    """
    command_name = ctx.command.name
    print(f"INFO: User ({ctx.author.id}) used command '{command_name}' in channel {ctx.channel.id}.")

    NOVELAI_UPSCALE_ENDPOINT = 'https://api.novelai.net/ai/upscale'

    global processing_lock, user_pending_requests, NAI_API
    user_id = ctx.author.id
    wait_msg = None

    if not NAI_API:
        await ctx.send("봇 설정 오류: NAI_API 키가 설정되지 않았다냥!", reference=ctx.message, mention_author=False)
        return

    if not ctx.message.attachments or len(ctx.message.attachments) > 1:
        await ctx.send("확대할 이미지를 하나만 첨부해줘야 한다냥!", reference=ctx.message, mention_author=False)
        return

    attachment = ctx.message.attachments[0]
    if not attachment.content_type or not attachment.content_type.startswith('image/'):
        await ctx.send(f"첨부된 파일 '{attachment.filename}'은 이미지 파일이 아닌 것 같다냥!", reference=ctx.message,
                       mention_author=False)
        return

    try:
        current_pending = user_pending_requests.get(user_id, 0)
        if current_pending >= MAX_PENDING_PER_USER:
            await ctx.send(f"처리 대기 중인 내 요청이 이미 {current_pending}개 있다냥!", reference=ctx.message, mention_author=False)
            return

        user_pending_requests[user_id] = current_pending + 1
        processing_status = "다른 요청 처리 중, " if processing_lock.locked() else ""
        wait_msg = await ctx.send(
            f"4배 확대 요청 접수! ({processing_status}내 대기열: {user_pending_requests[user_id]}/{MAX_PENDING_PER_USER})",
            reference=ctx.message, mention_author=False)

        async with processing_lock:
            if wait_msg:
                try:
                    await wait_msg.edit(content=f"내 4배 확대 요청 처리 시작!")
                except discord.HTTPException:
                    pass

            image_bytes = await attachment.read()

            try:
                with Image.open(io.BytesIO(image_bytes)) as img:
                    original_width, original_height = img.size

                    # --- [핵심] 이미지가 크면 거부 대신 '자동 축소' ---
                    MAX_INPUT_DIMENSION = 512
                    image_to_send_bytes = image_bytes
                    width_to_process = original_width
                    height_to_process = original_height

                    if original_width > MAX_INPUT_DIMENSION or original_height > MAX_INPUT_DIMENSION:
                        if wait_msg:
                            try:
                                await wait_msg.edit(content="이미지가 너무 커서 우선 작게 줄이는 중이다냥...")
                            except discord.HTTPException:
                                pass

                        ratio = MAX_INPUT_DIMENSION / max(original_width, original_height)
                        width_to_process = int(original_width * ratio)
                        height_to_process = int(original_height * ratio)

                        img_resized = img.resize((width_to_process, height_to_process), Image.Resampling.LANCZOS)

                        buffer = io.BytesIO()
                        img_resized.save(buffer, format='PNG')
                        image_to_send_bytes = buffer.getvalue()

                    # API의 곱셈 로직에 맞춰 2배 크기만 계산
                    base_target_width = width_to_process * 2
                    base_target_height = height_to_process * 2

            except UnidentifiedImageError:
                await wait_msg.edit(content="이 파일은 이미지 파일이 아닌 것 같다냥!")
                return

            base64_image = base64.b64encode(image_to_send_bytes).decode('utf-8')

            # API의 실제 곱셈 동작에 맞춘 페이로드
            payload = {
                "image": base64_image,
                "scale": 2,  # 추가 배율 2
                "width": base_target_width,  # 기본 배율 2
                "height": base_target_height  # 기본 배율 2
            }

            headers = {'Authorization': f'Bearer {NAI_API}', 'Content-Type': 'application/json',
                       'Accept': 'application/zip'}

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(NOVELAI_UPSCALE_ENDPOINT, headers=headers, json=payload,
                                            timeout=300) as response:
                        if wait_msg: await wait_msg.delete(); wait_msg = None

                        if response.status == 200:
                            zip_binary = await response.read()
                            with zipfile.ZipFile(io.BytesIO(zip_binary)) as zip_ref:
                                image_name = zip_ref.namelist()[0]
                                image_binary = zip_ref.read(image_name)
                            filename = f'upscaled_4x_{ctx.message.id}.png'
                            image_file = discord.File(io.BytesIO(image_binary), filename=filename)
                            await ctx.send(content="냥냥! 4배 확대를 완료했다냥!", file=image_file, reference=ctx.message,
                                           mention_author=False)
                        else:
                            error_text = await response.text()
                            await ctx.send(f'확대 실패! 상태코드: {response.status}\n```json\n{error_text[:500]}\n```',
                                           reference=ctx.message, mention_author=False)
            except Exception as e:
                if wait_msg: await wait_msg.delete(); wait_msg = None
                await ctx.send(f'확대 중 알 수 없는 오류 발생냥!: {e}', reference=ctx.message, mention_author=False)

    except Exception as e:
        print(f"CRITICAL FAIL: '{command_name}' for ({ctx.author.id}) - Top-level error: {e}")
        traceback.print_exc()
        if wait_msg: await wait_msg.delete()
    finally:
        if user_id in user_pending_requests:
            user_pending_requests[user_id] -= 1
            if user_pending_requests[user_id] <= 0:
                user_pending_requests.pop(user_id, None)


'''
# ------------------ Nano Banana 전용 커맨드 (&바나나 / &나노 / &나노바나나) ------------------
@bot.command(name='바나나', aliases=['나노', '나노바나나'])
async def nano_banana_command(ctx, *, prompt: str = ""):
    command_name = "바나나"
    print(f"INFO: User ({ctx.author.id}) used '{command_name}'. Prompt: '{prompt[:80]}...'")

    # Gemini "Nano Banana" 미리보기 모델
    NANO_BANANA_MODEL = "gemini-2.5-flash-image-preview"

    # google.generativeai 스타일: GenerativeModel 사용
    try:
        model = genai.GenerativeModel(
            NANO_BANANA_MODEL
            # 필요 시 generation_config, safety_settings 등 추가 가능
            # generation_config={"temperature": 0.9}
        )
    except Exception as e:
        await ctx.send(f"냥! 모델 초기화 실패냥: {e}")
        print(f"FAIL: '{command_name}' init. Reason: {e}")
        return

    processing_msg = await ctx.send("🍌 나노바나나 모드로 생성/편집 중… 잠깐만!")

    try:
        text_prompt = (prompt or "").strip()

        # contents 구성: 첨부 유무에 따라 T2I 또는 I2I
        parts = []
        if text_prompt:
            parts.append(text_prompt)

        attachments_data = []
        if ctx.message.attachments:
            try:
                attachments_data = await get_image_attachment_data(ctx.message.attachments)
            except Exception as attach_e:
                await processing_msg.edit(content=f"첨부 처리 오류냥: {attach_e}")
                print(f"FAIL: '{command_name}' attachment. Reason: {attach_e}")
                return

        # 한 장만 처리(필요하면 반복으로 확장 가능)
        if attachments_data:
            try:
                att = attachments_data[0]  # {"data": bytes, "mime_type": "...", "filename": "..."}
                # PIL로 리사이즈(너의 &젬편집과 비슷한 정책)
                img = Image.open(io.BytesIO(att["data"]))
                max_pixels = 2048 * 2048
                if img.width * img.height > max_pixels:
                    scale = (max_pixels / (img.width * img.height)) ** 0.5
                    img = img.resize((int(img.width * scale), int(img.height * scale)), Image.Resampling.LANCZOS)

                # google.generativeai는 PIL.Image 객체를 바로 parts에 넣어도 되고,
                # 혹은 inline_data dict로 넣어도 됨. 여기선 dict로 명시적으로 전달.
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                parts.append({
                    "mime_type": "image/png",
                    "data": buf.getvalue()
                })
            except Exception as pillow_e:
                await processing_msg.edit(content=f"이미지 로딩 실패냥: {pillow_e}")
                print(f"FAIL: '{command_name}' PIL load. Reason: {pillow_e}")
                return

        if not parts:
            await processing_msg.edit(content="프롬프트가 없어요! `&바나나 <프롬프트>` 또는 이미지를 첨부해줘냥.")
            return

        # google.generativeai 스타일 호출
        # 텍스트만 → 이미지 생성, 텍스트+이미지 → 이미지 편집
        response = model.generate_content(parts)

        # 응답에서 이미지 추출 (inline_data)
        image_bytes = None
        try:
            cand = response.candidates[0]
            for p in cand.content.parts:
                inline = getattr(p, "inline_data", None)
                if inline and getattr(inline, "data", None):
                    image_bytes = inline.data
                    break
        except Exception:
            pass

        if not image_bytes:
            # 이미지가 없을 때 텍스트라도 보여주기 (안전정책/프롬프트 이슈 등)
            text_out = None
            try:
                for p in response.candidates[0].content.parts:
                    if getattr(p, "text", None):
                        text_out = p.text
                        break
            except Exception:
                pass
            await processing_msg.edit(content=f"이미지 응답이 비어있다냥…\n```{(text_out or '응답을 해석할 수 없어요')[:500]}```")
            print(f"FAIL: '{command_name}' no image part.")
            return

        filename = f"nano_banana_{ctx.message.id}.png"
        file = discord.File(io.BytesIO(image_bytes), filename=filename)
        await processing_msg.delete()
        await ctx.reply(content=f"완료! 🍌 `{text_prompt or '(이미지 편집)'}`", file=file, mention_author=False)
        print(f"SUCCESS: '{command_name}' image sent.")

    except Exception as e:
        await processing_msg.edit(content=f"오류냥: {e}")
        print(f"FAIL: '{command_name}' Unknown. Reason: {e}")
        traceback.print_exc()
'''

'''
@bot.command(name="허깅확대")
async def upscale(ctx: commands.Context):
    print(f"INFO: User ({ctx.author.id}) used command '확대' in channel {ctx.channel.id}.")
    if not ctx.message.attachments:
        await ctx.reply("이미지를 한 장 첨부해줘!", mention_author=False)
        print(f"FAIL: '확대' for ({ctx.author.id}) - No attachment.")
        return
    if len(ctx.message.attachments) > 1:
        await ctx.reply("한 번에 하나의 이미지만 처리 가능하다냥!", mention_author=False)
        print(f"FAIL: '확대' for ({ctx.author.id}) - Too many attachments.")
        return

    att = ctx.message.attachments[0]
    original_filename = att.filename
    if not att.content_type or not att.content_type.startswith("image/"):
        await ctx.reply("이미지 파일 같지 않다냥! (예: png, jpg, webp)", mention_author=False)
        print(f"FAIL: '확대' for ({ctx.author.id}) - Not an image file type.")
        return

    mime_type = att.content_type
    raw_image_bytes = await att.read()
    MAX_DIMENSION = 1216
    try:
        with io.BytesIO(raw_image_bytes) as img_buffer, Image.open(img_buffer) as img:
            width, height = img.size
            # print(f"Original image dimensions: {width}x{height}") # 제거
            if width > MAX_DIMENSION or height > MAX_DIMENSION:
                await ctx.reply(f"냥! 너무 큰 이미지다냥! 가로 또는 세로가 {MAX_DIMENSION}픽셀 이하여야 한다냥. (현재: {width}x{height})",
                                mention_author=False)
                print(f"FAIL: '확대' for ({ctx.author.id}) - Image too large: {width}x{height}.")
                return
    except (UnidentifiedImageError, IOError) as e:  # 이미지 파일 오류
        await ctx.reply("냥냥? 이미지 파일을 인식할 수 없거나 손상되었다냥!", mention_author=False)
        print(f"FAIL: '확대' (image open) for ({ctx.author.id}). Reason: {e}")
        return
    except Exception as e:
        print(f"ERROR: '확대' (image size check) for ({ctx.author.id}). Reason: {e}")
        traceback.print_exc()
        await ctx.reply("이미지 크기 확인 중 알 수 없는 오류가 발생했다냥!", mention_author=False)
        return

    processing_msg = await ctx.reply("이미지 2배 업스케일 준비 중...", mention_author=False)
    try:
        async with aiohttp.ClientSession() as session:
            uploaded_file_data_obj = await upload_file_to_gradio(session, raw_image_bytes, original_filename, mime_type)
            if not uploaded_file_data_obj:
                raise RuntimeError("Gradio 서버에 파일 업로드를 실패했다냥. (콘솔 로그 확인)")
            await processing_msg.edit(content="파일 업로드 완료! 업스케일 작업 대기열에 추가 중...")
            current_session_hash = secrets.token_hex(10)
            api_payload_for_join = make_api_payload(uploaded_file_data_obj,
                                                    current_session_hash)  # make_api_payload -> make_api_payload_upscale (함수명 변경되었으면)
            result = await call_upscale_api_with_queue(session, api_payload_for_join)
            if not result:
                raise RuntimeError("API로부터 최종 이미지 데이터를 받지 못했다냥.")
            upscaled_image_bytes, received_mime_type = result
            try:
                img = Image.open(io.BytesIO(upscaled_image_bytes))
                # print(f"Pillow: Successfully opened result image. Original format detected by Pillow: {img.format}") # 제거
                output_format = 'PNG'  # 기본적으로 PNG로 저장
                if img.mode == 'RGBA' or (img.mode == 'P' and 'transparency' in img.info):
                    pass  # PNG 유지
                else:  # 알파 채널 없으면 RGB로 변환 후 PNG 저장
                    img = img.convert('RGB')
                png_buffer = io.BytesIO()
                img.save(png_buffer, format=output_format)
                png_bytes = png_buffer.getvalue()
                # print(f"Pillow: Result image converted to {output_format} and saved to buffer.") # 제거
            except UnidentifiedImageError:
                raise RuntimeError(f"API로부터 받은 결과가 이미지 파일이 아니다냥! (Pillow가 인식 못함, MIME: {received_mime_type})")
            except Exception as e_pillow:
                raise RuntimeError(f"Pillow 이미지 처리 중 오류 발생냥: {e_pillow}")

        output_file = discord.File(io.BytesIO(png_bytes), filename="upscaled_2x.png")
        await ctx.reply("2× 업스케일 완료!", file=output_file, mention_author=False)
        print(f"SUCCESS: '확대' for ({ctx.author.id}). Upscaled image sent.")
    except RuntimeError as e:
        await ctx.reply(f"업스케일 실패냥... 이유: {e}", mention_author=False)
        print(f"FAIL: '확대' for ({ctx.author.id}). Reason: {e}")
    except asyncio.TimeoutError as e:
        await ctx.reply(f"업스케일 작업 시간 초과냥... 서버가 바쁜 것 같다냥. 이유: {e}", mention_author=False)
        print(f"FAIL: '확대' for ({ctx.author.id}). Reason: Timeout - {e}")
    except Exception as e:
        await ctx.reply(f"냥냥펀치! 알 수 없는 오류로 업스케일에 실패했다냥: {e}", mention_author=False)
        print(f"FAIL: '확대' for ({ctx.author.id}). Unknown error: {e}")
        traceback.print_exc()
    finally:
        try:
            if processing_msg: await processing_msg.delete()
        except discord.HTTPException:
            pass


@bot.command(name='젬편집')  # 원본의 Gemini 편집 명령어
async def gemini_edit_image_command(ctx, *, prompt: str = ""):  # 함수명 충돌 방지
    command_name = "젬편집"  # 로그용
    print(
        f"INFO: User ({ctx.author.id}) used command '{command_name}' in channel {ctx.channel.id}. Prompt: '{prompt[:50]}...'")
    global image_model, GlmGenerationConfig, Schema, Type, safety_settings

    if not image_model:
        await ctx.send("이미지 편집 모델이 로드되지 않아 사용할 수 없다냥!")
        print(f"FAIL: '{command_name}' for ({ctx.author.id}) - Gemini image_model not loaded.")
        return
    if hasattr(image_model, '_model_name') and "exp-image-generation" not in image_model._model_name:
        print(
            f"Warning: Gemini image_model for '{command_name}' might not be the expected 'exp-image-generation' model (current: {getattr(image_model, '_model_name', 'Unknown')})")

    processing_msg = await ctx.send("냥냥... Gemini 이미지 생성 요청을 받았다냥! 잠시만 기다려줘냥...")
    text_prompt = prompt.strip()
    attachments_data = []
    if ctx.message.attachments:
        try:
            attachments_data = await get_image_attachment_data(ctx.message.attachments)  # 범용 첨부파일 다운로더 사용
        except Exception as attach_e:
            await processing_msg.edit(content=f"첨부파일 처리 중 오류 발생냥: {attach_e}")
            print(
                f"FAIL: '{command_name}' (attachment processing) for ({ctx.author.id}). Reason: {attach_e}")
            return

    contents = []
    if text_prompt: contents.append(text_prompt)
    # print(f"텍스트 프롬프트 추가: '{text_prompt}'") # 제거
    valid_attachments = False
    for att in attachments_data:  # 보통 하나의 첨부파일만 처리
        try:
            img = Image.open(io.BytesIO(att["data"]))
            max_pixels = 2048 * 2048
            if img.width * img.height > max_pixels:
                scale = (max_pixels / (img.width * img.height)) ** 0.5
                new_width, new_height = int(img.width * scale), int(img.height * scale)
                # print(f"Resizing image from {img.size} to ({new_width}, {new_height})") # 제거
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            contents.append(img)  # PIL 객체로 전달
            # print(f"PIL Image 객체 추가 (MIME: {att['mime_type']}, 크기: {img.size})") # 제거
            valid_attachments = True
        except Exception as pil_e:  # PIL 변환 실패 시 바이트 데이터로 시도
            # print(f"경고: 첨부파일을 PIL Image 객체로 변환 실패 ({pil_e}). 바이트 데이터로 추가 시도.") # 제거
            contents.append(att["data"])  # 원본 바이트 데이터 사용 (Gemini SDK가 처리할 수 있도록)
            # print(f"이미지 바이트 데이터 추가 (Fallback, MIME: {att['mime_type']}, 크기: {len(att['data'])} bytes)") # 제거
            valid_attachments = True
        if valid_attachments: break  # 첫 번째 유효한 첨부파일만 처리

    if not text_prompt and not valid_attachments:
        await processing_msg.edit(content="유효한 텍스트 프롬프트나 이미지 파일을 제공해줘냥!")
        print(f"FAIL: '{command_name}' for ({ctx.author.id}) - No valid prompt or attachment.")
        return
    if not contents:
        await processing_msg.edit(content="컨텐츠 준비에 실패했다냥!")
        print(f"FAIL: '{command_name}' for ({ctx.author.id}) - Contents list empty.")
        return

    # print(f"Gemini API에 전달할 최종 contents 리스트 (타입 확인): {[type(c) for c in contents]}") # 제거

    config_to_use = None
    if GlmGenerationConfig and Schema and Type:  # GLM 컴포넌트가 성공적으로 import 되었는지 확인
        try:
            TEXT_MODALITY_VALUE, IMAGE_MODALITY_VALUE = 1, 2
            schema_type, text_property_type, image_property_type = Type.OBJECT, Type.STRING, Type.STRING
            # print(f"사용할 Properties: text({text_property_type.name}), image({image_property_type.name})") # 제거
            config_to_use = GlmGenerationConfig(
                response_modalities=[TEXT_MODALITY_VALUE, IMAGE_MODALITY_VALUE],
                response_schema=Schema(type=schema_type, properties={"text": Schema(type=text_property_type),
                                                                     "image": Schema(type=image_property_type)})
            )
            # print(f"GenerationConfig 생성 성공 (properties 포함): {config_to_use}") # 제거
        except AttributeError as e:
            print(f"Warning: GenerationConfig 객체 생성 중 Attribute Error ({e}). Type Enum 멤버 확인 필요. config 없이 호출합니다.")
            config_to_use = None
        except Exception as e:
            print(f"Warning: GenerationConfig 객체 생성 실패 ({e}). config 없이 호출합니다.")
            config_to_use = None
    else:
        print("Warning: 필요한 glm 클래스/Enum을 찾지 못해 generation_config를 설정할 수 없습니다. config 없이 호출합니다.")

    try:
        # print(f"Calling image_model.generate_content with config: {config_to_use}") # 제거
        response = await asyncio.to_thread(image_model.generate_content, contents=contents,
                                           generation_config=config_to_use, safety_settings=safety_settings)
        # print("-" * 20); print("Gemini API 응답 수신:"); # print(response); print("-" * 20) # 제거

        sent, image_found, text_response = False, False, ""
        if response.candidates:
            first_candidate = response.candidates[0]
            finish_reason = getattr(first_candidate, 'finish_reason', 0)
            if finish_reason != 1:  # 1이 정상 종료
                reason_map = {0: "UNKNOWN", 2: "MAX_TOKENS", 3: "SAFETY", 4: "RECITATION", 5: "OTHER"}
                reason_text = reason_map.get(finish_reason, f"CODE_{finish_reason}")
                # print(f"Warning: Generation finished abnormally. Reason: {reason_text}") # 제거
                block_message = f"냥냥... 이미지 생성이 완료되지 못했어냥 (이유: {reason_text})."
                await processing_msg.edit(content=block_message)
                print(
                    f"FAIL: '{command_name}' for ({ctx.author.id}) - Generation finished abnormally: {reason_text}")
                return

            if first_candidate.content and first_candidate.content.parts:
                # print(f"응답에 {len(first_candidate.content.parts)}개의 파트 존재. 내용 확인:") # 제거
                for part in first_candidate.content.parts:
                    # print(f"  Part {i}: {part}") # 제거
                    current_text, inline_data = getattr(part, 'text', None), getattr(part, 'inline_data', None)
                    if current_text is not None and current_text.strip():
                        # print(f"    -> 텍스트 파트 발견: {current_text}...") # 제거
                        text_response += current_text.strip() + "\n"
                    elif inline_data and getattr(inline_data, 'data', None):
                        # print(f"    -> 이미지 데이터 파트 발견! MIME Type: {inline_data.mime_type}") # 제거
                        image_found = True
                        try:
                            image_bytes = inline_data.data
                            image = Image.open(io.BytesIO(image_bytes))
                            image_buffer = io.BytesIO()
                            img_format = "PNG"  # 기본 포맷
                            if inline_data.mime_type:
                                mime = inline_data.mime_type.lower()
                                if "jpeg" in mime:
                                    img_format = "JPEG"
                                elif "webp" in mime:
                                    img_format = "WEBP"
                            supported_discord_formats = ["PNG", "JPEG", "GIF", "WEBP"]
                            if img_format.upper() not in supported_discord_formats: img_format = "PNG"
                            if img_format.upper() == "JPEG" and image.mode == 'RGBA': image = image.convert('RGB')
                            image.save(image_buffer, format=img_format,
                                       quality=95 if img_format.upper() == "JPEG" else None)
                            image_buffer.seek(0)
                            discord_file = discord.File(fp=image_buffer, filename=f"gemini_image.{img_format.lower()}")
                            content_to_send = text_response.strip() if text_response.strip() else f"{ctx.author.mention} 냥! 이미지를 생성했다냥!"
                            await ctx.send(content=content_to_send, file=discord_file)
                            await processing_msg.delete()
                            sent = True
                            print(f"SUCCESS: '{command_name}' for ({ctx.author.id}). Image sent.")
                            break
                        except Exception as img_e:
                            # print(f"    -> 이미지 처리/전송 중 오류 발생: {img_e}") # 제거
                            print(
                                f"FAIL: '{command_name}' (image processing/sending) for ({ctx.author.id}). Reason: {img_e}")
                            traceback.print_exc()
                            await processing_msg.edit(content=f"이미지 데이터를 받았지만 처리 중 오류가 발생했다냥...😿 ({img_e})")
                            sent = True;
                            break
                    # else: print(f"    -> 내용이 없거나 알 수 없는 파트 유형") # 제거
        if sent:
            pass  # print("이미지 처리 시도 완료.") # 제거
        elif not image_found:
            # print("Gemini 응답에서 이미지 데이터를 찾지 못함.") # 제거
            final_message = f"{ctx.author.mention} 냥... 이미지를 생성하지 못했거나 응답에 이미지가 없어냥."
            if text_response:
                final_message += f"\n\n대신 이런 답변을 받았다냥:\n```\n{text_response.strip()}\n```"
            elif hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
                final_message += f"\n(피드백: {response.prompt_feedback.block_reason})"
            await processing_msg.edit(content=final_message)
            print(f"FAIL: '{command_name}' for ({ctx.author.id}) - No image data in Gemini response.")
    except google.api_core.exceptions.InvalidArgument as e:
        # print(f"API Argument Error: {e}") # 제거
        error_detail = str(e)
        user_err_msg = f"냥냥... API 요청 인자값에 문제가 있어냥! (오류: {error_detail})"
        if "modalit" in error_detail.lower() or "schema" in error_detail.lower():
            user_err_msg = f"냥냥... API 설정(Modality/Schema)을 모델이 지원 안 할 수도 있어냥. (오류: {error_detail})"
        await processing_msg.edit(content=user_err_msg)
        print(f"FAIL: '{command_name}' for ({ctx.author.id}) - Gemini API InvalidArgument: {e}")
    except google.api_core.exceptions.GoogleAPIError as e:
        # print(f"Google API Error: {e}") # 제거
        await processing_msg.edit(content=f"냥냥... 구글 API 서버에 문제가 발생했어냥! 잠시 후 다시 시도해줘냥. (오류: {e})")
        print(f"FAIL: '{command_name}' for ({ctx.author.id}) - Gemini API GoogleAPIError: {e}")
    except Exception as e:  # 그 외 모든 예외
        # print(f"Gemini API 호출 또는 전체 처리 중 오류 발생: {e}") # 제거
        # config_str = str(config_to_use) if 'config_to_use' in locals() else "Not Defined/Used"
        # print(f"오류 발생 시 사용된 config: {config_str}") # 제거
        # contents_str = str([type(c) for c in contents]) if 'contents' in locals() else "Not Defined/Used"
        # print(f"오류 발생 시 전달된 contents 타입: {contents_str}") # 제거
        print(f"FAIL: '{command_name}' for ({ctx.author.id}) - Unknown error: {e}")
        traceback.print_exc()
        error_user_msg = f"이미지 생성 중 오류가 발생했다냥! 냥냥.. 😿 관리자를 확인해달라냥!"
        is_config_related_error = False
        if 'config_to_use' in locals() and config_to_use is not None and \
                any(kw in str(e).lower() for kw in ["schema", "type", "properties", "modality"]):
            is_config_related_error = True
            # print("오류 원인 추정: generation_config 객체 생성/전달 문제.") # 제거
        if is_config_related_error: error_user_msg += "\n(내부 설정 오류 가능성 있음)"
        await processing_msg.edit(content=error_user_msg)
'''


@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user: return
    await bot.process_commands(message)  # 명령어 먼저 처리

    # 명령어 사용 시 AI 응답 방지 (기존 로직 유지)
    if message.content.startswith(("&", bot.user.mention)):  # 간단한 접두사/멘션 체크
        # 좀 더 정확하게 하려면 모든 명령어 이름을 확인해야 하지만, 일단 이 정도로 타협
        possible_command_parts = message.content.split(" ", 1)
        if len(possible_command_parts) > 0:
            first_word = possible_command_parts[0].replace(bot.user.mention, "").strip().lstrip("&")
            if bot.get_command(first_word):  # 실제 명령어인지 확인
                return  # 명령어였으므로 AI 응답 안 함

    # AI 응답 조건 (멘션, DM, 추적 채널/스레드)
    # tracked_channels는 전역 변수로 가정 (필요 시 on_ready에서 로드)
    global tracked_channels  # 이 변수가 사용된다면 전역 선언 필요
    tracked_channels = []  # 임시 초기화 (실제 사용 시 on_ready에서 로드)

    if not (bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel) or \
            message.channel.id in tracked_channels or message.channel.id in tracked_threads):
        return

    content_for_ai = message.content.replace(f"<@!{bot.user.id}>", "").replace(f"<@{bot.user.id}>", "").strip()
    # 멘션 제거 후 내용이 없으면 응답 안 함
    if not content_for_ai and not message.attachments:  # 첨부파일만 있어도 AI 응답 시도
        return

    print(
        f"INFO: AI processing message from {message.author} ({message.author.id}) in channel {message.channel.id}. Content: '{content_for_ai[:50]}...' Attachments: {len(message.attachments)}")

    try:
        async with message.channel.typing():
            query = content_for_ai
            attachments_for_ai = []
            if message.attachments:
                attachments_for_ai = await get_attachment_data_general(message.attachments)  # 범용 첨부파일 로더
                if not attachments_for_ai and message.attachments:  # 다운로드 실패 시
                    print(f"Warning: AI - Failed to process attachments for message {message.id} from {message.author}")

            if message.reference and message.reference.message_id:  # 답장 처리
                try:
                    reply_message = await message.channel.fetch_message(message.reference.message_id)
                    if reply_message.author.id != bot.user.id:
                        query = f"{query} (답장 대상: @{reply_message.author.name} \"{reply_message.clean_content}...\")"
                    if reply_message.attachments:  # 답장 메시지의 첨부파일도 포함
                        attachments_for_ai.extend(await get_attachment_data_general(reply_message.attachments))
                except discord.NotFound:
                    print(f"Warning: AI - Could not fetch replied message {message.reference.message_id}")
                except Exception as e_ref:
                    print(f"Warning: AI - Error processing replied message {message.reference.message_id}: {e_ref}")

            response_text = await generate_response(message.channel.id, attachments_for_ai, query)
            await split_and_send_response(message, response_text, 1700)  # 메시지 분할 전송

            # 메시지 히스토리 관리 (최근 N개 턴만 유지)
            MAX_HISTORY_TURNS = 50
            if message.channel.id in message_history:
                current_hist = message_history[message.channel.id].history
                if len(current_hist) > (MAX_HISTORY_TURNS * 2 + len(bot_template)):  # bot_template 길이 고려
                    # bot_template은 항상 유지하고, 그 뒤의 최근 대화만 남김
                    message_history[message.channel.id].history = bot_template + current_hist[-(MAX_HISTORY_TURNS * 2):]

            # 히스토리 저장 (shelve)
            with shelve.open('chatdata') as file:
                if message.channel.id in message_history:  # 히스토리가 실제로 생성되었는지 확인
                    file[str(message.channel.id)] = message_history[message.channel.id].history
    except Exception as e:
        print(f"ERROR: AI on_message processing failed for message {message.id} from {message.author}. Reason: {e}")
        traceback.print_exc()
        if hasattr(e, 'code') and e.code == 50035:  # Discord 메시지 길이 제한
            await message.channel.send("냥냥... 답변이 너무 길어서 보낼 수가 없다냥...")
        # else: await message.channel.send('AI 처리 중 오류가 발생했다냥.') # 일반적인 오류 메시지는 생략 (로그로 충분)


async def get_attachment_data_general(attachments: List[discord.Attachment]) -> List[
    Dict[str, any]]:  # 함수명 변경하여 Gemini용과 구분
    """AI 모델에 전달하기 위한 범용 첨부파일 다운로더"""
    result = []
    async with aiohttp.ClientSession() as session:
        for attachment in attachments:
            try:
                async with session.get(attachment.url) as resp:
                    if resp.status == 200:
                        attachment_data = await resp.read()
                        mime_type = attachment.content_type
                        if not mime_type:  # 기본적인 MIME 타입 추론
                            ext = os.path.splitext(attachment.filename.lower())[1]
                            if ext in ['.png', '.jpg', '.jpeg', '.webp', '.gif', '.heic', '.heif']:
                                mime_type = f"image/{'jpeg' if ext == '.jpg' else ext[1:]}"
                            # 기타 타입에 대한 추론 추가 가능
                            else:
                                mime_type = "application/octet-stream"  # 매우 일반적인 타입
                        result.append({"mime_type": mime_type, "data": attachment_data})
                    # else: print(f"Warning: Failed to download attachment {attachment.filename}, status {resp.status}") # 제거
            except Exception as e:
                print(f"Warning: Error downloading attachment {attachment.filename} for AI: {e}")  # 실패 시 로그
    return result


async def generate_response(channel_id, attachments, text):
    """Gemini를 사용하여 AI 응답 생성 (첨부파일 포함)"""
    global model
    if model is None:
        return "냥냥... Gemini 모델이 초기화되지 않았다냥... 설정이나 API 키를 확인해줘냥."

    try:
        prompt_parts = []  # Gemini SDK는 Part 객체 또는 Part와 유사한 딕셔너리 리스트를 기대
        for att in attachments:  # attachments는 이미 {'mime_type': ..., 'data': ...} 형태의 딕셔너리 리스트
            prompt_parts.append(att)  # 그대로 전달
        prompt_parts.append({"text": text})  # 텍스트도 딕셔너리 형태로 추가

        if channel_id not in message_history or message_history[channel_id] is None:  # 해당 채널 히스토리 없으면 새로 시작
            message_history[channel_id] = model.start_chat(history=bot_template.copy())  # .copy()로 원본 불변성 유지

        try:
            response = await message_history[channel_id].send_message_async(prompt_parts)
            return response.text
        except Exception as first_err:
            print(f"Warning: Gemini send_message_async failed for channel {channel_id} ({first_err}). Resetting chat session and retrying...")
            message_history[channel_id] = model.start_chat(history=bot_template.copy())
            response = await message_history[channel_id].send_message_async(prompt_parts)
            return response.text
    except Exception as e:
        # 오류 발생 시 파일에 상세 로그 기록
        with open('gemini_errors.log', 'a+', encoding='utf-8') as errorlog:
            timestamp = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            errorlog.write(f"\n--- {timestamp} ---\n")
            errorlog.write(f"Channel ID: {channel_id}\n")
            errorlog.write(f"Text Input: {text[:200]}...\n")  # 긴 텍스트는 일부만 기록
            errorlog.write(f"Number of Attachments: {len(attachments)}\n")
            if channel_id in message_history and hasattr(message_history[channel_id], 'history'):
                # 너무 긴 히스토리는 일부만 기록
                history_to_log = message_history[channel_id].history
                log_hist_str = str(history_to_log[-10:]) if len(history_to_log) > 10 else str(history_to_log)
                errorlog.write(f"History (last up to 5 turns):\n{log_hist_str}\n")
            errorlog.write('Traceback:\n' + traceback.format_exc() + "\n")
        print(
            f"ERROR: Gemini response generation for channel {channel_id} failed. See gemini_errors.log. Exception: {e}")
        return "냥냥... 답변을 생성하는 중에 심각한 오류가 발생했다냥... 관리자에게 문의해줘냥."


class ConfirmClearView(discord.ui.View):  # DM 삭제용 View
    def __init__(self, user: discord.User, timeout=30):
        super().__init__(timeout=timeout)
        self.user = user

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.user:
            await interaction.response.send_message("사용 권한이 없다냥!", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="삭제", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        deleted = 0
        try:
            # DM 채널이므로 interaction.channel 사용
            async for msg in interaction.channel.history(limit=100):
                if msg.author == interaction.client.user:  # 봇이 보낸 메시지만 삭제
                    await msg.delete()
                    deleted += 1
                    await asyncio.sleep(0.2)  # Rate limit 방지
            await interaction.followup.send(f"✅ {deleted}개의 메시지를 삭제했다냥!", ephemeral=True)
            print(
                f"INFO:  User  ({interaction.user.id}) cleared {deleted} bot messages in DM with bot.")
        except Exception as e:
            await interaction.followup.send("메시지 삭제 중 오류가 발생했다냥.", ephemeral=True)
            print(f"ERROR: /clear command failed for  User  ({interaction.user.id}). Reason: {e}")
        self.stop()

    @discord.ui.button(label="취소", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("삭제를 취소했다냥!", ephemeral=True)
        self.stop()


@bot.tree.command(name="clear", description="Clear DM history with the bot.")  # DM 전용 명령어
async def clear(interaction: discord.Interaction):
    print(f"INFO:  User  ({interaction.user.id}) used slash command '/clear'.")
    if interaction.guild is not None:  # 서버 채널에서는 사용 불가
        await interaction.response.send_message("❌ 이 명령어는 DM에서만 사용할 수 있다냥!", ephemeral=True)
        return
    view = ConfirmClearView(interaction.user)
    await interaction.response.send_message(
        "**정말로 DM에서 냥냥이가 보낸 메시지를 삭제하시겠습니까?**\n"
        "`삭제` 버튼을 누르면 즉시 삭제됩니다.",
        view=view, ephemeral=True
    )


@bot.tree.command(name='forget', description='Forget message history in the current channel.')
@app_commands.describe(persona='Optional: Set a new persona for the bot.')
async def forget(interaction: discord.Interaction, persona: Optional[str] = None):
    log_persona = persona if persona else "None"
    print(
        f"INFO:  User  ({interaction.user.id}) used slash command '/forget' in channel {interaction.channel.id}. Persona: {log_persona}")
    channel_id = interaction.channel_id
    try:
        if channel_id in message_history:  # 기존 히스토리 삭제
            message_history.pop(channel_id)

        # 새 페르소나 또는 기본 템플릿으로 히스토리 재시작
        temp_template = bot_template.copy()
        if persona:
            temp_template.append({'role': 'user', 'parts': [f"이전에 했던 말을 잊어줘! 너는 {persona}야."]})
            temp_template.append({'role': 'model', 'parts': ["알겠습니다!"]})
        message_history[channel_id] = model.start_chat(history=temp_template)

        # 변경된 히스토리 저장
        with shelve.open('chatdata') as file:
            file[str(channel_id)] = message_history[channel_id].history
        await interaction.response.send_message(f"이 채널의 메시지 기록을 삭제했다냥!{f' 새로운 페르소나: {persona}냥!' if persona else ''}")
    except Exception as e:
        await interaction.response.send_message("메시지 기록 삭제/저장 중 오류가 발생했다냥.", ephemeral=True)
        print(
            f"ERROR: /forget command for  User  ({interaction.user.id}) in channel {channel_id} failed. Reason: {e}")


@bot.tree.command(name='createthread', description='Create a thread where the bot responds to every message.')
@app_commands.describe(name='Thread name')
async def create_thread_command(interaction: discord.Interaction,
                                name: str):  # 함수명 변경 (create_thread는 discord.py 내부 함수와 충돌 가능성)
    print(
        f"INFO:  User  ({interaction.user.id}) used slash command '/createthread' in channel {interaction.channel.id}. Thread name: {name}")
    if not isinstance(interaction.channel, discord.TextChannel):
        await interaction.response.send_message("텍스트 채널에서만 스레드를 만들 수 있다냥!", ephemeral=True)
        return
    try:
        thread = await interaction.channel.create_thread(name=name, auto_archive_duration=1440)  # 24시간 후 자동 아카이브
        if thread.id not in tracked_threads:  # 중복 추가 방지
            tracked_threads.append(thread.id)
        await interaction.response.send_message(f"스레드 '{name}' 생성 완료다냥! 이 스레드에서 이야기하라냥!")
        await thread.send(f"{interaction.user.mention}, 응답 준비 완료다냥!")
        with shelve.open('chatdata') as file:
            file['tracked_threads'] = tracked_threads
        print(f"INFO: Thread {thread.id} ('{name}') created by  and added to tracking.")
    except discord.HTTPException as e:
        print(f"ERROR: /createthread by  ({interaction.user.id}) failed (Discord API). Reason: {e}")
        if not interaction.response.is_done():
            await interaction.response.send_message("스레드 생성 중 Discord API 오류가 발생했다냥.", ephemeral=True)
        else:
            await interaction.followup.send("스레드 생성 중 Discord API 오류가 발생했다냥.", ephemeral=True)
    except Exception as e:
        print(f"ERROR: /createthread by  ({interaction.user.id}) failed (Other). Reason: {e}")
        if not interaction.response.is_done():
            await interaction.response.send_message("스레드 생성 중 내부 오류가 발생했다냥.", ephemeral=True)
        else:
            await interaction.followup.send("스레드 생성 중 내부 오류가 발생했다냥.", ephemeral=True)


@bot.tree.command(name="wake", description="Wake up 검냥이 (secondary bot process).")
async def wake(interaction: discord.Interaction):
    print(f"INFO:  User  ({interaction.user.id}) used slash command '/wake'.")
    global secondary_process
    # LOCK_PATH는 전역 변수 lock_path 사용
    await interaction.response.defer(ephemeral=True)
    if os.path.exists(lock_path):  # 전역 lock_path 사용
        try:
            with open(lock_path, "r") as f:
                pid = int(f.read().strip())
            if psutil.pid_exists(pid):
                await interaction.followup.send("검냥이는 이미 일어나있다냥!")
                return
            else:  # 죽은 프로세스 락 파일
                os.remove(lock_path)
                print(f"INFO: Stale lock file {lock_path} removed by '/wake' from .")
        except Exception as e:
            await interaction.followup.send(f"PID 검사 중 오류 발생: {e}", ephemeral=True)
            print(f"ERROR: /wake PID check for  failed. Reason: {e}")
            return

    script_path = os.path.join(os.path.dirname(__file__), "main2.py")
    if not os.path.isfile(script_path):
        await interaction.followup.send("main2.py 파일이 없다냥!", ephemeral=True)
        print(f"FAIL: /wake by  - main2.py not found at {script_path}.")
        return
    try:
        # stdout, stderr 파이프 없이 실행 (백그라운드 실행)
        secondary_process = subprocess.Popen([sys.executable, script_path])
        with open(lock_path, "w") as f:
            f.write(str(secondary_process.pid))
        await interaction.followup.send("검냥이를 깨웠다냥!")
        print(
            f"INFO: 검냥이 (main2.py PID: {secondary_process.pid}) started by  ({interaction.user.id}).")
    except Exception as e:
        await interaction.followup.send(f"검냥이 실행 중 오류 발생: {e}", ephemeral=True)
        print(f"ERROR: /wake by  failed to start main2.py. Reason: {e}")


async def split_and_send_response(message_system: discord.Message, text: str, max_length: int):
    """AI 응답을 코드 블록과 일반 텍스트로 분리하여 전송 (최대 길이 고려)"""
    parts = re.split(r'(```[\s\S]*?```)', text)  # 코드 블록 기준으로 분리
    for part in parts:
        if not part.strip(): continue  # 빈 부분은 무시
        if part.startswith("```") and part.endswith("```"):  # 코드 블록인 경우
            code_content = part[3:-3]  # ``` 제거
            # 코드 블록도 너무 길면 분할 (Discord 임베드 제한 등 고려)
            for i in range(0, len(code_content), max_length - 10):  # ```와 언어명 여유 공간
                chunk = code_content[i:i + max_length - 10]
                # 간단한 언어 추론 (첫 줄이 짧은 영단어면 언어로 간주)
                lang = ""
                first_line = chunk.split('\n', 1)[0]
                if re.match(r'^[a-zA-Z0-9_+#-]+$', first_line) and len(first_line) < 20:
                    lang = first_line
                    # chunk = chunk[len(lang):].lstrip('\n') # 언어명 제거 시도 (때로 부정확할 수 있음)
                await message_system.reply(f"```{lang}\n{chunk}\n```")
        else:  # 일반 텍스트인 경우
            for i in range(0, len(part), max_length):
                await message_system.reply(part[i:i + max_length])


@bot.event
async def on_ready():
    global tracked_threads, tracked_channels  # tracked_channels 사용 시 전역 선언
    tracked_channels = []  # 임시 초기화, 실제 사용 시 shelve에서 로드

    try:
        # shelve에서 데이터 로드 (히스토리, 추적 스레드 등)
        with shelve.open('chatdata') as file:
            for key, value in file.items():  # 채널별 대화 히스토리 로드
                if key.isdigit():  # 키가 숫자인 경우 (채널 ID)
                    try:
                        # 히스토리 형식 검증 (간단하게)
                        if isinstance(value, list) and all(
                                isinstance(item, dict) and 'role' in item and 'parts' in item for item in value):
                            # 저장된 채널 히스토리가 예전 bot_template을 포함하고 있어도
                            # 시작 부분의 템플릿만 제거하고 현재 bot_template을 다시 붙인다.
                            # 이렇게 해야 명령어 개편(&생성23~26)이 기존 채널에도 즉시 반영된다.
                            saved_conversation = value
                            if value:
                                first_parts = value[0].get('parts', [])
                                first_text = str(first_parts[0]) if first_parts else ''
                                if '너는 인공지능 비서 냥냥이야' in first_text:
                                    template_end = None
                                    for idx, item in enumerate(value[:30]):
                                        parts = item.get('parts', [])
                                        item_text = str(parts[0]) if parts else ''
                                        if (
                                            '복제와 편집의 경우에는 꼭 레퍼런스 이미지를 보내줘야 된다냥' in item_text
                                            or '앞으로 냥냥이 이미지 명령어를 물어보면 이 사용법을 기준으로' in item_text
                                        ):
                                            template_end = idx
                                            break
                                    if template_end is not None:
                                        saved_conversation = value[template_end + 1:]

                            refreshed_history = bot_template.copy() + saved_conversation
                            message_history[int(key)] = model.start_chat(history=refreshed_history)
                        else:  # 형식 안 맞으면 기본 템플릿으로 초기화
                            print(f"Warning: Invalid history format for channel {key} in chatdata. Reinitializing.")
                            message_history[int(key)] = model.start_chat(history=bot_template.copy())
                    except Exception as e_hist:  # 히스토리 로드 중 오류 발생 시
                        print(f"Error loading history for channel {key}: {e_hist}. Reinitializing.")
                        message_history[int(key)] = model.start_chat(history=bot_template.copy())

            tracked_threads = file.get('tracked_threads', [])  # 추적 스레드 ID 리스트 로드
            # tracked_channels = file.get('tracked_channels', []) # 추적 채널 ID 리스트 로드 (필요 시)
        print(
            f"Loaded {len(message_history)} channel histories and {len(tracked_threads)} tracked threads from chatdata.")

        synced = await bot.tree.sync()
        print(f"{len(synced)}개의 명령어를 동기화했습니다냥!")
    except Exception as e:
        print(f"동기화 또는 데이터 로딩 중 오류 발생: {e}")
        traceback.print_exc()  # 상세 오류 출력
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


def cleanup():
    # LOCK_PATH는 전역 변수 lock_path 사용
    if os.path.exists(lock_path):
        try:
            os.remove(lock_path)
            print(f"INFO: Lock file {lock_path} removed on bot exit.")
        except Exception as e:
            print(f"ERROR: Could not remove lock file {lock_path} on bot exit: {e}")


atexit.register(cleanup)


async def main():
    init_clone_limit_db()
    async with bot:
        await bot.add_cog(Music(bot))
        # BOT_TOKEN은 상단에서 직접 정의된 값을 사용
        if not BOT_TOKEN:
            print("CRITICAL ERROR: Discord Bot Token (BOT_TOKEN) is not set. Bot cannot start.")
            return
        await bot.start(BOT_TOKEN)


if __name__ == "__main__":
    # asyncio.run()은 스크립트 최하단에서 한 번만 호출되어야 합니다.
    # 만약 다른 곳에서 asyncio.run()을 사용 중이라면 충돌이 발생할 수 있습니다.
    asyncio.run(main())
