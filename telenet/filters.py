import re
from typing import Union, Optional, Pattern, Callable
from .types import Message, CallbackQuery, Update

class BaseFilter:
    """کلاس پایه برای فیلترها"""
    def __call__(self, obj) -> bool:
        return True
    
    def __and__(self, other):
        return AndFilter(self, other)
    
    def __or__(self, other):
        return OrFilter(self, other)

class AnyMessage(BaseFilter):
    """فیلتر برای هر پیام"""
    def __call__(self, obj) -> bool:
        return isinstance(obj, Message)

class Command(BaseFilter):
    """فیلتر برای دستورات (کامندها)"""
    def __init__(self, *names: str, prefix: str = "/"):
        self.names = {f"{prefix}{n}" for n in names}
        self.prefix = prefix
    
    def __call__(self, obj) -> bool:
        if not isinstance(obj, Message) or not obj.text:
            return False
        text = obj.text.strip()
        if not text.startswith(self.prefix):
            return False
        command = text.split()[0].lower()
        return command in self.names
    
    def __repr__(self):
        return f"Command({', '.join(self.names)})"

class Text(BaseFilter):
    """فیلتر برای متن پیام"""
    def __init__(self, equals: str = None, contains: str = None, startswith: str = None, endswith: str = None):
        self.equals = equals
        self.contains = contains
        self.startswith = startswith
        self.endswith = endswith
    
    def __call__(self, obj) -> bool:
        if not isinstance(obj, Message) or not obj.text:
            return False
        
        text = obj.text
        
        if self.equals is not None:
            return text == self.equals
        if self.contains is not None:
            return self.contains in text
        if self.startswith is not None:
            return text.startswith(self.startswith)
        if self.endswith is not None:
            return text.endswith(self.endswith)
        
        return False

class Regex(BaseFilter):
    """فیلتر برای regex"""
    def __init__(self, pattern: Union[str, Pattern]):
        self.pattern = re.compile(pattern) if isinstance(pattern, str) else pattern
    
    def __call__(self, obj) -> bool:
        if not isinstance(obj, Message) or not obj.text:
            return False
        return bool(self.pattern.search(obj.text))

class CallbackData(BaseFilter):
    """فیلتر برای callback data"""
    def __init__(self, prefix: str = None, equals: str = None, regex: str = None):
        self.prefix = prefix
        self.equals = equals
        self.regex = re.compile(regex) if regex else None
    
    def __call__(self, obj) -> bool:
        if not isinstance(obj, CallbackQuery) or not obj.data:
            return False
        
        data = obj.data
        
        if self.equals is not None:
            return data == self.equals
        if self.prefix is not None:
            return data.startswith(self.prefix)
        if self.regex is not None:
            return bool(self.regex.search(data))
        
        return True

class AndFilter(BaseFilter):
    """فیلتر ترکیبی AND"""
    def __init__(self, *filters):
        self.filters = filters
    
    def __call__(self, obj) -> bool:
        return all(f(obj) for f in self.filters)

class OrFilter(BaseFilter):
    """فیلتر ترکیبی OR"""
    def __init__(self, *filters):
        self.filters = filters
    
    def __call__(self, obj) -> bool:
        return any(f(obj) for f in self.filters)

class MiddlewareFilter(BaseFilter):
    """فیلتر برای middleware"""
    def __init__(self, predicate: Callable):
        self.predicate = predicate
    
    def __call__(self, obj) -> bool:
        return self.predicate(obj)

# میانبرهای مفید
Any = AnyMessage
CommandFilter = Command
TextFilter = Text
