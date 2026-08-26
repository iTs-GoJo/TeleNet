import asyncio
import logging
from telenet import TeleNetClient, Router, Command, InlineButton, CallbackData, Text
from telenet.middleware import middleware

# تنظیم لاگر
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

TOKEN = "BOT_TOKEN"
bot = TeleNetClient(TOKEN)
router = Router()

# Middleware برای لاگ کردن
@middleware
async def logging_middleware(obj, next):
    print(f"📩 دریافت: {obj}")
    await next()
    print(f"✅ پردازش شد")

# دکمه لینک: وقتی کاربر بزنه، مستقیم میره گوگل
@router.on(Command("start"))
async def start_handler(message):
    await bot.send_message(
        message.chat.id,
        "🤖 خوش آمدی به ربات!\n\n"
        "این یک ربات نمونه برای تست TeleNet است.\n"
        "دستورات:\n"
        "/menu - نمایش منو\n"
        "/help - راهنما\n"
        "/about - درباره",
        buttons=[
            [InlineButton("📚 دموی ساده", callback_data="demo")],
            [InlineButton("🌐 گوگل", url="https://google.com")],
            [InlineButton("🔗 تلگرام", url="https://t.me")]
        ]
    )

# دکمه callback: وقتی کاربر بزنه، بات پاسخ میده
@router.on(Command("menu"))
async def menu_handler(message):
    await bot.send_message(
        message.chat.id,
        "🍽️ لطفاً یک گزینه انتخاب کنید:",
        buttons=[
            [InlineButton("📁 گزینه ۱", callback_data="opt1")],
            [InlineButton("📁 گزینه ۲", callback_data="opt2")],
            [InlineButton("📁 گزینه ۳", callback_data="opt3")]
        ]
    )

@router.on(Command("help"))
async def help_handler(message):
    help_text = (
        "📖 راهنما:\n\n"
        "🔹 /start - شروع\n"
        "🔹 /menu - نمایش منو\n"
        "🔹 /about - درباره ربات\n"
        "🔹 /help - این راهنما\n\n"
        "💡 می‌توانید هر متنی بفرستید و من پاسخ می‌دهم!"
    )
    await bot.send_message(message.chat.id, help_text)

@router.on(Command("about"))
async def about_handler(message):
    await bot.send_message(
        message.chat.id,
        "ℹ️ درباره ربات:\n"
        "این ربات با TeleNet ساخته شده است.\n"
        "TeleNet - Async Telegram Bot API Framework\n"
        "Version: 2.7.0"
    )

# هندلر callback data
@router.on(CallbackData(prefix="opt"))
async def callback_handler(q):
    option = q.data.replace("opt", "")
    await bot.answer_callback(q.id, f"گزینه {option} انتخاب شد")
    await bot.send_message(
        q.message.chat.id,
        f"✅ شما گزینه {option} را انتخاب کردید"
    )

@router.on(CallbackData(equals="demo"))
async def demo_callback(q):
    await bot.answer_callback(q.id, "دموی ساده را انتخاب کردید")
    await bot.send_message(
        q.message.chat.id,
        "📚 این یک دموی ساده است!\n"
        "TeleNet از callback_data پشتیبانی می‌کند.",
        buttons=[
            [InlineButton("برگشت به منو", callback_data="back_to_menu")]
        ]
    )

@router.on(CallbackData(equals="back_to_menu"))
async def back_to_menu_callback(q):
    await bot.answer_callback(q.id, "برگشت به منو")
    await menu_handler(q.message)

# هندلر برای متن‌های خاص
@router.on(Text(equals="سلام"))
async def say_hello(message):
    await bot.send_message(message.chat.id, "سلام! 👋 چطوری؟")

@router.on(Text(contains="ربات"))
async def bot_reply(message):
    await bot.send_message(message.chat.id, "من یک ربات هستم! 🤖")

# دریافت اطلاعات کاربر
@router.on(Command("me"))
async def me_handler(message):
    user = message.from_user
    if user:
        await bot.send_message(
            message.chat.id,
            f"👤 اطلاعات شما:\n"
            f"نام: {user.full_name}\n"
            f"آیدی: {user.id}\n"
            f"یوزرنیم: @{user.username}" if user.username else f"یوزرنیم: ندارد"
        )

async def main():
    # اضافه کردن middleware
    router.add_middleware(logging_middleware)
    
    try:
        # شروع بات
        await bot.start()
        info = await bot.get_me()
        print(f"🤖 ربات {info['result']['first_name']} شروع به کار کرد!")
        
        # شروع polling
        await bot.poll_updates(router=router)
    
    except KeyboardInterrupt:
        print("\n⏹️ ربات متوقف شد")
    
    finally:
        await bot.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 خداحافظ!")
