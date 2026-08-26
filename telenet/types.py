from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class User:
    """کلاس User برای نمایش کاربر تلگرام"""
    id: int
    is_bot: bool = False
    first_name: str = ""
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Optional[Dict]) -> Optional["User"]:
        if not data:
            return None
        return cls(
            id=data.get("id", 0),
            is_bot=data.get("is_bot", False),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name"),
            username=data.get("username"),
            language_code=data.get("language_code")
        )
    
    @property
    def full_name(self) -> str:
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name

@dataclass
class Chat:
    """کلاس Chat برای نمایش چت تلگرام"""
    id: int
    type: str = "private"
    title: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Optional[Dict]) -> Optional["Chat"]:
        if not data:
            return None
        return cls(
            id=data.get("id", 0),
            type=data.get("type", "private"),
            title=data.get("title"),
            username=data.get("username"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name")
        )
    
    @property
    def name(self) -> str:
        return self.title or self.username or self.first_name or str(self.id)

@dataclass
class Message:
    """کلاس Message برای نمایش پیام تلگرام"""
    message_id: int
    chat: Chat
    text: Optional[str] = None
    from_user: Optional[User] = None
    date: Optional[int] = None
    photo: Optional[List[Dict]] = None
    document: Optional[Dict] = None
    sticker: Optional[Dict] = None
    caption: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Optional[Dict]) -> Optional["Message"]:
        if not data:
            return None
        return cls(
            message_id=data.get("message_id", 0),
            chat=Chat.from_dict(data.get("chat")),
            text=data.get("text") or data.get("caption"),
            from_user=User.from_dict(data.get("from")),
            date=data.get("date"),
            photo=data.get("photo"),
            document=data.get("document"),
            sticker=data.get("sticker"),
            caption=data.get("caption")
        )

@dataclass
class CallbackQuery:
    """کلاس CallbackQuery برای نمایش کال‌بک کوئری تلگرام"""
    id: str
    from_user: User
    data: Optional[str] = None
    message: Optional[Message] = None
    chat_instance: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Optional[Dict]) -> Optional["CallbackQuery"]:
        if not data:
            return None
        return cls(
            id=data.get("id", ""),
            from_user=User.from_dict(data.get("from")),
            data=data.get("data"),
            message=Message.from_dict(data.get("message")),
            chat_instance=data.get("chat_instance")
        )

@dataclass
class Update:
    """کلاس Update برای نمایش آپدیت تلگرام"""
    update_id: int
    message: Optional[Message] = None
    callback_query: Optional[CallbackQuery] = None
    edited_message: Optional[Message] = None
    channel_post: Optional[Message] = None
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Update":
        return cls(
            update_id=data.get("update_id", 0),
            message=Message.from_dict(data.get("message")),
            callback_query=CallbackQuery.from_dict(data.get("callback_query")),
            edited_message=Message.from_dict(data.get("edited_message")),
            channel_post=Message.from_dict(data.get("channel_post"))
        )

def parse_update(raw: Dict) -> Update:
    """تبدیل دیکشنری خام تلگرام به آبجکت Update"""
    return Update.from_dict(raw)
