import logging
import requests as req
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler

# تبدیل اعداد فارسی به انگلیسی
def fa_to_en_digits(text):
    fa_to_en_map = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
    return text.translate(fa_to_en_map)

# تنظیم لاگ‌ها
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

# دستور شروع ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! 👋\n"
        "به **ربات LrnTix** خوش آمدید! 🌟\n"
        "من اینجا هستم تا تاریخ‌های مختلف را به شما نمایش دهم. 📅\n"
        "شما می‌توانید تاریخ مورد نظر خود را به صورت زیر وارد کنید:\n"
        "- 2023-02-11 (میلادی)\n"
        "- 2023/02/11 (میلادی)\n\n"
        "بعد از ارسال تاریخ، دو دکمه برای شما نمایش داده خواهد شد:\n"
        "1. **تاریخ میلادی** (برای مشاهده رویدادهای میلادی)\n"
        "2. **تاریخ شمسی** (برای مشاهده رویدادهای شمسی)\n\n"
        "امیدوارم از ربات استفاده کنید و سوالات خود را بپرسید! 😄\n"
        "(طراح: امیرمحمد)\n"
        "لطفاً تاریخ مورد نظر را به صورت 2023-02-11 یا 2023/02/11 وارد کنید. 📅"
    )

async def send_buttons(update: Update, user_text: str):
    # ساخت دکمه‌ها
    keyboard = [
        [
            InlineKeyboardButton("تاریخ میلادی", callback_data=f"gregorian_{user_text}"),
            InlineKeyboardButton("تاریخ شمسی", callback_data=f"jalali_{user_text}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "لطفاً انتخاب کنید:",
        reply_markup=reply_markup
    )

# عملکرد دریافت پیام و ارسال اطلاعات تاریخ
async def make_text_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    logging.info(f"متن دریافتی از کاربر: {user_text}")

    try:
        # تبدیل اعداد فارسی و اصلاح فرمت تاریخ
        user_text = fa_to_en_digits(user_text).replace('-', '/')

        # ارسال دکمه‌ها به کاربر فقط یک بار
        await send_buttons(update, user_text)

    except Exception as e:
        logging.error(f"خطا هنگام دریافت اطلاعات: {e}")
        text = "❌ خطایی در دریافت اطلاعات رخ داد. لطفاً تاریخ را به درستی وارد کنید."

        await update.message.reply_text(text)

# عملکرد زمانی که کاربر روی دکمه‌ها کلیک می‌کند
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    # تحلیل اطلاعات callback_data برای میلادی یا شمسی
    if data.startswith("gregorian"):
        date = data.split('_')[1]
        url = f'https://holidayapi.ir/gregorian/{date}'
    elif data.startswith("jalali"):
        date = data.split('_')[1]
        url = f'https://holidayapi.ir/jalali/{date}'
    
    response = req.get(url)
    data = response.json()

    if "events" in data and isinstance(data["events"], list):
        events = data["events"]
        if events:
            event_list = "\n".join([f"- {event['description']}" for event in events])
            text = f"📅 تاریخ: {date}\nرویدادها:\n{event_list}"
        else:
            text = f"📅 تاریخ: {date}\n❌ هیچ مناسبتی یافت نشد."
    else:
        text = f"📅 تاریخ: {date}\n❌ اطلاعاتی برای این تاریخ یافت نشد."

    await query.answer()
    await query.edit_message_text(text)

# راه‌اندازی ربات
application = ApplicationBuilder().token('7203928702:AAH-IHqLUr3I4AhgV7ZbFlyoZNODyz_OqWg').build()

# اضافه کردن هندلرها
application.add_handler(CommandHandler('start', start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, make_text_response))
application.add_handler(CallbackQueryHandler(button_callback))

# اجرای ربات
application.run_polling()
