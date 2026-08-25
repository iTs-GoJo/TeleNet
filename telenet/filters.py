import re
from .types import Message, CallbackQuery

class BaseFilter: 
    def __call__(self, obj): return True

class AnyMessage(BaseFilter):
    def __call__(self, obj): return isinstance(obj, Message)

class Command(BaseFilter):
    def __init__(self, *names, prefix="/"): self.names = {f"{prefix}{n}" for n in names}
    def __call__(self, obj): 
        return isinstance(obj, Message) and isinstance(obj.text, str) and obj.text.split()[0] in self.names

class Text(BaseFilter):
    def __init__(self, equals=None, contains=None): self.equals, self.contains = equals, contains
    def __call__(self, obj):
        if not isinstance(obj, Message) or not isinstance(obj.text, str): return False
        if self.equals is not None: return obj.text == self.equals
        if self.contains is not None: return self.contains in obj.text
        return False

class Regex(BaseFilter):
    def __init__(self, pattern): self.p = re.compile(pattern) if isinstance(pattern, str) else pattern
    def __call__(self, obj):
        return isinstance(obj, Message) and isinstance(obj.text, str) and bool(self.p.search(obj.text))

class CallbackData(BaseFilter):
    def __init__(self, prefix=None, equals=None): self.prefix, self.equals = prefix, equals
    def __call__(self, obj):
        if not isinstance(obj, CallbackQuery) or obj.data is None: return False
        if self.equals is not None: return obj.data == self.equals
        if self.prefix is not None: return str(obj.data).startswith(self.prefix)
        return True