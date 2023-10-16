from aiogram import Router, Bot, types, F
from aiogram.filters import Command
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import re
from worker import gomain
import pickle
from tasks import add_to_queu_task
from create_db import db



router = Router()


class CheckParam(StatesGroup):
    PARAM = State()

class AddPostToQueue(StatesGroup):
    PARAMS = State()




def get_users():
    users_data = []
    with open('users.txt', 'r') as f:
        acc_list = f.readlines()
        for line in acc_list:
            user_data = line.split(':')
            users_data.append(user_data)
    return users_data



def save_queue_state(queue):
    queue_state = [job.key for job in queue.jobs]
    with open("queue_state.pkl", "wb") as file:
        pickle.dump(queue_state, file)


@router.message(Command('start'))
async def cmd_start(message: types.Message, bot: Bot):
    await star(message, bot) 

    
async def star(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    keys = [
        [types.InlineKeyboardButton(text='меню', callback_data="main")],
    ]
    kb = types.InlineKeyboardMarkup(inline_keyboard=keys)
    await bot.send_message(chat_id=user_id, text='Привет ', reply_markup = kb, parse_mode='HTML')
    

@router.callback_query(lambda c: re.match(r'^main', c.data))
async def get_list(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await state.clear()
    keys = [
        [types.InlineKeyboardButton(text='Добавить пост в очередь', callback_data="add_post")],
        [types.InlineKeyboardButton(text='Статистика', callback_data="stats")],

    ]
    kb = types.InlineKeyboardMarkup(inline_keyboard=keys)
    await call.message.answer("Выберите действие:", reply_markup=kb)



@router.callback_query(lambda c: c.data == 'add_post')
async def add_post(call: types.CallbackQuery, state: FSMContext):
    keys = [
        [types.InlineKeyboardButton(text='На Главную', callback_data="main")],

    ]
    kb = types.InlineKeyboardMarkup(inline_keyboard=keys)
    await state.set_state(AddPostToQueue.PARAMS)
    await call.message.answer("Введи через пробел количество апвотов, задержка между вотами в секундах, ссылка на пост. \nПример - 50 15 http://red.com - для 50 вотов, будут проставляться через 15 секунд каждый", reply_markup=kb)


@router.message(AddPostToQueue.PARAMS, F.text)
async def process_add_location(message: types.Message, state: FSMContext):
    params = message.text.split(' ')
    keys = [
        [types.InlineKeyboardButton(text='На Главную', callback_data="main")],
    ]
    kb = types.InlineKeyboardMarkup(inline_keyboard=keys)
    
    await message.answer('Добавлено', reply_markup=kb)
    await state.clear()
    db.db_add_param_from_usr(params)
    await add_to_queu_task(params)
    


@router.callback_query(lambda c: c.data == 'stats')
async def stats(call: types.CallbackQuery, state: FSMContext):
    all_params = db.db_get_all_params()
    text = 'Введи ссылку чтоб получить статистику по работе\nВсе добавленные ссылки:\n'
    for param in all_params:
        if param[4] == 1:
            done = 'да'
        else:
            done = 'нет'
        text += f"""{param[3]} добавлена <a href="{param[0]}">ссылка</a> na {param[1]} вотов, окончено - {done}\n"""
    keys = [
        [types.InlineKeyboardButton(text='Отмена', callback_data="main")],
    ]
    kb = types.InlineKeyboardMarkup(inline_keyboard=keys)
    await state.set_state(CheckParam.PARAM)
    await call.message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.message(CheckParam.PARAM, F.text)
async def param_info(message: types.Message, state: FSMContext):
    url = message.text
    jobs = db.get_jobs_where_url(url)
    print(jobs)
    done = 0
    err = 0
    for job in jobs:
        if job[4] == 'upvote_ok':
            done += 1
        else:
            err += 1
    text = f"{url}\n\n Успешно: {done}"
    keys = [
        [types.InlineKeyboardButton(text='На главную', callback_data="main")],
    ]
    kb = types.InlineKeyboardMarkup(inline_keyboard=keys)
    await state.clear()
    await message.answer(text, reply_markup=kb)
        


