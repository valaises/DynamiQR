import aiohttp
from ast import literal_eval


async def get_request(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.json()


async def post_request(url: str, data: dict):
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, json=data) as resp:
            return resp.status


async def create_user(id: int, link_limit: int = 3):
    return await post_request(url=f'http://dynamiqr.xyz/create_user',
                              data=dict(user_id=id,
                                        link_limit=link_limit))


async def get_user(id: int):
    return await get_request(url=f'http://dynamiqr.xyz/user/{id}')


# async def update_user():
#     return await post_request(url='http://dynamiqr.xyz', data=dict())


async def get_user_links(id: int):
    return await get_request(url=f'http://dynamiqr.xyz/user/{id}/links_list')


async def get_user_link(link_id: int, user_id: int):
    return await get_request(url=f'http://dynamiqr.xyz/user/{user_id}/links/{link_id}')


async def create_user_link(user_id: int, link_id: int, link_text: str):
    return await post_request(url=f'http://dynamiqr.xyz/add_link',
                              data=dict(owner_id=user_id, link_id=link_id, link_text=link_text))


async def change_link_text(user_id: int, link_id: int, link_text: str):
    return await post_request(url=f'http://dynamiqr.xyz/change_link_text',
                              data=dict(owner_id=user_id, link_id=link_id, link_text=link_text))
