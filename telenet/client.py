import aiohttp
import asyncio
import json
from typing import Optional, Dict, Any, List, Union
from .utils.logger import get_logger
from .utils.rate_limit import TokenBucket
from .utils.backoff import retry_async
from .types import parse_update, Update
from .exceptions import APIError
from .keyboards import InlineKeyboard
from .router import Router

class TeleNetClient:
    """کلاس اصلی کلاینت تلگرام"""
    
    def __init__(
        self,
        token: str,
        base_url: Optional[str] = None,
        rate_per_sec: float = 28,
        capacity: int = 30,
        timeout: int = 60
    ):
        self.token = token
        self.base_url = base_url or f"https://api.telegram.org/bot{token}"
        self.session: Optional[aiohttp.ClientSession] = None
        self.log = get_logger()
        self.bucket = TokenBucket(rate=rate_per_sec, capacity=capacity)
        self._offset = 0
        self._running = False
        self.timeout = timeout
        self._webhook_server = None
    
    async def start(self):
        """شروع کلاینت"""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                headers={"Content-Type": "application/json"}
            )
            self.log.info("TeleNetClient started")
    
    async def close(self):
        """بستن کلاینت"""
        if self.session:
            await self.session.close()
            self.session = None
            self.log.info("TeleNetClient closed")
    
    async def _request(self, method: str, payload: Optional[Dict] = None) -> Dict:
        """ارسال درخواست به API تلگرام"""
        if self.session is None:
            await self.start()
        
        url = f"{self.base_url}/{method}"
        
        async def do():
            await self.bucket.acquire(1)
            async with self.session.post(url, json=payload or {}) as resp:
                data = await resp.json()
                if not data.get("ok", False):
                    error_code = data.get("error_code", 0)
                    description = data.get("description", "Unknown error")
                    
                    # مدیریت خطاهای خاص
                    if error_code == 429:  # Too Many Requests
                        retry_after = data.get("parameters", {}).get("retry_after", 1)
                        self.log.warning(f"Rate limited! Retry after {retry_after}s")
                        await asyncio.sleep(retry_after)
                        raise APIError(description, error_code)
                    
                    elif error_code == 409:  # Conflict
                        self.log.error("Conflict detected - another getUpdates call")
                        raise APIError("Conflict: Another getUpdates call is active", error_code)
                    
                    raise APIError(description, error_code)
                return data
        
        return await retry_async(do, retries=3)
    
    async def get_me(self) -> Dict:
        """دریافت اطلاعات بات"""
        return await self._request("getMe")
    
    async def send_message(
        self,
        chat_id: Union[int, str],
        text: str,
        parse_mode: Optional[str] = None,
        disable_web_page_preview: bool = False,
        disable_notification: bool = False,
        reply_to_message_id: Optional[int] = None,
        buttons: Optional[List[List]] = None,
        **kwargs
    ) -> Dict:
        """ارسال پیام"""
        payload = {
            "chat_id": chat_id,
            "text": text,
        }
        
        if parse_mode:
            payload["parse_mode"] = parse_mode
        if disable_web_page_preview:
            payload["disable_web_page_preview"] = True
        if disable_notification:
            payload["disable_notification"] = True
        if reply_to_message_id:
            payload["reply_to_message_id"] = reply_to_message_id
        if buttons:
            kb = InlineKeyboard()
            for row in buttons:
                kb.row(*row)
            payload["reply_markup"] = kb.to_markup()
        
        payload.update(kwargs)
        return await self._request("sendMessage", payload)
    
    async def send_photo(
        self,
        chat_id: Union[int, str],
        photo: Union[str, bytes],
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None,
        buttons: Optional[List[List]] = None,
        **kwargs
    ) -> Dict:
        """ارسال عکس"""
        payload = {"chat_id": chat_id}
        
        if isinstance(photo, str) and photo.startswith("http"):
            payload["photo"] = photo
        else:
            # برای فایل‌های باینری
            payload["photo"] = photo
        
        if caption:
            payload["caption"] = caption
        if parse_mode:
            payload["parse_mode"] = parse_mode
        if buttons:
            kb = InlineKeyboard()
            for row in buttons:
                kb.row(*row)
            payload["reply_markup"] = kb.to_markup()
        
        payload.update(kwargs)
        return await self._request("sendPhoto", payload)
    
    async def answer_callback(
        self,
        callback_query_id: str,
        text: Optional[str] = None,
        show_alert: bool = False,
        url: Optional[str] = None
    ) -> Dict:
        """پاسخ به کال‌بک کوئری"""
        payload = {"callback_query_id": callback_query_id}
        
        if text:
            payload["text"] = text
        if show_alert:
            payload["show_alert"] = True
        if url:
            payload["url"] = url
        
        return await self._request("answerCallbackQuery", payload)
    
    async def edit_message_text(
        self,
        chat_id: Optional[Union[int, str]] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        text: str = "",
        parse_mode: Optional[str] = None,
        buttons: Optional[List[List]] = None,
        **kwargs
    ) -> Dict:
        """ویرایش متن پیام"""
        payload = {"text": text}
        
        if chat_id:
            payload["chat_id"] = chat_id
        if message_id:
            payload["message_id"] = message_id
        if inline_message_id:
            payload["inline_message_id"] = inline_message_id
        if parse_mode:
            payload["parse_mode"] = parse_mode
        if buttons:
            kb = InlineKeyboard()
            for row in buttons:
                kb.row(*row)
            payload["reply_markup"] = kb.to_markup()
        
        payload.update(kwargs)
        return await self._request("editMessageText", payload)
    
    async def delete_message(
        self,
        chat_id: Union[int, str],
        message_id: int
    ) -> Dict:
        """حذف پیام"""
        payload = {"chat_id": chat_id, "message_id": message_id}
        return await self._request("deleteMessage", payload)
    
    async def set_webhook(
        self,
        url: str,
        allowed_updates: Optional[List[str]] = None,
        secret_token: Optional[str] = None
    ) -> Dict:
        """تنظیم وبهوک"""
        payload = {"url": url}
        if allowed_updates:
            payload["allowed_updates"] = allowed_updates
        if secret_token:
            payload["secret_token"] = secret_token
        return await self._request("setWebhook", payload)
    
    async def delete_webhook(self) -> Dict:
        """حذف وبهوک"""
        return await self._request("deleteWebhook")
    
    async def get_updates(
        self,
        offset: Optional[int] = None,
        limit: int = 100,
        timeout: int = 0,
        allowed_updates: Optional[List[str]] = None
    ) -> List[Update]:
        """دریافت آپدیت‌ها"""
        payload = {"limit": limit, "timeout": timeout}
        
        if offset is not None:
            payload["offset"] = offset
        if allowed_updates:
            payload["allowed_updates"] = allowed_updates
        
        data = await self._request("getUpdates", payload)
        updates = []
        
        for raw in data.get("result", []):
            updates.append(parse_update(raw))
        
        return updates
    
    async def poll_updates(
        self,
        *,
        router: Router,
        timeout: int = 30,
        allowed_updates: Optional[List[str]] = None,
        limit: int = 100
    ):
        """شروع polling آپدیت‌ها"""
        self._running = True
        await self.start()
        
        self.log.info(f"Polling started (timeout={timeout}s)")
        
        while self._running:
            try:
                data = await self._request("getUpdates", {
                    "offset": self._offset,
                    "timeout": timeout,
                    "limit": limit,
                    "allowed_updates": allowed_updates or ["message", "callback_query"]
                })
                
                for raw in data.get("result", []):
                    self._offset = raw.get("update_id", 0) + 1
                    upd = parse_update(raw)
                    
                    # ارسال به router
                    if upd.message:
                        await router.dispatch(upd.message)
                    if upd.callback_query:
                        await router.dispatch(upd.callback_query)
                    if upd.edited_message:
                        await router.dispatch(upd.edited_message)
                    if upd.channel_post:
                        await router.dispatch(upd.channel_post)
                
                # گزارش وضعیت
                if self.log.level == 10:  # DEBUG
                    self.log.debug(f"Received {len(data.get('result', []))} updates")
                
            except asyncio.CancelledError:
                self.log.info("Polling cancelled")
                break
            except Exception as e:
                self.log.error(f"Polling error: {e}")
                await asyncio.sleep(1)
    
    def stop(self):
        """توقف polling"""
        self._running = False
        self.log.info("Polling stopped")
    
    async def __aenter__(self):
        """Context manager support"""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

# کلاس کمکی برای دسترسی آسان
class TeleNet(TeleNetClient):
    """نام کوتاه برای TeleNetClient"""
    pass
