from typing import List, Callable, Any, Optional
import asyncio

class Middleware:
    """کلاس Middleware برای پردازش میانی"""
    
    def __init__(self):
        self._middlewares: List[Callable] = []
    
    def add(self, func: Callable):
        """افزودن middleware"""
        if not callable(func):
            raise TypeError("Middleware must be callable")
        self._middlewares.append(func)
    
    def remove(self, func: Callable):
        """حذف middleware"""
        if func in self._middlewares:
            self._middlewares.remove(func)
    
    async def run(self, obj: Any, handler: Callable):
        """اجرای همه middlewareها و هندلر"""
        if not self._middlewares:
            await self._call_handler(handler, obj)
            return
        
        async def call_next(index: int):
            if index < len(self._middlewares):
                middleware_func = self._middlewares[index]
                
                # پشتیبانی از هر دو فرمت middleware
                if asyncio.iscoroutinefunction(middleware_func):
                    await middleware_func(obj, lambda: call_next(index + 1))
                else:
                    result = middleware_func(obj, lambda: call_next(index + 1))
                    if asyncio.iscoroutine(result):
                        await result
            else:
                await self._call_handler(handler, obj)
        
        await call_next(0)
    
    async def _call_handler(self, handler: Callable, obj: Any):
        """اجرای هندلر اصلی"""
        if asyncio.iscoroutinefunction(handler):
            await handler(obj)
        else:
            result = handler(obj)
            if asyncio.iscoroutine(result):
                await result

# دکوراتور برای راحت‌تر کردن middleware
def middleware(func: Callable) -> Callable:
    """دکوراتور برای ساخت middleware"""
    return func
