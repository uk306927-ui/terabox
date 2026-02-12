from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests

# ================== CONFIG ==================

BOT_TOKEN = "8556835870:AAEfpftWDjz6vQ7PNxsjIncyHplTlVQ5mRw"

API_ID = 21493021
API_HASH = "724cd4ff94207025989137657bc78761"

TERABOX_API = "https://xapiverse.com/api/terabox"
TERABOX_KEY = "sk_444eaefa85e98c1c3136a7f8c002e18b"

# 🔥 TG DUMP GROUP (BOT MUST BE ADMIN HERE)
DUMP_GROUP = -1003754300096

# JOIN BUTTON LINKS (COSMETIC ONLY)
MAIN_GROUP_LINK = "https://t.me/apnahub69"
STACK_GROUP_LINK = "https://t.me/eldersMAH"

# ============================================

app = Client(
    "terabox_bot",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)

# /start
@app.on_message(filters.command("start") & filters.private)
def start(client, message):
    message.reply(
        "👋 **Welcome to TeraBox Bot**\n\n"
        "🚨 *Bot use karne ke liye groups join karna zaroori hai*\n"
        "Join karke **Verify Join** dabao 👇",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Join Main Group", url=MAIN_GROUP_LINK)],
            [InlineKeyboardButton("📂 Join Stack Group", url=STACK_GROUP_LINK)],
            [InlineKeyboardButton("✅ Verify Join", callback_data="verify_join")]
        ])
    )

# Verify Join (COSMETIC)
@app.on_callback_query(filters.regex("verify_join"))
def verify_join(client, query):
    query.message.edit_text(
        "✅ **Verified!**\n\n"
        "Ab apna **TeraBox link bhejo** 👇"
    )

# Main handler
@app.on_message(filters.private & filters.text & ~filters.command("start"))
def handle_message(client, message):
    text = message.text.strip()

    if "terabox" not in text.lower():
        message.reply("❌ **Valid TeraBox link bhejo**")
        return

    status = message.reply("⏳ **Processing your TeraBox link...**")

    # API call
    try:
        r = requests.post(
            TERABOX_API,
            json={"url": text},
            headers={
                "Content-Type": "application/json",
                "xAPIverse-Key": TERABOX_KEY
            },
            timeout=30
        )
        data = r.json()
    except:
        status.edit("❌ API error. Try again later.")
        return

    if data.get("status") != "success" or not data.get("list"):
        status.edit("❌ Video fetch nahi ho paya.")
        return

    file = data["list"][0]

    # ---------- Buttons ----------
    buttons = []

    stream_urls = file.get("fast_stream_url") or {}
    if isinstance(stream_urls, dict):
        for q, link in stream_urls.items():
            if link:
                buttons.append(
                    [InlineKeyboardButton(f"▶ Stream {q}", url=link)]
                )

    if file.get("fast_download_link"):
        buttons.append(
            [InlineKeyboardButton("⬇ Download", url=file["fast_download_link"])]
        )

    keyboard = InlineKeyboardMarkup(buttons) if buttons else None

    caption = (
        f"🎬 **{file['name']}**\n"
        f"⏱ Duration: {file.get('duration', 'N/A')}\n"
        f"📦 Size: {file.get('size_formatted', 'N/A')}\n\n"
        f"👇 Stream / Download below"
    )

    # 🔹 SEND TO USER
    client.send_photo(
        chat_id=message.chat.id,
        photo=file["thumbnail"],
        caption=caption,
        reply_markup=keyboard
    )

    # 🔹 DUMP TO TG GROUP (COMMON FOLDER)
    client.send_photo(
        chat_id=DUMP_GROUP,
        photo=file["thumbnail"],
        caption=caption,
        reply_markup=keyboard
    )

    status.delete()

print("✅ Starting TeraBox Bot (TG DUMP MODE)...")
app.run()
