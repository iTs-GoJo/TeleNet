import aiohttp, asyncio
from .utils.logger import get_logger
from .utils.rate_limit import TokenBucket
from .utils.backoff import retry_async
from .types import parse_update
from .exceptions import APIError

class TeleNetClient:
    def __init__(self, token, base_url=None, rate_per_sec=28, capacity=30):
        self.token = token
        self.base_url = base_url or f"https://api.telegram.org/bot{token}"
        self.session = None
        self.log = get_logger()
        self.bucket = TokenBucket(rate=rate_per_sec, capacity=capacity)
        self._offset = 0
        self._running = False

    async def start(self):
        if self.session is None:
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60))

    async def close(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def _request(self, method, payload=None):
        assert self.session is not None, "Call start() first"
        url = f"{self.base_url}/{method}"

        async def do():
            await self.bucket.acquire(1)
            async with self.session.post(url, json=payload or {}) as resp:
                data = await resp.json()
                if not data.get("ok", False):
                    raise APIError(
                        data.get("description", "Unknown error"),
                        data.get("error_code")
                    )
                return data

        return await retry_async(do, retries=3)

    async def get_me(self):
        return await self._request("getMe")

    async def send_message(self, chat_id, text, **kw):
        markup = None
        if "buttons" in kw:
            from .keyboards import InlineKeyboard
            kb = InlineKeyboard()
            for row in kw.pop("buttons"):
                kb.row(*row)
            markup = kb.to_markup()
        if markup:
            kw["reply_markup"] = markup

        payload = {"chat_id": chat_id, "text": text}
        payload |= kw
        return await self._request("sendMessage", payload)

    async def answer_callback(self, callback_id, text=None, show_alert=False):
        payload = {"callback_query_id": callback_id}
        if text:
            payload["text"] = text
        if show_alert:
            payload["show_alert"] = True
        return await self._request("answerCallbackQuery", payload)

    async def poll_updates(self, *, router, timeout=30, allowed_updates=None):
        self._running = True
        await self.start()
        self.log.info("Polling started")
        while self._running:
            try:
                data = await self._request("getUpdates", {
                    "offset": self._offset,
                    "timeout": timeout,
                    "allowed_updates": allowed_updates or ["message", "callback_query"]
                })
                for raw in data.get("result", []):
                    upd = parse_update(raw)
                    self._offset = raw.get("update_id", 0) + 1
                    if upd.message:
                        await router.dispatch(upd.message)
                    if upd.callback_query:
                        await router.dispatch(upd.callback_query)
            except Exception as e:
                self.log.error(f"Loop error: {e}")
                await asyncio.sleep(1)

    def stop(self):
        self._running = False