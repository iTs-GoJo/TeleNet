# TeleNet

TeleNet یک کتابخانه مدرن و قدرتمند Python برای ساخت ربات‌های تلگرام با asyncio است. با TeleNet می‌توانید ربات‌های پیچیده با پیام فارسی، دکمه‌های اینلاین، هندلینگ پیشرفته و مدیریت کامل کامندها بسازید.

## 🔹 ویژگی‌ها

- طراحی مدرن و سبک با asyncio
- پشتیبانی کامل از پیام‌های فارسی و Unicode
- سیستم Router & Command برای مدیریت کامندها
- پشتیبانی از Middleware
- Long Polling و Webhook
- Rate Limiting و Retry خودکار
- پشتیبانی از دکمه‌های Inline و Reply Keyboard
- کاملاً ماژولار و قابل گسترش

## 🔹 نصب

```bash
pip install telenet
```

نصب به صورت محلی (توسعه):

```bash
git clone https://github.com/yourusername/telenet.git
cd telenet
pip install -e .
```

🔹 شروع سریع

```python
import asyncio
from telenet import TeleNetClient, Router, Command

TOKEN = "YOUR_BOT_TOKEN"
bot = TeleNetClient(TOKEN)
router = Router()

@router.on(Command("start"))
async def start(ctx):
    await bot.send_message(ctx.chat.id, "سلام! خوش اومدی 😎")

async def main():
    await bot.start()
    await bot.poll_updates(router=router)

if __name__ == "__main__":
    asyncio.run(main())
```

🔹 استفاده از دکمه‌های اینلاین

```python
from telenet import TeleNetClient, Router, Command, InlineButton

@router.on(Command("start"))
async def start(ctx):
    await bot.send_message(
        ctx.chat.id,
        "یکی از گزینه‌ها را انتخاب کنید:",
        buttons=[
            [InlineButton("رفتن به گوگل", url="https://google.com")],
            [InlineButton("گزینه ۱", callback_data="opt1")]
        ]
    )
```

🔹 Middleware

```python
from telenet.middleware import middleware

@middleware
async def logging_middleware(obj, next):
    print(f"📩 دریافت: {obj}")
    await next()
    print("✅ پردازش شد")

router.add_middleware(logging_middleware)
```

🔹 Webhook

```python
from telenet.webhook import WebhookServer

async def main():
    await bot.start()
    server = WebhookServer(bot, router, path="/webhook", port=8443)
    await server.start()
    await asyncio.Event().wait()
```

🔹 نیازمندی‌ها

· Python 3.9+
· aiohttp>=3.9

🔹 لایسنس

MIT License

---

Designed by Ali-Jafari & GPT | With ❤
