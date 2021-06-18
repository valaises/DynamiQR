import aiohttp


async def get_request(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.text()


async def post_request(url: str, data: dict):
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, data=data) as resp:
            return resp.status
