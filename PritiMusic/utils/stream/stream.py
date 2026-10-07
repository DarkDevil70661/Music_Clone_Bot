import os
import random
import asyncio
from typing import Union

from pyrogram.types import InlineKeyboardMarkup

import config
from PritiMusic import Carbon, YouTube, app
from PritiMusic.core.call import Lucky
from PritiMusic.misc import db
from PritiMusic.utils.database import is_active_chat
from PritiMusic.utils.exceptions import AssistantErr
from PritiMusic.utils.inline import aq_markup, close_markup, stream_markup
from PritiMusic.utils.stream.queue import put_queue
from PritiMusic.utils.pastebin import LuckyBin
from PritiMusic.utils.thumbnails import get_thumb


# ==========================================================
# RANDOM IMAGE
# ==========================================================

def get_random_img(img_list):
    if img_list:
        if isinstance(img_list, (list, tuple)):
            try:
                return random.choice(img_list)
            except Exception:
                pass

        return img_list

    return "https://telegra.ph/file/2e3d368e77c449c287430.jpg"


# ==========================================================
# CHECK MEDIA STREAMS USING FFPROBE
# ==========================================================

async def _ffprobe_streams(file_path: str):
    """
    Check whether a local media file contains
    audio and/or video streams.

    Returns:
        (has_audio, has_video)
    """

    if not file_path:
        return False, False

    if not os.path.isfile(file_path):
        return False, False

    try:
        # --------------------------------------------------
        # AUDIO
        # --------------------------------------------------

        process = await asyncio.create_subprocess_exec(
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a",
            "-show_entries",
            "stream=index",
            "-of",
            "csv=p=0",
            file_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        audio_output, _ = await process.communicate()

        has_audio = bool(audio_output.strip())

        # --------------------------------------------------
        # VIDEO
        # --------------------------------------------------

        process = await asyncio.create_subprocess_exec(
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v",
            "-show_entries",
            "stream=index",
            "-of",
            "csv=p=0",
            file_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        video_output, _ = await process.communicate()

        has_video = bool(video_output.strip())

        return has_audio, has_video

    except (FileNotFoundError, OSError):
        # ffprobe itself is missing
        return False, False

    except Exception:
        return False, False


# ==========================================================
# PREPARE MEDIA
# ==========================================================

async def _prepare_media(file_path, video=False):
    """
    Validate a downloaded media source.

    For audio playback:
        If a video file has audio, use it.
        If the file has no audio but contains video,
        attempt to extract an MP3 audio track.

    For video playback:
        The file must contain both video and audio.

    Remote URLs are returned directly.
    """

    if not file_path:
        return None

    raw_path = str(file_path).strip()

    if raw_path.lower() in {
        "none",
        "false",
        "null",
        "0",
        "",
    }:
        return None

    # ------------------------------------------------------
    # REMOTE STREAM
    # ------------------------------------------------------

    remote_prefixes = (
        "http://",
        "https://",
        "rtmp://",
        "rtmps://",
    )

    if raw_path.startswith(remote_prefixes):
        return raw_path

    # ------------------------------------------------------
    # LOCAL FILE
    # ------------------------------------------------------

    path = os.path.abspath(os.path.expanduser(raw_path))

    if not os.path.isfile(path):
        return None

    try:
        if os.path.getsize(path) <= 0:
            return None
    except OSError:
        return None

    # ------------------------------------------------------
    # CHECK AUDIO / VIDEO
    # ------------------------------------------------------

    has_audio, has_video = await _ffprobe_streams(path)

    # ------------------------------------------------------
    # NORMAL AUDIO FILE
    # ------------------------------------------------------

    if has_audio and not video:
        return path

    # ------------------------------------------------------
    # NORMAL VIDEO FILE
    # ------------------------------------------------------

    if has_audio and has_video and video:
        return path

    # ------------------------------------------------------
    # AUDIO PLAYBACK BUT AUDIO STREAM IS MISSING
    # ------------------------------------------------------

    if not video and has_video and not has_audio:

        base, _ = os.path.splitext(path)

        repaired = f"{base}_audio.mp3"

        try:
            process = await asyncio.create_subprocess_exec(
                "ffmpeg",
                "-y",
                "-i",
                path,
                "-vn",
                "-map",
                "0:a:0",
                "-c:a",
                "libmp3lame",
                "-b:a",
                "192k",
                repaired,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.PIPE,
            )

            _, stderr = await process.communicate()

            if (
                process.returncode == 0
                and os.path.isfile(repaired)
                and os.path.getsize(repaired) > 0
            ):
                repaired_audio, _ = await _ffprobe_streams(
                    repaired
                )

                if repaired_audio:
                    return repaired

        except (FileNotFoundError, OSError):
            pass

        except Exception:
            pass

    # ------------------------------------------------------
    # INVALID MEDIA
    # ------------------------------------------------------

    return None


# ==========================================================
# DOWNLOAD + VALIDATE MEDIA
# ==========================================================

async def _download_media(
    vidid,
    mystic,
    video=False,
    error_text=None,
):
    """
    Download YouTube media and validate it before
    sending it to PyTgCalls.
    """

    try:
        file_path, direct = await YouTube.download(
            vidid,
            mystic,
            video=video,
            videoid=True,
        )

    except Exception as e:
        print(
            f"[YouTube Download Error] {type(e).__name__}: {e}"
        )

        if error_text:
            raise AssistantErr(error_text)

        raise AssistantErr(
            "Failed to download the requested track."
        )

    if not file_path:
        if error_text:
            raise AssistantErr(error_text)

        raise AssistantErr(
            "Failed to download the requested track."
        )

    # ------------------------------------------------------
    # VALIDATE / REPAIR MEDIA
    # ------------------------------------------------------

    prepared = await _prepare_media(
        file_path,
        video=video,
    )

    if not prepared:

        print(
            "[Media Error] Downloaded source has no "
            "usable audio/video stream."
        )

        if error_text:
            raise AssistantErr(error_text)

        raise AssistantErr(
            "Downloaded media has no usable audio source."
        )

    return prepared, direct


# ==========================================================
# THUMBNAIL
# ==========================================================

async def _get_thumbnail(vidid, user_id):

    try:
        image = await get_thumb(
            vidid,
            user_id,
            app,
        )

        if image:
            return image

    except Exception as e:
        print(
            f"[Thumbnail Error] {type(e).__name__}: {e}"
        )

    return get_random_img(
        config.PLAYLIST_IMG_URL
    )


# ==========================================================
# MAIN STREAM FUNCTION
# ==========================================================

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

    # ======================================================
    # FORCE PLAY
    # ======================================================

    if forceplay:
        try:
            await Lucky.stop_stream(chat_id)
        except Exception as e:
            print(
                f"[Stop Stream Error] {type(e).__name__}: {e}"
            )

    # ======================================================
    # PLAYLIST
    # ======================================================

    if streamtype == "playlist":

        msg = f"{_['play_19']}\n\n"

        count = 0
        position = 0

        for search in result:

            # ------------------------------------------------
            # PLAYLIST LIMIT
            # ------------------------------------------------

            if count >= config.PLAYLIST_FETCH_LIMIT:
                break

            # ------------------------------------------------
            # GET DETAILS
            # ------------------------------------------------

            try:
                (
                    title,
                    duration_min,
                    duration_sec,
                    thumbnail,
                    vidid,
                ) = await YouTube.details(
                    search,
                    False if spotify else True,
                )

            except Exception as e:

                print(
                    f"[Playlist Details Error] "
                    f"{type(e).__name__}: {e}"
                )

                continue

            # ------------------------------------------------
            # INVALID DURATION
            # ------------------------------------------------

            if str(duration_min) == "None":
                continue

            if duration_sec is None:
                continue

            try:
                if duration_sec > config.DURATION_LIMIT:
                    continue
            except Exception:
                continue

            # ------------------------------------------------
            # ACTIVE CHAT
            # ------------------------------------------------

            if await is_active_chat(chat_id):

                await put_queue(
                    chat_id,
                    original_chat_id,
                    f"vid_{vidid}",
                    title,
                    duration_min,
                    user_name,
                    vidid,
                    user_id,
                    "video" if video else "audio",
                )

                position = len(
                    db.get(chat_id)
                ) - 1

                count += 1

                msg += (
                    f"{count}. "
                    f"{title[:70]}\n"
                    f"{_['play_20']} "
                    f"{position}\n\n"
                )

                continue

            # ------------------------------------------------
            # NEW STREAM
            # ------------------------------------------------

            if not forceplay:
                db[chat_id] = []

            status = True if video else False

            try:

                file_path, direct = await _download_media(
                    vidid,
                    mystic,
                    video=status,
                    error_text=_["play_14"],
                )

            except AssistantErr:
                raise

            except Exception as e:

                print(
                    f"[Playlist Download Error] "
                    f"{type(e).__name__}: {e}"
                )

                raise AssistantErr(
                    _["play_14"]
                )

            # ------------------------------------------------
            # JOIN VOICE CHAT
            # ------------------------------------------------

            try:

                await Lucky.join_call(
                    chat_id,
                    original_chat_id,
                    file_path,
                    video=status,
                    image=thumbnail,
                )

            except Exception as e:

                print(
                    f"[Playlist JoinCall Error] "
                    f"{type(e).__name__}: {e}"
                )

                raise

            # ------------------------------------------------
            # QUEUE
            # ------------------------------------------------

            await put_queue(
                chat_id,
                original_chat_id,
                file_path
                if direct
                else f"vid_{vidid}",
                title,
                duration_min,
                user_name,
                vidid,
                user_id,
                "video" if video else "audio",
                forceplay=forceplay,
            )

            # ------------------------------------------------
            # THUMBNAIL
            # ------------------------------------------------

            img = await _get_thumbnail(
                vidid,
                user_id,
            )

            # ------------------------------------------------
            # SEND NOW PLAYING
            # ------------------------------------------------

            run = await app.send_photo(
                original_chat_id,
                photo=img,
                caption=_["stream_1"].format(
                    f"https://t.me/"
                    f"{app.username}"
                    f"?start=info_{vidid}",
                    title[:23],
                    duration_min,
                    user_name,
                ),
                reply_markup=InlineKeyboardMarkup(
                    stream_markup(
                        _,
                        chat_id,
                    )
                ),
                has_spoiler=False,
            )

            # ------------------------------------------------
            # UPDATE DATABASE
            # ------------------------------------------------

            if db.get(chat_id):

                db[chat_id][0][
                    "mystic"
                ] = run

                db[chat_id][0][
                    "markup"
                ] = "stream"

        # ----------------------------------------------------
        # NO TRACKS
        # ----------------------------------------------------

        if count == 0:
            return

        # ----------------------------------------------------
        # PLAYLIST RESULT
        # ----------------------------------------------------

        link = await LuckyBin(msg)

        lines = msg.count("\n")

        if lines >= 17:

            car = os.linesep.join(
                msg.split(os.linesep)[:17]
            )

        else:
            car = msg

        carbon = await Carbon.generate(
            car,
            random.randint(
                100,
                10000000,
            ),
        )

        return await app.send_photo(
            original_chat_id,
            photo=carbon,
            caption=_["play_21"].format(
                position,
                link,
            ),
            reply_markup=close_markup(_),
            has_spoiler=False,
        )

    # ======================================================
    # YOUTUBE
    # ======================================================

    elif streamtype == "youtube":

        link = result["link"]

        vidid = result["vidid"]

        title = (
            result["title"]
        ).title()

        duration_min = result[
            "duration_min"
        ]

        thumbnail = result[
            "thumb"
        ]

        status = True if video else False

        # --------------------------------------------------
        # DOWNLOAD
        # --------------------------------------------------

        try:

            file_path, direct = await _download_media(
                vidid,
                mystic,
                video=status,
                error_text=_["play_14"],
            )

        except AssistantErr:
            raise

        except Exception as e:

            print(
                f"[YouTube Stream Error] "
                f"{type(e).__name__}: {e}"
            )

            raise AssistantErr(
                _["play_14"]
            )

        # --------------------------------------------------
        # ACTIVE CHAT
        # --------------------------------------------------

        if await is_active_chat(chat_id):

            await put_queue(
                chat_id,
                original_chat_id,
                file_path
                if direct
                else f"vid_{vidid}",
                title,
                duration_min,
                user_name,
                vidid,
                user_id,
                "video" if video else "audio",
            )

            position = len(
                db.get(chat_id)
            ) - 1

            await app.send_message(
                chat_id=original_chat_id,
                text=_["queue_4"].format(
                    position,
                    title[:27],
                    duration_min,
                    user_name,
                ),
                reply_markup=InlineKeyboardMarkup(
                    aq_markup(
                        _,
                        chat_id,
                    )
                ),
            )

        # --------------------------------------------------
        # START NEW STREAM
        # --------------------------------------------------

        else:

            if not forceplay:
                db[chat_id] = []

            try:

                await Lucky.join_call(
                    chat_id,
                    original_chat_id,
                    file_path,
                    video=status,
                    image=thumbnail,
                )

            except Exception as e:

                print(
                    f"[YouTube JoinCall Error] "
                    f"{type(e).__name__}: {e}"
                )

                raise

            # ------------------------------------------------
            # ADD QUEUE
            # ------------------------------------------------

            await put_queue(
                chat_id,
                original_chat_id,
                file_path
                if direct
                else f"vid_{vidid}",
                title,
                duration_min,
                user_name,
                vidid,
                user_id,
                "video" if video else "audio",
                forceplay=forceplay,
            )

            # ------------------------------------------------
            # THUMBNAIL
            # ------------------------------------------------

            img = await _get_thumbnail(
                vidid,
                user_id,
            )

            # ------------------------------------------------
            # NOW PLAYING
            # ------------------------------------------------

            run = await app.send_photo(
                original_chat_id,
                photo=img,
                caption=_["stream_1"].format(
                    f"https://t.me/"
                    f"{app.username}"
                    f"?start=info_{vidid}",
                    title[:23],
                    duration_min,
                    user_name,
                ),
                reply_markup=InlineKeyboardMarkup(
                    stream_markup(
                        _,
                        chat_id,
                    )
                ),
                has_spoiler=False,
            )

            # ------------------------------------------------
            # DATABASE
            # ------------------------------------------------

            if db.get(chat_id):

                db[chat_id][0][
                    "mystic"
                ] = run

                db[chat_id][0][
                    "markup"
                ] = "stream"

    # ======================================================
    # LIVE STREAM
    # ======================================================

    elif streamtype == "live":

        link = result["link"]

        vidid = result["vidid"]

        title = (
            result["title"]
        ).title()

        thumbnail = result["thumb"]

        duration_min = "Live Track"

        status = True if video else False

        # --------------------------------------------------
        # ACTIVE CHAT
        # --------------------------------------------------

        if await is_active_chat(chat_id):

            await put_queue(
                chat_id,
                original_chat_id,
                f"live_{vidid}",
                title,
                duration_min,
                user_name,
                vidid,
                user_id,
                "video" if video else "audio",
            )

            position = len(
                db.get(chat_id)
            ) - 1

            await app.send_message(
                chat_id=original_chat_id,
                text=_["queue_4"].format(
                    position,
                    title[:27],
                    duration_min,
                    user_name,
                ),
                reply_markup=InlineKeyboardMarkup(
                    aq_markup(
                        _,
                        chat_id,
                    )
                ),
            )

        # --------------------------------------------------
        # START LIVE
        # --------------------------------------------------

        else:

            if not forceplay:
                db[chat_id] = []

            try:

                n, file_path = await YouTube.video(
                    link
                )

            except Exception as e:

                print(
                    f"[Live Stream Error] "
                    f"{type(e).__name__}: {e}"
                )

                raise AssistantErr(
                    _["str_3"]
                )

            # ------------------------------------------------
            # INVALID LIVE SOURCE
            # ------------------------------------------------

            if (
                n == 0
                or not file_path
                or str(file_path) == "None"
            ):

                raise AssistantErr(
                    _["str_3"]
                )

            # ------------------------------------------------
            # LOCAL LIVE FILE
            # ------------------------------------------------

            if not str(file_path).startswith(
                (
                    "http://",
                    "https://",
                    "rtmp://",
                    "rtmps://",
                )
            ):

                prepared = await _prepare_media(
                    file_path,
                    video=status,
                )

                if not prepared:

                    raise AssistantErr(
                        _["str_3"]
                    )

                file_path = prepared

            # ------------------------------------------------
            # JOIN LIVE CALL
            # ------------------------------------------------

            try:

                await Lucky.join_call(
                    chat_id,
                    original_chat_id,
                    file_path,
                    video=status,
                    image=(
                        thumbnail
                        if thumbnail
                        else None
                    ),
                )

            except Exception as e:

                print(
                    f"[Live JoinCall Error] "
                    f"{type(e).__name__}: {e}"
                )

                raise

            # ------------------------------------------------
            # QUEUE
            # ------------------------------------------------

            await put_queue(
                chat_id,
                original_chat_id,
                f"live_{vidid}",
                title,
                duration_min,
                user_name,
                vidid,
                user_id,
                "video" if video else "audio",
                forceplay=forceplay,
            )

            # ------------------------------------------------
            # THUMBNAIL
            # ------------------------------------------------

            img = await _get_thumbnail(
                vidid,
                user_id,
            )

            # ------------------------------------------------
            # NOW PLAYING
            # ------------------------------------------------

            run = await app.send_photo(
                original_chat_id,
                photo=img,
                caption=_["stream_1"].format(
                    f"https://t.me/"
                    f"{app.username}"
                    f"?start=info_{vidid}",
                    title[:23],
                    duration_min,
                    user_name,
                ),
                reply_markup=InlineKeyboardMarkup(
                    stream_markup(
                        _,
                        chat_id,
                    )
                ),
                has_spoiler=False,
            )

            # ------------------------------------------------
            # DATABASE
            # ------------------------------------------------

            if db.get(chat_id):

                db[chat_id][0][
                    "mystic"
                ] = run

                db[chat_id][0][
                    "markup"
                ] = "tg"
