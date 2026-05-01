import asyncio


def retry(attempts=3, base_delay=5):
    def decorator(fn):
        async def wrapper(*args, **kwargs):
            for attempt in range(attempts):
                try:
                    return await fn(*args, **kwargs)
                except Exception as e:
                    if attempt == attempts - 1:
                        raise
                    await asyncio.sleep(base_delay * (2 ** attempt))
        return wrapper
    return decorator
