from aiohttp import web
import asyncio
import json
from typing import Optional
from .types import parse_update
from .router import Router
from .utils.logger import get_logger

class WebhookServer:
    """سرور وبهوک تلگرام"""
    
    def __init__(
        self,
        client,
        router: Router,
        path: str = "/webhook",
        port: int = 8080,
        host: str = "0.0.0.0"
    ):
        self.client = client
        self.router = router
        self.path = path
        self.port = port
        self.host = host
        self.log = get_logger()
        
        self.app = web.Application()
        self.app.router.add_post(self.path, self._handle_webhook)
        self.app.router.add_get("/", self._health_check)
    
    async def _handle_webhook(self, request: web.Request) -> web.Response:
        """مدیریت درخواست وبهوک"""
        try:
            data = await request.json()
            upd = parse_update(data)
            
            # پردازش آپدیت‌ها
            if upd.message:
                await self.router.dispatch(upd.message)
            if upd.callback_query:
                await self.router.dispatch(upd.callback_query)
            if upd.edited_message:
                await self.router.dispatch(upd.edited_message)
            if upd.channel_post:
                await self.router.dispatch(upd.channel_post)
            
            return web.json_response({"ok": True})
        
        except Exception as e:
            self.log.error(f"Webhook error: {e}")
            return web.json_response({"ok": False, "error": str(e)}, status=500)
    
    async def _health_check(self, request: web.Request) -> web.Response:
        """چک سلامت سرور"""
        return web.json_response({
            "status": "ok",
            "service": "telenet-webhook",
            "version": "2.7.0"
        })
    
    async def start(self):
        """شروع سرور"""
        self.log.info(f"Webhook server starting on {self.host}:{self.port}")
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        self.log.info(f"Webhook server running at http://{self.host}:{self.port}{self.path}")
    
    async def stop(self):
        """توقف سرور"""
        self.log.info("Webhook server stopping")
    
    def run(self):
        """اجرای سرور (blocking)"""
        web.run_app(self.app, host=self.host, port=self.port)

# نسخه ساده‌تر برای استفاده سریع
def run_webhook(client, router, path="/webhook", port=8080):
    """اجرای سریع وبهوک"""
    server = WebhookServer(client, router, path, port)
    server.run()
