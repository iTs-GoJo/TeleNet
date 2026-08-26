import asyncio
from typing import List, Tuple, Callable, Any, Optional
from .middleware import Middleware
from .filters import BaseFilter
from .types import Update, Message, CallbackQuery

class Router:
    """کلاس Router برای مدیریت هندلرها"""
    
    def __init__(self):
        self.handlers: List[Tuple[BaseFilter, Callable]] = []
        self.middleware = Middleware()
        self.error_handlers: List[Callable] = []
    
    def on(self, filter=None):
        """دکوراتور برای ثبت هندلر"""
        def wrapper(func):
            self.handlers.append((filter or BaseFilter(), func))
            return func
        return wrapper
    
    def on_message(self, *filters):
        """دکوراتور برای هندلر پیام‌ها"""
        from .filters import AnyMessage
        return self.on(AnyMessage() if not filters else filters[0])
    
    def on_callback(self, *filters):
        """دکوراتور برای هندلر کال‌بک‌ها"""
        from .filters import CallbackData
        return self.on(CallbackData() if not filters else filters[0])
    
    def add_middleware(self, func: Callable):
        """افزودن middleware"""
        self.middleware.add(func)
    
    def error_handler(self, func: Callable):
        """ثبت هندلر خطا"""
        self.error_handlers.append(func)
        return func
    
    async def dispatch(self, obj: Any):
        """ارسال آبجکت به هندلرهای مناسب"""
        for filt, func in self.handlers:
            try:
                if filt(obj):
                    await self._run_handler(func, obj)
                    break  # فقط اولین هندلر مناسب اجرا شود
            except Exception as e:
                await self._handle_error(e, obj, func)
    
    async def _run_handler(self, func: Callable, obj: Any):
        """اجرای هندلر با middleware"""
        await self.middleware.run(obj, func)
    
    async def _handle_error(self, error: Exception, obj: Any, handler: Callable):
        """مدیریت خطاها"""
        for error_handler in self.error_handlers:
            try:
                await error_handler(error, obj, handler)
            except Exception:
                pass

class SubRouter(Router):
    """Router فرزند برای گروه‌بندی هندلرها"""
    
    def __init__(self, parent: Optional[Router] = None):
        super().__init__()
        self.parent = parent
        self.sub_routers: List[SubRouter] = []
    
    def include_router(self, router: "SubRouter"):
        """اضافه کردن router فرزند"""
        self.sub_routers.append(router)
    
    async def dispatch(self, obj: Any):
        """ارسال به هندلرهای خود و فرزندان"""
        await super().dispatch(obj)
        for sub in self.sub_routers:
            await sub.dispatch(obj)
