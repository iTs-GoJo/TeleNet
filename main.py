import asyncio
from telenet import TeleNetClient, Router, Command, InlineButton

TOKEN = "8238495851:AAHhHRmTHRU2mUR7n7qtCJZcziyMUoqccew"
bot = TeleNetClient(TOKEN)
router = Router()

# دکمه لینک: وقتی کاربر بزنه، مستقیم میره گوگل
@router.on(Command("start"))
async def start_handler(message):
    await bot.send_message(
        message.chat.id,
        "تست دکمه:",
        buttons=[
            [InlineButton("رفتن به گوگل", url="https://google.com")]
        ]
    )

# دکمه callback: وقتی کاربر بزنه، بات پاسخ میده
@router.on(Command("menu"))
async def menu_handler(message):
    await bot.send_message(
        message.chat.id,
        "یه گزینه انتخاب کن:",
        buttons=[
            [InlineButton("گزینه ۱", callback_data="opt1")],
            [InlineButton("گزینه ۲", callback_data="opt2")]
        ]
    )

# هندلر callback
@router.on(lambda q: hasattr(q, "data"))  # فقط callback هایی که data دارن
async def callback_handler(q):
    await bot.answer_callback(q.id, f"شما {q.data} را انتخاب کردید")
    await bot.send_message(q.message.chat.id, f"گزینه {q.data} انتخاب شد ✅")

async def main():
    await bot.start()
    await bot.poll_updates(router=router)

if __name__ == "__main__":
    asyncio.run(main())