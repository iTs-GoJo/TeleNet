from dataclasses import dataclass

@dataclass
class Chat:
    id: int
    type: str = None
    title: str = None
    username: str = None
    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.type = kwargs.get("type")
        self.title = kwargs.get("title")
        self.username = kwargs.get("username")
@dataclass
class Message:
    chat: Chat
    text: str
    message_id: int = None

@dataclass
class CallbackQuery:
    id: str
    from_user: object
    data: str
    message: Message = None

@dataclass
class Update:
    update_id: int
    message: Message = None
    callback_query: CallbackQuery = None

def parse_update(raw):
    msg = None
    cb = None
    if "message" in raw:
        m = raw["message"]
        chat = Chat(**m["chat"]) if "chat" in m else None
        msg = Message(chat=chat, text=m.get("text",""), message_id=m.get("message_id"))
    if "callback_query" in raw:
        c = raw["callback_query"]
        cb = CallbackQuery(id=c["id"], from_user=c["from"], data=c.get("data"), message=msg)
    return Update(update_id=raw.get("update_id",0), message=msg, callback_query=cb)