import random
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, Message

import config
from PritiMusic.utils.decorators.language import language

# Yahan styled_button aur ButtonStyle import kiya gaya hai
from button import styled_button, ButtonStyle


# Main Bot Link (Where users can create a clone)
# Ideally, this should be in config, but hardcoding here works too.
BOT_LINK = "https://t.me/clone_MUSICrobot"

# ✅ Helper to safely get Random Start Image
def get_random_start_img():
    if config.START_IMG_URL:
        if isinstance(config.START_IMG_URL, list):
            return random.choice(config.START_IMG_URL)
        return config.START_IMG_URL
    return "https://i.supaimg.com/d8919cc0-dc9c-41e0-9c14-2ff75835e603/65159577-4855-412e-95e7-f72324a37d7f.jpg" # Fallback Image


@Client.on_message(filters.command("clone"))
@language
async def ping_clone(client: Client, message: Message, _):
    # ✅ Random Photo Logic (Spoiler Removed)
    await message.reply_photo(
        photo=get_random_start_img(),
        caption=_["NO_CLONE_MSG"],
        reply_markup=InlineKeyboardMarkup(
            [
                [styled_button(" ❖ 𝐆ᴏ 𝐀ηᴅ 𝐂ʟᴏηє ❖ ", url=BOT_LINK, style=ButtonStyle.SUCCESS)]
            ]
        )
    )
