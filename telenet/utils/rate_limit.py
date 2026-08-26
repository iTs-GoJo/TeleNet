import asyncio
import time
from typing import Optional

class TokenBucket:
    """کلاس Token Bucket برای محدودیت نرخ"""
    
    def __init__(self, rate: float = 1, capacity: float = 5):
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.timestamp = time.monotonic()
        self.lock = asyncio.Lock()
    
    async def acquire(self, tokens: float = 1):
        """دریافت توکن"""
        async with self.lock:
            now = time.monotonic()
            self._refill(now)
            
            while self.tokens < tokens:
                wait_time = (tokens - self.tokens) / self.rate
                await asyncio.sleep(wait_time)
                
                now = time.monotonic()
                self._refill(now)
            
            self.tokens -= tokens
    
    def _refill(self, now: float):
        """پر کردن توکن‌ها"""
        elapsed = now - self.timestamp
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        self.timestamp = now
    
    def try_acquire(self, tokens: float = 1) -> bool:
        """تلاش برای دریافت توکن بدون انتظار"""
        now = time.monotonic()
        self._refill(now)
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        
        return False

class LeakyBucket:
    """کلاس Leaky Bucket برای محدودیت نرخ"""
    
    def __init__(self, rate: float = 1, capacity: int = 5):
        self.rate = rate
        self.capacity = capacity
        self.queue = asyncio.Queue()
        self.last_time = time.monotonic()
    
    async def acquire(self):
        """دریافت اجازه ارسال"""
        async with self.queue:
            while self.queue.qsize() >= self.capacity:
                await asyncio.sleep(0.1)
            
            await self.queue.put(time.monotonic())
    
    def release(self):
        """آزاد کردن ظرفیت"""
        pass
