import asyncio, time

class TokenBucket:
    def __init__(self, rate=1, capacity=5):
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.timestamp = time.monotonic()
        self.lock = asyncio.Lock()

    async def acquire(self, tokens=1):
        async with self.lock:
            now = time.monotonic()
            self.tokens = min(self.capacity, self.tokens + (now - self.timestamp) * self.rate)
            self.timestamp = now
            while self.tokens < tokens:
                await asyncio.sleep((tokens - self.tokens) / self.rate)
                now = time.monotonic()
                self.tokens = min(self.capacity, self.tokens + (now - self.timestamp) * self.rate)
                self.timestamp = now
            self.tokens -= tokens