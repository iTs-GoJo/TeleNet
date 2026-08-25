import asyncio

class Router:
    def __init__(self):
        self.handlers = []

    def on(self, filter):
        def wrapper(func):
            self.handlers.append((filter, func))
            return func
        return wrapper

    async def dispatch(self, obj):
        for filt, func in self.handlers:
            if filt(obj):
                if asyncio.iscoroutinefunction(func):
                    await func(obj)
                else:
                    func(obj)