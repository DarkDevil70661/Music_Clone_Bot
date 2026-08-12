# PritiMusic/plugins/admins/autoplay.py

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from PritiMusic import app
from PritiMusic.utils.database.autoplay import is_autoplay_group, add_autoplay_group, remove_autoplay_group
from PritiMusic.utils.decorators import AdminRightsCheck
from config import BANNED_USERS  

@app.on_message(
    filters.command(["autoplay"]) 
    & filters.group 
    & ~BANNED_USERS
)
@AdminRightsCheck
async def autoplay_mode(client, message: Message, _, chat_id):
    state = await is_autoplay_group(chat_id)
    
    text = "**🎧 𝐀𝐮𝐭𝐨𝐩𝐥𝐚𝐲 𝐒𝐲𝐬𝐭𝐞𝐦**\n\nGroup ke liye autoplay status update kar diya gaya hai.\n\n-- 🤞 𝐏ᴏᴡєʀєᴅ 𝐁ʏ ➛ BETA BOT HUB.🙂❤️"
    
    if state:
        # Pehle ON tha, ab OFF kar rahe hain
        await remove_autoplay_group(chat_id)
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(text="Autoplay : Disabled 🔴", callback_data="dummy_btn")],
            [InlineKeyboardButton(text="🤞 𝐁𝐄𝐓𝐀 𝐁𝐎𝐓 𝐇𝐔𝐁", url="https://t.me/Music_Bot_Center_x")]
        ])
        return await message.reply_text(text, reply_markup=reply_markup)
    else:
        # Pehle OFF tha, ab ON kar rahe hain
        await add_autoplay_group(chat_id)
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(text="Autoplay : Enabled 🟢", callback_data="dummy_btn")],
            [InlineKeyboardButton(text="🤞 𝐁𝐄𝐓𝐀 𝐁𝐎𝐓 𝐇𝐔𝐁", url="https://t.me/Music_Bot_Center_x")]
        ])
        return await message.reply_text(text, reply_markup=reply_markup)