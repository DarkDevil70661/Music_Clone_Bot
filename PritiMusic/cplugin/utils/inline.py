from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# --- OPTION 1: Static ---
buttons = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text="▷", callback_data="resume_cb"),
            InlineKeyboardButton(text="II", callback_data="pause_cb"),
            InlineKeyboardButton(text="‣‣I", callback_data="skip_cb"),
            InlineKeyboardButton(text="▢", callback_data="end_cb"),
        ],
        [
            InlineKeyboardButton(text="❖ 𝐂ʟᴏηє 𝐍ᴏᴡ ❖", url="https://t.me/Music_Clone1_Bot")
        ],
    ]
)

close_key = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text="❖ 𝐂ʟᴏsє ❖", callback_data="close")
        ]
    ]
)

# --- OPTION 2: Dynamic (RECOMMENDED) ---
def stream_markup(chat_id):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}"),
                InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
                InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
                InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
            ],
            [
                InlineKeyboardButton(text="❖ 𝐂ʟᴏηє 𝐍ᴏᴡ ❖", url="https://t.me/Music_Clone1_Bot")
            ],
            [
                InlineKeyboardButton(text="❖ 𝐂ʟᴏsє ❖", callback_data="close")
            ]
        ]
    )
