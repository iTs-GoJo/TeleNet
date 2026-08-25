import asyncio
async def retry_async(func, retries=3, delay=1):
    for i in range(retries):
        try:
            return await func()
        except Exception as e:
            if i == retries - 1: raise
            await asyncio.sleep(delay)