class Middleware:
    def __init__(self):
        self._middlewares = []

    def add(self, func):
        """Add a middleware function: async def middleware(obj, next)"""
        self._middlewares.append(func)

    async def run(self, obj, handler):
        async def call(index):
            if index < len(self._middlewares):
                await self._middlewares[index](obj, lambda: call(index+1))
            else:
                await handler(obj)
        await call(0)