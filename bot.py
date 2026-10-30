import os
import re
import logging
import threading

from fastapi import FastAPI
import uvicorn

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "Lanat_Ba_To_Lanati").strip().lstrip("@").lower()
ADMIN_CHAT_ID_RAW = os.getenv("ADMIN_CHAT_ID", "8545093827").strip()
try:
    ADMIN_CHAT_ID = int(ADMIN_CHAT_ID_RAW) if ADMIN_CHAT_ID_RAW else None
except ValueError:
    ADMIN_CHAT_ID = None

BOT_NAME = os.getenv("BOT_NAME", "Arshia Danesh").strip()
OWNER_NAME = os.getenv("OWNER_NAME", "عرشیا دانش").strip()
OWNER_USERNAME = "@" + ADMIN_USERNAME
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/AR_Better").strip()
PORT = int(os.getenv("PORT", "10000"))

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing. Add the new BotFather token in Render Environment Variables.")

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
web_app = FastAPI()

@web_app.get("/")
async def home():
    return {"status": "online", "bot": BOT_NAME}

@web_app.get("/health")
async def health():
    return {"status": "ok", "bot": BOT_NAME}

def run_web_server():
    uvicorn.run(web_app, host="0.0.0.0", port=PORT, log_level="warning")

def is_admin(user):
    if not user:
        return False
    if ADMIN_CHAT_ID is not None:
        return user.id == ADMIN_CHAT_ID
    return (user.username or "").strip().lower() == ADMIN_USERNAME

