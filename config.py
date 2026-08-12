import re
from os import getenv
from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()

API_ID = int(getenv("API_ID", "0"))
API_HASH = getenv("API_HASH")

BOT_TOKEN = getenv("BOT_TOKEN")
BOT_ID = getenv("BOT_ID")

SHRUTI_API_URL = "https://api.shrutibots.site"
SHRUTI_API_KEY = "ShrutiBotsC0WH1GowF2HkGoKv4F3y"

OWNER_USERNAME = getenv("OWNER_USERNAME", "")
BOT_USERNAME = getenv("BOT_USERNAME", "")
BOT_NAME = getenv("BOT_NAME", "")
ASSUSERNAME = getenv("ASSUSERNAME", "")
BOT_LINK = getenv("BOT_LINK", "https://t.me/clone_MUSICrobot")

MONGO_DB_URI = getenv("MONGO_DB_URI")

YTPROXY_URL = getenv("YTPROXY_URL", 'https://tgapi.xbitcode.com')
YT_API_KEY = getenv("YT_API_KEY" , 'xbit_B4TNnBAoe6uoSM7NLFz-dk6X7GibJ6Bh')

DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 17000))

LOGGER_ID = int(getenv("LOGGER_ID", "0"))
CLONE_LOGGER = LOGGER_ID

OWNER_ID = int(getenv("OWNER_ID", "0"))

HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")
HEROKU_API_KEY = getenv("HEROKU_API_KEY")

UPSTREAM_REPO = getenv(
    "UPSTREAM_REPO",
    "https://github.com/ISTKHAROP/clone",
)
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "main")
GIT_TOKEN = getenv("GIT_TOKEN", "")

SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/IAMISTKHAR")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/KavyaBots")
GITHUB = getenv("GITHUB", "https://github.com/TEAM-ISTKHAR")

AUTO_LEAVING_ASSISTANT = getenv("AUTO_LEAVING_ASSISTANT", "False")
AUTO_LEAVE_ASSISTANT_TIME = int(getenv("ASSISTANT_LEAVE_TIME", "9000"))

SONG_DOWNLOAD_DURATION = int(getenv("SONG_DOWNLOAD_DURATION", "9999999"))
SONG_DOWNLOAD_DURATION_LIMIT = int(getenv("SONG_DOWNLOAD_DURATION_LIMIT", "9999999"))

SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", "1c21247d714244ddbb09925dac565aed")
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", "709e1a2969664491b58200860623ef19")

PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", 25))
PLAYLIST_ID = -1003812209413

TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", "5242880000"))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", "5242880000"))

STRING1 = getenv("STRING_SESSION", "")
STRING2 = getenv("STRING_SESSION2", None)

BANNED_USERS = filters.user()
adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}

START_IMG_URL = getenv("START_IMG_URL", "https://i.supaimg.com/d8919cc0-dc9c-41e0-9c14-2ff75835e603/7044b8ee-8eda-45fe-9152-36d8c90c38e5.jpg").split()
HELP_IMG_URL = getenv("HELP_IMG_URL", "https://i.supaimg.com/d8919cc0-dc9c-41e0-9c14-2ff75835e603/93c17667-88a9-48cf-90e3-5db11c8e1034.jpg").split()
PING_IMG_URL = getenv("PING_IMG_URL", "https://i.supaimg.com/d8919cc0-dc9c-41e0-9c14-2ff75835e603/65159577-4855-412e-95e7-f72324a37d7f.jpg").split()

PLAYLIST_IMG_URL = getenv("PLAYLIST_IMG_URL", "https://i.supaimg.com/d8919cc0-dc9c-41e0-9c14-2ff75835e603/8c1e1ab0-fff6-40b7-b11a-bfcfdeb46da8.jpg").split()
STATS_IMG_URL = getenv("STATS_IMG_URL", "https://files.catbox.moe/6k3x66.jpg")
TELEGRAM_AUDIO_URL = getenv("TELEGRAM_AUDIO_URL", "https://i.supaimg.com/d8919cc0-dc9c-41e0-9c14-2ff75835e603/ae47c575-a948-4884-a2b8-3fb64dd5cbf6.jpg").split()
TELEGRAM_VIDEO_URL = getenv("TELEGRAM_VIDEO_URL", "https://i.supaimg.com/d8919cc0-dc9c-41e0-9c14-2ff75835e603/ae47c575-a948-4884-a2b8-3fb64dd5cbf6.jpg").split()
STREAM_IMG_URL = getenv("STREAM_IMG_URL", "https://i.supaimg.com/d8919cc0-dc9c-41e0-9c14-2ff75835e603/30d4e018-9a14-4d43-8955-9eaf9e50c762.png").split()
SOUNCLOUD_IMG_URL = getenv("SOUNCLOUD_IMG_URL", "https://i.supaimg.com/d8919cc0-dc9c-41e0-9c14-2ff75835e603/5f111ec5-af25-4c36-aebe-527414a74cd8.jpg").split()
YOUTUBE_IMG_URL = getenv("YOUTUBE_IMG_URL", "https://te.legra.ph/file/6abc32c3858f205434cd5.jpg").split()
SPOTIFY_ARTIST_IMG_URL = getenv("SPOTIFY_ARTIST_IMG_URL", "https://i.supaimg.com/d8919cc0-dc9c-41e0-9c14-2ff75835e603/65159577-4855-412e-95e7-f72324a37d7f.jpg").split()
SPOTIFY_ALBUM_IMG_URL = getenv("SPOTIFY_ALBUM_IMG_URL", "https://i.supaimg.com/d8919cc0-dc9c-41e0-9c14-2ff75835e603/65159577-4855-412e-95e7-f72324a37d7f.jpg").split()
SPOTIFY_PLAYLIST_IMG_URL = getenv("SPOTIFY_PLAYLIST_IMG_URL", "https://i.supaimg.com/d8919cc0-dc9c-41e0-9c14-2ff75835e603/65159577-4855-412e-95e7-f72324a37d7f.jpg").split()

def time_to_seconds(time):
    return sum(int(x) * 60**i for i, x in enumerate(reversed(str(time).split(":"))))

DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))

if SUPPORT_CHANNEL and not re.match("(?:http|https)://", SUPPORT_CHANNEL):
    raise SystemExit("[ERROR] - SUPPORT_CHANNEL url must start with https://")

if SUPPORT_CHAT and not re.match("(?:http|https)://", SUPPORT_CHAT):
    raise SystemExit("[ERROR] - SUPPORT_CHAT url must start with https://")

CMBOT = [
    "💞", "🥂", "🔍", "🧪", "⚡️", "🔥", "🦋", "🎩", "🌈", "🍷",
    "🥃", "🥤", "🕊️", "💌", "🧨", "✨", "💥", "💯", "🌟", "⚡️",
    "❤️", "😍", "🥰", "😘", "😂", "🤣", "😱", "😡", "👏", "🙏",
    "🎉", "🎊", "🎶", "🎵", "🎧", "🎸", "🎹", "🥁", "🎺", "🎷",
    "🔥", "⚡️", "💫", "🌙", "☀️", "🌈", "❄️", "🌸", "🌺", "🌹",
    "🦋", "🕊️", "🐍", "🐯", "🦁", "🐺", "🐉", "🦅", "🦄", "🐎"
]

EFFECT_ID = [
    5046509860389126442,
    5107584321108051014,
    5104841245755180586,
    5159385139981059251,
]
