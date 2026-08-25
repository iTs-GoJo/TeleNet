class MemoryStorage:
    def __init__(self):
        self.data = {}
    async def set(self, key, value):
        self.data[key] = value
    async def get(self, key, default=None):
        return self.data.get(key, default)
    async def delete(self, key):
        self.data.pop(key, None)