# keyboards.py

class InlineButton:
    """
    یک دکمه اینلاین که می‌تواند:
    - callback_data داشته باشد (دکمه تعاملی)
    - یا url داشته باشد (دکمه لینک)
    """
    def __init__(self, text, callback_data=None, url=None):
        self.text = text
        self.callback_data = callback_data
        self.url = url

class InlineKeyboard:
    """
    کیبورد اینلاین چند ردیفه
    """
    def __init__(self):
        self.rows = []

    def row(self, *buttons):
        """
        یک ردیف دکمه به کیبورد اضافه می‌کند
        """
        self.rows.append(list(buttons))
        return self

    def to_markup(self):
        """
        خروجی به شکل دیکشنری آماده برای ارسال به تلگرام
        """
        return {
            "inline_keyboard": [
                [
                    {
                        "text": b.text,
                        **({"callback_data": b.callback_data} if b.callback_data else {}),
                        **({"url": b.url} if b.url else {})
                    }
                    for b in row
                ]
                for row in self.rows
            ]
        }