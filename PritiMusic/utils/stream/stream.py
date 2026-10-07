import os
import random
from typing import Union

from pyrogram.types import InlineKeyboardMarkup

import config
from PritiMusic import Carbon, YouTube, app
from PritiMusic.core.call import Lucky
from PritiMusic.misc import db
from PritiMusic.utils.database import add_active_video_chat, is_active_chat
from PritiMusic.utils.exceptions import AssistantErr
from PritiMusic.utils.inline import aq_markup, close_markup, stream_markup
from PritiMusic.utils.stream.queue import put_queue, put_queue_index
from PritiMusic.utils.pastebin import LuckyBin
from PritiMusic.utils.thumbnails import get_thumb 

# ✅ Helper to get Random Image safely
def get_random_img(img_list):
    if img_list:
        if isinstance(img_list, list):
            return random.choice(img_list)
        return img_list
    return "https://telegra.ph/file/2e3d368e77c449c287430.jpg"

async def stream(
    _,
    mystic,
    user_id,
    result,
    chat_id,
    user_name,
    original_chat_id,
    video: Union[bool, str] = None,
    streamtype: Union[bool, str] = None,
    spotify: Union[bool, str] = None,
    forceplay: Union[bool, str] = None,
):
    if not result:
        return
    if forceplay:
        # ✅ FIX: Changed 'force_stop_stream' to 'stop_stream'
        await Lucky.stop_stream(chat_id)

    # ==========================================
    # PLAYLIST STREAM TYPE
    # ==========================================
    if streamtype == "playlist":
        msg = f"{_['play_19']}\n\n"
        count = 0
        for search in result:
            if int(count) == config.PLAYLIST_FETCH_LIMIT:
                continue
            try:
                (
                    title,
                    duration_min,
                    duration_sec,
                    thumbnail,
                    vidid,
                ) = await YouTube.details(search, False if spotify else True)
            except:
                continue
            if str(duration_min) == "None":
                continue
            if duration_sec > config.DURATION_LIMIT:
                continue
            if await is_active_chat(chat_id):
                await put_queue(
                    chat_id, original_chat_id, f"vid_{vidid}", title, duration_min, user_name, vidid, user_id, "video" if video else "audio",
                )
                position = len(db.get(chat_id)) - 1
                count += 1
                msg += f"{count}. {title[:70]}\n{_['play_20']} {position}\n\n"
            else:
                if not forceplay:
                    db[chat_id] = []
                status = True if video else None
                try:
                    file_path, direct = await YouTube.download(vidid, mystic, video=status, videoid=True)
                except:
                    raise AssistantErr(_["play_14"])
                
                # ✅ FIX: Handle silent download failure
                if not file_path or str(file_path) == "None":
                    raise AssistantErr(_["play_14"])

                await Lucky.join_call(chat_id, original_chat_id, file_path, video=status, image=thumbnail)
                await put_queue(
                    chat_id, original_chat_id, file_path if direct else f"vid_{vidid}", title, duration_min, user_name, vidid, user_id, "video" if video else "audio", forceplay=forceplay,
                )
                
                # ✅ FIXED: Missing thumbnail fallback
                img = await get_thumb(vidid, user_id, app)
                if not img: img = get_random_img(config.PLAYLIST_IMG_URL)

                button = stream_markup(_, chat_id)
                run = await app.send_photo(
                    original_chat_id, photo=img, caption=_["stream_1"].format(f"https://t.me/{app.username}?start=info_{vidid}", title[:23], duration_min, user_name),
                    reply_markup=InlineKeyboardMarkup(button), has_spoiler=False
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "stream"
        if count == 0: return
        else:
            link = await LuckyBin(msg)
            lines = msg.count("\n")
            car = os.linesep.join(msg.split(os.linesep)[:17]) if lines >= 17 else msg
            carbon = await Carbon.generate(car, random.randint(100, 10000000))
            return await app.send_photo(original_chat_id, photo=carbon, caption=_["play_21"].format(position, link), reply_markup=close_markup(_), has_spoiler=False)

    # ==========================================
    # YOUTUBE STREAM TYPE
    # ==========================================
    elif streamtype == "youtube":
        link, vidid, title, duration_min, thumbnail = result["link"], result["vidid"], (result["title"]).title(), result["duration_min"], result["thumb"]
        status = True if video else None
        try:
            file_path, direct = await YouTube.download(vidid, mystic, videoid=True, video=status)
        except:
            raise AssistantErr(_["play_14"])
        
        # ✅ FIX: Handle silent download failure
        if not file_path or str(file_path) == "None":
            raise AssistantErr(_["play_14"])
        
        if await is_active_chat(chat_id):
            await put_queue(chat_id, original_chat_id, file_path if direct else f"vid_{vidid}", title, duration_min, user_name, vidid, user_id, "video" if video else "audio")
            position = len(db.get(chat_id)) - 1
            await app.send_message(chat_id=original_chat_id, text=_["queue_4"].format(position, title[:27], duration_min, user_name), reply_markup=InlineKeyboardMarkup(aq_markup(_, chat_id)))
        else:
            if not forceplay: db[chat_id] = []
            await Lucky.join_call(chat_id, original_chat_id, file_path, video=status, image=thumbnail)
            await put_queue(chat_id, original_chat_id, file_path if direct else f"vid_{vidid}", title, duration_min, user_name, vidid, user_id, "video" if video else "audio", forceplay=forceplay)
            
            # ✅ FIXED: Missing thumbnail fallback
            img = await get_thumb(vidid, user_id, app)
            if not img: img = get_random_img(config.PLAYLIST_IMG_URL)

            run = await app.send_photo(original_chat_id, photo=img, caption=_["stream_1"].format(f"https://t.me/{app.username}?start=info_{vidid}", title[:23], duration_min, user_name), reply_markup=InlineKeyboardMarkup(stream_markup(_, chat_id)), has_spoiler=False)
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "stream"

    # ==========================================
    # LIVE STREAM TYPE
    # ==========================================
    elif streamtype == "live":
        link, vidid, title, thumbnail = result["link"], result["vidid"], (result["title"]).title(), result["thumb"]
        duration_min = "Live Track"
        status = True if video else None
        if await is_active_chat(chat_id):
            await put_queue(chat_id, original_chat_id, f"live_{vidid}", title, duration_min, user_name, vidid, user_id, "video" if video else "audio")
            position = len(db.get(chat_id)) - 1
            await app.send_message(chat_id=original_chat_id, text=_["queue_4"].format(position, title[:27], duration_min, user_name), reply_markup=InlineKeyboardMarkup(aq_markup(_, chat_id)))
        else:
            if not forceplay: db[chat_id] = []
            n, file_path = await YouTube.video(link)
            
            # ✅ FIX: Handle verification for both stream validation
            if n == 0 or not file_path or str(file_path) == "None": 
                raise AssistantErr(_["str_3"])
                
            await Lucky.join_call(chat_id, original_chat_id, file_path, video=status, image=thumbnail if thumbnail else None)
            await put_queue(chat_id, original_chat_id, f"live_{vidid}", title, duration_min, user_name, vidid, user_id, "video" if video else "audio", forceplay=forceplay)
            
            # ✅ FIXED: Missing thumbnail fallback
            img = await get_thumb(vidid, user_id, app)
            if not img: img = get_random_img(config.PLAYLIST_IMG_URL)

            run = await app.send_photo(original_chat_id, photo=img, caption=_["stream_1"].format(f"https://t.me/{app.username}?start=info_{vidid}", title[:23], duration_min, user_name), reply_markup=InlineKeyboardMarkup(stream_markup(_, chat_id)), has_spoiler=False)
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"
