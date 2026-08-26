from typing import List, Optional, Union, Dict, Any

class Button:
    """کلاس پایه برای دکمه‌ها"""
    def __init__(self, text: str):
        self.text = text
    
    def to_dict(self) -> Dict[str, Any]:
        """تبدیل به دیکشنری برای API"""
        return {"text": self.text}

class InlineButton(Button):
    """دکمه اینلاین"""
    def __init__(
        self,
        text: str,
        callback_data: Optional[str] = None,
        url: Optional[str] = None,
        switch_inline_query: Optional[str] = None,
        switch_inline_query_current_chat: Optional[str] = None
    ):
        super().__init__(text)
        self.callback_data = callback_data
        self.url = url
        self.switch_inline_query = switch_inline_query
        self.switch_inline_query_current_chat = switch_inline_query_current_chat
    
    def to_dict(self) -> Dict[str, Any]:
        """تبدیل به دیکشنری برای API"""
        result = {"text": self.text}
        
        if self.callback_data:
            result["callback_data"] = self.callback_data
        if self.url:
            result["url"] = self.url
        if self.switch_inline_query:
            result["switch_inline_query"] = self.switch_inline_query
        if self.switch_inline_query_current_chat:
            result["switch_inline_query_current_chat"] = self.switch_inline_query_current_chat
        
        return result

class KeyboardButton(Button):
    """دکمه کیبورد عادی"""
    def __init__(self, text: str, request_contact: bool = False, request_location: bool = False):
        super().__init__(text)
        self.request_contact = request_contact
        self.request_location = request_location
    
    def to_dict(self) -> Dict[str, Any]:
        """تبدیل به دیکشنری برای API"""
        result = {"text": self.text}
        
        if self.request_contact:
            result["request_contact"] = True
        if self.request_location:
            result["request_location"] = True
        
        return result

class InlineKeyboard:
    """کیبورد اینلاین"""
    def __init__(self):
        self.rows: List[List[InlineButton]] = []
    
    def row(self, *buttons: InlineButton) -> "InlineKeyboard":
        """افزودن یک ردیف دکمه"""
        self.rows.append(list(buttons))
        return self
    
    def add(self, *buttons: InlineButton) -> "InlineKeyboard":
        """افزودن دکمه‌ها به ردیف آخر"""
        if not self.rows:
            self.rows.append([])
        self.rows[-1].extend(buttons)
        return self
    
    def to_markup(self) -> Dict[str, Any]:
        """تبدیل به JSON markup برای API"""
        return {
            "inline_keyboard": [
                [button.to_dict() for button in row]
                for row in self.rows
            ]
        }
    
    def __iter__(self):
        return iter(self.rows)
    
    def __len__(self):
        return len(self.rows)

class ReplyKeyboard:
    """کیبورد پاسخ (Reply Keyboard)"""
    def __init__(self, resize_keyboard: bool = True, one_time_keyboard: bool = False):
        self.rows: List[List[KeyboardButton]] = []
        self.resize_keyboard = resize_keyboard
        self.one_time_keyboard = one_time_keyboard
    
    def row(self, *buttons: KeyboardButton) -> "ReplyKeyboard":
        """افزودن یک ردیف دکمه"""
        self.rows.append(list(buttons))
        return self
    
    def add(self, *buttons: KeyboardButton) -> "ReplyKeyboard":
        """افزودن دکمه‌ها به ردیف آخر"""
        if not self.rows:
            self.rows.append([])
        self.rows[-1].extend(buttons)
        return self
    
    def to_markup(self) -> Dict[str, Any]:
        """تبدیل به JSON markup برای API"""
        return {
            "keyboard": [
                [button.to_dict() for button in row]
                for row in self.rows
            ],
            "resize_keyboard": self.resize_keyboard,
            "one_time_keyboard": self.one_time_keyboard
        }

class ForceReply:
    """نیرو به پاسخ"""
    def __init__(self, selective: bool = True):
        self.selective = selective
    
    def to_markup(self) -> Dict[str, Any]:
        """تبدیل به JSON markup برای API"""
        return {
            "force_reply": True,
            "selective": self.selective
        }

# میانبرهای برای راحتی
def inline_keyboard(rows: List[List[InlineButton]]) -> Dict[str, Any]:
    """ساخت سریع کیبورد اینلاین"""
    kb = InlineKeyboard()
    for row in rows:
        kb.row(*row)
    return kb.to_markup()

def reply_keyboard(rows: List[List[KeyboardButton]]) -> Dict[str, Any]:
    """ساخت سریع کیبورد پاسخ"""
    kb = ReplyKeyboard()
    for row in rows:
        kb.row(*row)
    return kb.to_markup()
