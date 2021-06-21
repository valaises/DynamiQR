import asyncio
import io
import logging

import qrcode
from PIL.Image import Image
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

import crud
import database
import models
import requests

API_TOKEN = ''

models.Base.metadata.create_all(bind=database.engine)
logging.basicConfig(level=logging.INFO)


loop = asyncio.get_event_loop()
bot = Bot(token=API_TOKEN, parse_mode='HTML')
dp = Dispatcher(bot, loop=loop, storage=MemoryStorage())


class CreateLinkStates(StatesGroup):
    enter_link = State()


class UpdateLinkStates(StatesGroup):
    enter_link = State()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    with database.GetDB() as db:
        user = crud.get_user(db=db, id=message.from_user.id)
        if not user:
            link_limit = 3
            crud.create_user(db=db, id=message.from_user.id,
                             username=message.from_user.username,
                             fullname=message.from_user.first_name)
            if not await requests.get_user(id=message.from_user.id):
                await requests.create_user(id=message.from_user.id, link_limit=link_limit)
            await bot.send_message(message.chat.id,
                                   text=f'<b>Hello, {message.from_user.username}!</b>\n\n'
                                        f'You can create {link_limit} link(s)'
                                        f'<b>Howto create links: https://habr.com/ru/company/macloud/blog/556452/</b>\n'
                                        f'Check command /menu to create first link!')
        else:
            user = await requests.get_user(id=message.from_user.id)
            await bot.send_message(message.chat.id,
                                   text=f'<b>Hello, {message.from_user.username}!</b>\n\n'
                                        f'You can create {user["link_limit"]} link(s) more\n'
                                        f'Check command /menu to interact with your links')


@dp.callback_query_handler(lambda c: c.data == 'menu')
@dp.message_handler(commands=['menu'])
async def menu(message: types.Message):
    text = '<b>Menu</b>'
    user = await requests.get_user(id=message.from_user.id)
    user_links = await requests.get_user_links(id=message.from_user.id)
    keyboard = types.InlineKeyboardMarkup()
    if user['link_limit'] == 0:
        text += '\nUnfortunately, your links limit is over.\n Contact @valaised'
    else:
        keyboard.row(types.InlineKeyboardButton(text='Add link', callback_data='add_link'))
    if user_links:
        keyboard.row(types.InlineKeyboardButton(text='View my links', callback_data='view_links'))
    await message.answer(text=text, reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data == 'add_link', state=None)
async def add_link(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.message.chat.id, text='Please, enter a new link:')
    await CreateLinkStates.enter_link.set()


@dp.callback_query_handler(lambda c: c.data.startswith('change_link'), state=None)
async def change_link(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback_query.message.chat.id, text='Please, enter a new link:')
    await UpdateLinkStates.enter_link.set()
    await state.update_data(link_id=int(callback_query.data.split(' ')[-1]))


@dp.message_handler(state=UpdateLinkStates.enter_link)
async def upd_link_ans(message: types.Message, state: FSMContext):
    link_text = message.text
    data = await state.get_data()
    await requests.change_link_text(user_id=message.from_user.id, link_id=data.get('link_id'), link_text=link_text)
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[
        types.InlineKeyboardButton(text='Get QR code', callback_data=f'create_qr {data.get("link_id")}'),
        types.InlineKeyboardButton(text='Back to your links', callback_data='view_links')
    ]])
    await state.finish()
    await message.reply(text=f'<b>Your link was updated!:</b>\n\n{link_text}', reply_markup=keyboard)


@dp.message_handler(state=CreateLinkStates.enter_link)
async def add_link_ans(message: types.Message, state: FSMContext):
    link_text = message.text
    user_links = await requests.get_user_links(id=message.from_user.id)
    link_id = message.from_user.id + len(user_links) + 1
    await requests.create_user_link(user_id=message.from_user.id, link_id=link_id, link_text=link_text)
    await state.finish()
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[
        types.InlineKeyboardButton(text='Get QR code', callback_data=f'create_qr {link_id}')
    ]])
    await message.reply(text='Your link was created', reply_markup=keyboard)


def image_to_byte_array(image: Image):
  imgByteArr = io.BytesIO()
  image.save(imgByteArr, format=image.format)
  imgByteArr = imgByteArr.getvalue()
  return imgByteArr


@dp.callback_query_handler(lambda c: c.data.startswith('create_qr'))
async def create_qr(callback_query: types.CallbackQuery):
    link_id = callback_query.data.split(' ')[-1]
    link = f'http://dynamiqr.xyz/user/{callback_query.from_user.id}/links/{link_id}'
    qr = qrcode.QRCode()
    qr.add_data(link)
    qr.make(fit=True)
    img = image_to_byte_array(qr.make_image(fill_color='black', back_color='white'))
    # keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[
    #     types.InlineKeyboardButton(text='Back to your links', callback_data='view_links'),
    #     types.InlineKeyboardButton(text='Menu', callback_data='menu')
    # ]])
    await bot.send_photo(chat_id=callback_query.from_user.id,
                         caption=f'<b>{link}</b>\n\nPress /menu',
                         photo=img)


@dp.callback_query_handler(lambda c: c.data == 'view_links')
async def view_links(callback_query: types.CallbackQuery):
    user_links = await requests.get_user_links(id=callback_query.from_user.id)
    keyboard = types.InlineKeyboardMarkup()
    buttons = (types.InlineKeyboardButton(link['link_text'], callback_data=f'link_options {e}') for e, link in enumerate(user_links))
    for btn in buttons:
        keyboard.row(btn)
    await callback_query.message.edit_text(text='<b>Here are your links</b>', reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data.startswith('link_options'))
async def link_options(callback_query: types.CallbackQuery):
    user_links = await requests.get_user_links(id=callback_query.from_user.id)
    link = user_links[int(callback_query.data.split(' ')[-1])]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[
        types.InlineKeyboardButton(text='Change my link', callback_data=f'change_link {link["link_id"]}'),
        types.InlineKeyboardButton(text='Get QR code', callback_data=f'create_qr {link["link_id"]}'),
        types.InlineKeyboardButton(text='<< Back', callback_data='view_links')
    ]])
    await callback_query.message.edit_text(text=f'<b>You are viewing:</b>\n'
                                                f'{link["link_text"]}\n\n<b>Your static link is:</b>\n'
                                                f'http://dynamiqr/user/{callback_query.from_user.id}/links/{link["link_id"]}', reply_markup=keyboard)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
