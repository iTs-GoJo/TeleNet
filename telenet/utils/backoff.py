# utils/backoff.py
import asyncio
from functools import wraps
from typing import Callable, Optional, Type, Tuple

async def retry_async(
    func: Callable,
    retries: int = 3,
    delay: float = 1,
    max_delay: float = 30,
    exponential: bool = True
):
    """اجرای تابع با retry (بدون دکوراتور)"""
    current_delay = delay
    
    for attempt in range(retries):
        try:
            return await func()
        except Exception:
            if attempt == retries - 1:
                raise
            if exponential:
                current_delay = min(current_delay * 2, max_delay)
            else:
                current_delay = delay
            await asyncio.sleep(current_delay)

def retry_async_decorator(
    retries: int = 3,
    delay: float = 1,
    max_delay: float = 30,
    exponential: bool = True
):
    """دکوراتور برای retry"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_delay = delay
            
            for attempt in range(retries):
                try:
                    return await func(*args, **kwargs)
                except Exception:
                    if attempt == retries - 1:
                        raise
                    if exponential:
                        current_delay = min(current_delay * 2, max_delay)
                    else:
                        current_delay = delay
                    await asyncio.sleep(current_delay)
            return None
        return wrapper
    return decorator
