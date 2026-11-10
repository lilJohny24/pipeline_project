import asyncio

import aiohttp

#ЧАСТЬ 1

async def fetch_post(session, post_id, semaphore):
    async with semaphore:
        try:
            async with session.get(
                f'https://jsonplaceholder.typicode.com/posts/{post_id}',
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                response.raise_for_status()
                return await response.json()
        except Exception:
            return None


async def start_log_func(post_id):
    print(f'Начало загрузки поста {post_id}')


async def fetch_post_then_log_func(session, post_id, semaphore):
    await start_log_func(post_id)
    return await fetch_post(session, post_id, semaphore)


async def fetch_all_posts(post_ids=None):
    if post_ids is None:
        post_ids = range(1, 101)
    semaphore = asyncio.Semaphore(5)
    async with aiohttp.ClientSession() as session:
        tasks = [
            asyncio.create_task(fetch_post_then_log_func(session, pid, semaphore))
            for pid in post_ids
        ]
        return await asyncio.gather(*tasks)

#print(asyncio.run(fetch_all_posts()))