def main_menu():
    keyboard = [
        ["👤 درباره عرشیا", "💌 پیام به عرشیا"],
        ["🤖 درباره ربات", "❓ راهنما"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)

def channel_button():
    return InlineKeyboardMarkup([[InlineKeyboardButton("📢 کانال عرشیا", url=CHANNEL_URL)]])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ADMIN_CHAT_ID
    if not update.message or not update.effective_user:
        return
    if is_admin(update.effective_user):
        ADMIN_CHAT_ID = update.effective_chat.id
        logger.info("Admin detected. Chat ID: %s", ADMIN_CHAT_ID)
    context.user_data["waiting_message"] = False
    await update.message.reply_text(
        "سلام، خوش اومدی! 🖤\n\n"
        "به فضای شخصی عرشیا دانش خوش اومدی.\n\n"
        "اینجا می‌تونی درباره عرشیا بیشتر بدونی، مستقیم براش پیام بفرستی "
        "و به کانالش سر بزنی.\n\n"
        "از منوی پایین، بخش موردنظرت رو انتخاب کن. 🤍",
        reply_markup=channel_button(),
    )
    await update.message.reply_text("منوی اصلی | عرشیا دانش", reply_markup=main_menu())

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    await update.message.reply_text(
        "👤 درباره عرشیا\n\n"
        "〘 عرشیا دانش 〙\n\n"
        "نام: عرشیا دانش\n"
        "Username: @Lanat_Ba_To_Lanati\n"
        "شناسه کاربری: 8545093827\n"
        "کانال: @AR_Better\n\n"
        "برای ارتباط مستقیم، گزینهٔ «💌 پیام به عرشیا» رو انتخاب کن. 🤍",
        reply_markup=main_menu(),
    )

async def about_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    await update.message.reply_text(
        "🤖 درباره ربات\n\n"
        "این ربات راه ارتباط مستقیم با عرشیا دانش است.\n\n"
        "می‌تونی متن، عکس، ویدیو، فایل یا پیام صوتی بفرستی؛ "
        "پیامت برای مدیر ربات ارسال می‌شه و امکان پاسخ مستقیم وجود داره.\n\n"
        "ساده، شخصی و برای ارتباط راحت‌تر طراحی شده.\n\n"
        "⚙️ مدیریت: @Lanat_Ba_To_Lanati",
        reply_markup=main_menu(),
    )

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    await update.message.reply_text(
        "❓ راهنمای استفاده\n\n"
        "👤 درباره عرشیا — نمایش اطلاعات عرشیا.\n"
        "💌 پیام به عرشیا — ارسال متن، عکس، ویدیو، فایل یا ویس.\n"
        "🤖 درباره ربات — آشنایی با امکانات ربات.\n"
        "📢 کانال عرشیا — ورود به کانال رسمی.\n\n"
        "برای لغو ارسال پیام و برگشت به منو، /start را بزن.",
        reply_markup=main_menu(),
    )

async def my_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user or not is_admin(update.effective_user):
        return
    await update.message.reply_text(
        "🆔 اطلاعات شما\n\n"
        f"User ID: {update.effective_user.id}\n"
        f"Chat ID: {update.effective_chat.id}"
    )

async def start_sending(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    context.user_data["waiting_message"] = True
    await update.message.reply_text(
        "💌 پیامت رو برای عرشیا بفرست.\n\n"
        "می‌تونی متن، عکس، ویدیو، فایل یا ویس ارسال کنی.\n"
        "پیامت مستقیماً برای مدیر ربات فرستاده می‌شه.\n\n"
        "برای لغو و برگشت به منوی اصلی، /start رو بزن.",
        reply_markup=main_menu(),
    )

async def send_user_message_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user:
        return
    if ADMIN_CHAT_ID is None:
        await update.message.reply_text(
            "⚠️ مدیر هنوز ربات را فعال نکرده است. لطفاً عرشیا یک‌بار وارد ربات شود و /start را بزند."
        )
        return
    user = update.effective_user
    username_text = f"@{user.username}" if user.username else "ندارد"
    header = (
        "📩 پیام جدید از کاربر\n\n"
        f"👤 نام: {user.full_name}\n"
        f"🔹 Username: {username_text}\n"
        f"🆔 User ID: {user.id}\n\n"
        "↩️ برای پاسخ دادن، روی همین پیام Reply بزن."
    )
    try:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=header)
        await update.message.copy(chat_id=ADMIN_CHAT_ID)
        context.user_data["waiting_message"] = False
        await update.message.reply_text("✅ پیامت با موفقیت برای عرشیا ارسال شد.", reply_markup=main_menu())
    except Exception:
        logger.exception("Could not send user message to admin.")
        await update.message.reply_text("❌ ارسال پیام انجام نشد. لطفاً کمی بعد دوباره امتحان کن.", reply_markup=main_menu())

def extract_user_id_from_admin_message(message):
    if not message.reply_to_message:
        return None
    replied_text = message.reply_to_message.text or message.reply_to_message.caption or ""
    match = re.search(r"User ID:\s*(-?\d+)", replied_text)
    return int(match.group(1)) if match else None

async def send_admin_reply_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user or not is_admin(update.effective_user):
        return False
    if not update.message.reply_to_message:
        return False
    target_user_id = extract_user_id_from_admin_message(update.message)
    if not target_user_id:
        await update.message.reply_text("⚠️ برای پاسخ، روی پیام «📩 پیام جدید از کاربر» Reply بزن.")
        return True
    try:
        await update.message.copy(chat_id=target_user_id)
        await update.message.reply_text("✅ پاسخ برای کاربر ارسال شد.")
    except Exception:
        logger.exception("Could not send admin reply to user.")
        await update.message.reply_text("❌ ارسال پاسخ انجام نشد؛ ممکن است کاربر ربات را بلاک کرده باشد.")
    return True

async def message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user:
        return
    if is_admin(update.effective_user):
        if await send_admin_reply_to_user(update, context):
            return
    text = update.message.text or ""
    if text == "👤 درباره عرشیا":
        await profile(update, context)
    elif text == "💌 پیام به عرشیا":
        await start_sending(update, context)
    elif text == "🤖 درباره ربات":
        await about_bot(update, context)
    elif text == "❓ راهنما":
        await help_menu(update, context)
    elif context.user_data.get("waiting_message", False):
        await send_user_message_to_admin(update, context)
    else:
        await update.message.reply_text("برای استفاده از ربات، یکی از گزینه‌های منو را انتخاب کن.", reply_markup=main_menu())

async def post_init(application: Application):
    await application.bot.set_my_commands([
        ("start", "شروع ربات"),
        ("help", "راهنما"),
        ("myid", "شناسه کاربری مدیر"),
    ])

def main():
    threading.Thread(target=run_web_server, daemon=True).start()
    application = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_menu))
    application.add_handler(CommandHandler("myid", my_id))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, message_router))
    application.run_polling(drop_pending_updates=False)

if __name__ == "__main__":
    main()
