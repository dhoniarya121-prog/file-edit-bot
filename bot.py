import logging
import os
import re

from telegram import Update
from telegram.error import BadRequest
from telegram.ext import Application, ContextTypes, MessageHandler, filters

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.INFO
)
log = logging.getLogger("cleaner-bot")

TOKEN = os.environ["BOT_TOKEN"]
PORT = int(os.environ.get("PORT", "10000"))
BASE_URL = os.environ.get("RENDER_EXTERNAL_URL") or os.environ.get("WEBHOOK_URL", "")


def flag(name: str, default: str = "true") -> bool:
    return os.environ.get(name, default).strip().lower() in ("1", "true", "yes", "on")


def csv(name: str) -> list[str]:
    return [x.strip() for x in os.environ.get(name, "").split(",") if x.strip()]


# ---- Settings (Render dashboard > Environment se badal sakte ho) ----
REMOVE_LINKS = flag("REMOVE_LINKS")            # http/https/t.me/www links + hyperlinks
REMOVE_MENTIONS = flag("REMOVE_MENTIONS")      # @username
REMOVE_HASHTAGS = flag("REMOVE_HASHTAGS")      # #tag
REMOVE_EMOJI_SPAM = flag("REMOVE_EMOJI_SPAM", "false")  # lagataar repeat emojis
DELETE_IF_EMPTY = flag("DELETE_IF_EMPTY", "false")      # text khali ho jaye to post delete
BLOCKED_WORDS = csv("BLOCKED_WORDS")           # in words wali poori line hat jayegi
REMOVE_PHRASES = csv("REMOVE_PHRASES")         # sirf ye phrase hatega, line rahegi
ALLOWED_CHANNELS = {int(x) for x in csv("ALLOWED_CHANNELS")}  # khali = sab channels

LINK_TAG = re.compile(r"<a\b[^>]*>.*?</a>", re.I | re.S)
URL = re.compile(r"(?:https?://|www\.|t\.me/|telegram\.me/)\S+", re.I)
MENTION = re.compile(r"(?<!\w)@\w{3,}")
HASHTAG = re.compile(r"(?<!\w)#\w+")
REPEAT_CHAR = re.compile(r"(\S)\1{3,}")


def clean(html: str) -> str:
    text = html

    if REMOVE_LINKS:
        text = LINK_TAG.sub("", text)
        text = URL.sub("", text)
    if REMOVE_MENTIONS:
        text = MENTION.sub("", text)
    if REMOVE_HASHTAGS:
        text = HASHTAG.sub("", text)
    if REMOVE_EMOJI_SPAM:
        text = REPEAT_CHAR.sub(r"\1", text)

    for phrase in REMOVE_PHRASES:
        text = re.sub(re.escape(phrase), "", text, flags=re.I)

    lines = text.split("\n")
    if BLOCKED_WORDS:
        lines = [
            ln for ln in lines if not any(w.lower() in ln.lower() for w in BLOCKED_WORDS)
        ]

    # extra spaces aur khali lines saaf karo
    lines = [re.sub(r"[ \t]{2,}", " ", ln).strip() for ln in lines]
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text


async def on_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.channel_post
    if not msg:
        return
    if ALLOWED_CHANNELS and msg.chat_id not in ALLOWED_CHANNELS:
        return

    is_text = msg.text is not None
    original = msg.text_html if is_text else msg.caption_html
    if not original:
        return  # bina text/caption wala media

    cleaned = clean(original)
    if cleaned == original.strip():
        return  # kuch badla nahi

    try:
        if not cleaned:
            if DELETE_IF_EMPTY:
                await msg.delete()
            return
        if is_text:
            await msg.edit_text(
                cleaned, parse_mode="HTML", disable_web_page_preview=True
            )
        else:
            await msg.edit_caption(caption=cleaned, parse_mode="HTML")
        log.info("Edited message %s in chat %s", msg.message_id, msg.chat_id)
    except BadRequest as e:
        if "not modified" not in str(e).lower():
            log.warning("Edit failed: %s", e)


def main():
    app = Application.builder().token(TOKEN).build()
    # sirf naye posts; edited posts ignore (infinite loop se bachne ke liye)
    app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, on_channel_post))

    if BASE_URL:
        log.info("Starting webhook on port %s", PORT)
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=f"{BASE_URL.rstrip('/')}/{TOKEN}",
            allowed_updates=["channel_post"],
            drop_pending_updates=True,
        )
    else:
        log.info("Local mode: polling")
        app.run_polling(allowed_updates=["channel_post"], drop_pending_updates=True)


if __name__ == "__main__":
    main()
