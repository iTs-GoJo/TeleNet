from aiohttp import web
import asyncio

class WebhookServer:
    def __init__(self, app, router, path="/webhook", port=8080):
        self._app = app
        self.router = router
        self.path = path
        self.port = port
        self._aio_app = web.Application()
        self._aio_app.router.add_post(self.path, self._handler)

    async def _handler(self, request):
        data = await request.json()
        upd = self._app.types.parse_update(data)
        if upd.message:
            await self.router.dispatch(upd.message)
        if upd.callback_query:
            await self.router.dispatch(upd.callback_query)
        return web.json_response({"ok": True})

    def run(self):
        web.run_app(self._aio_app, port=self.port)