class APIError(Exception):
    def __init__(self, message, code=None):
        super().__init__(f"[{code}] {message}" if code else message)
        self.code = code