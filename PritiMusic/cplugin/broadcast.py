"""
Broadcast Plugin for PritiMusic
🤞 𝐏ᴏᴡєʀєᴅ 𝐁ʏ ➛ <a href="https://t.me/Music_Bot_Center_x">[˹BETA BOTS.🙂❤️˼]</a>
"""

import asyncio
from pyrogram import filters, Client
from pyrogram.errors import FloodWait
from pyrogram.types import Message
from pyrogram.enums import ParseMode

from PritiMusic import app
from PritiMusic.utils.database import (
    get_served_chats_clone,
    get_served_users_clone,
)
from PritiMusic.utils.database.clonedb import get_owner_id_from_db
from PritiMusic.utils.decorators.language import language
from config import OWNER_ID, SUPPORT_CHAT

# HTML Footer
POWERED_BY = '\n\n🤞 𝐏ᴏᴡєʀєᴅ 𝐁ʏ ➛ <a href="https://t.me/Music_Bot_Center_x">[˹BETA BOTS.🙂❤️˼]</a>'

# Global flag
IS_BROADCASTING = False

@Client.on_message(filters.command(["broadcast"]))
@language
async def broadcast_message(client, message: Message, _):
    global IS_BROADCASTING
    
    bot_obj = await client.get_me()
    bot_id = bot_obj.id
    
    try:
        clone_owner_id = await get_owner_id_from_db(bot_id)
    except:
        clone_owner_id = get_owner_id_from_db(bot_id)
        
    if message.from_user.id not in [OWNER_ID, clone_owner_id]:
        return await message.reply_text(_["c_brod_1"].format(SUPPORT_CHAT))

    if IS_BROADCASTING:
        return await message.reply_text("⏳ **Broadcast is already running. Please wait.**")

    query = ""
    if message.reply_to_message:
        query = message.text.split(None, 1)[1] if len(message.command) > 1 else ""
    else:
        if len(message.command) < 2:
            return await message.reply_text(_["broad_2"])
        query = message.text.split(None, 1)[1]

    flags = ["-pin", "-nobot", "-pinloud", "-user"]
    query_to_send = query
    for flag in flags:
        query_to_send = query_to_send.replace(flag, "").strip()

    if not message.reply_to_message and not query_to_send:
        return await message.reply_text(_["broad_8"])

    IS_BROADCASTING = True
    status_msg = await message.reply_text(_["broad_1"])

    try:
        # --- PART A: BROADCAST TO GROUPS ---
        if "-nobot" not in message.text:
            sent = 0
            pin_count = 0
            served_chats = await get_served_chats_clone(bot_id)
            
            for chat in served_chats:
                try:
                    chat_id = int(chat["chat_id"])
                    if message.reply_to_message:
                        m = await client.forward_messages(chat_id, message.chat.id, message.reply_to_message.id)
                    else:
                        m = await client.send_message(chat_id, text=query_to_send)
                    
                    if "-pin" in message.text or "-pinloud" in message.text:
                        try:
                            msg_obj = m[0] if isinstance(m, list) else m
                            notify = "-pinloud" in message.text
                            await msg_obj.pin(disable_notification=not notify)
                            pin_count += 1
                        except: pass
                    sent += 1
                    await asyncio.sleep(0.2) 
                except FloodWait as fw:
                    await asyncio.sleep(int(fw.value))
                except Exception:
                    continue
            await message.reply_text(
                _["broad_3"].format(sent, pin_count) + POWERED_BY, 
                parse_mode=ParseMode.HTML, 
                disable_web_page_preview=True
            )

        # --- PART B: BROADCAST TO USERS ---
        if "-user" in message.text:
            susr = 0
            served_users = await get_served_users_clone(bot_id)
            
            for user in served_users:
                try:
                    user_id = int(user["user_id"])
                    if message.reply_to_message:
                        await client.forward_messages(user_id, message.chat.id, message.reply_to_message.id)
                    else:
                        await client.send_message(user_id, text=query_to_send)
                    susr += 1
                    await asyncio.sleep(0.2)
                except FloodWait as fw:
                    await asyncio.sleep(int(fw.value))
                except Exception:
                    pass
            await message.reply_text(
                _["broad_4"].format(susr) + POWERED_BY, 
                parse_mode=ParseMode.HTML, 
                disable_web_page_preview=True
            )

    finally:
        IS_BROADCASTING = False
