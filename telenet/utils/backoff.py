import asyncio
from typing import Callable, Type, Optional
from functools import wraps

def retry_async(
    func: Callable,
    retries: int = 3,
    delay: float = 1,
    max_delay: float = 30,
    exponential: bool = True,
    exceptions: Optional[tuple] = None
):
    """دکوراتور retry با backoff"""
    
    async def wrapper(*args, **kwargs):
        current_delay = delay
        
        for attempt in range(retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if exceptions and not isinstance(e, exceptions):
                    raise
                
                if attempt == retries - 1:
                    raise
                
                # محاسبه تاخیر بعدی
                if exponential:
                    current_delay = min(current_delay * 2, max_delay)
                else:
                    current_delay = delay
                
                await asyncio.sleep(current_delay)
    
    return wrapper

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
                except Exception as e:
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
