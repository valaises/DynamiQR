import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text

from . import models, crud, requests, database

API_TOKEN = 'api_token'

models.Base.metadata.create_all(bind=database.engine)
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    with database.GetDB() as db:
        user = crud.get_user(db=db, id=message.from_user.id)
        if not user:
            crud.create_user(db=db, id=message.from_user.id,
                             username=message.from_user.username,
                             fullname=message.from_user.first_name)
            await requests.post_request(f'dynamiqr.xyz/create_user', data=dict(id=id))
            user = crud.get_user(db=db, id=message.from_user.id)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('View my links', 'Add link', 'Help', 'Increase link limit')
    await message.reply(f'You can create N links more', reply_markup=keyboard)


@dp.message_handler(Text(equals='View my links'))
async def get_links(message: types.Message):
    links = await requests.get_request(f'dynamiqr.xyz/user/{message.from_user.id}/links_list')
    if not links:
        await message.reply('No links specified',
                            reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add('Add link'))


@dp.message_handler(commands=['admin'], commands_prefix='/')
async def get_info(message: types.Message):
    user = message.from_user.id
    await message.reply(user)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
