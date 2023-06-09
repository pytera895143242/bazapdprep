from aiogram import Bot, types
import logging
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import asyncio
import sqlite3
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

memory_storage = MemoryStorage()
bot = Bot(token='6078917054:AAH-rWFRtmaVOypmnz_xtwcLe6FK2ZtyyFw',parse_mode='html')
dp = Dispatcher(bot,storage=memory_storage)
logging.basicConfig(level=logging.INFO)


db = sqlite3.connect('server.db')
sql = db.cursor()

def reg_user(id):
    sql.execute(""" CREATE TABLE IF NOT EXISTS user_time (
            id BIGINT,
            status_ref
            ) """)

    sql.execute(f"SELECT id FROM user_time WHERE id ='{id}'")
    if sql.fetchone() is None:
        sql.execute(f"INSERT INTO user_time VALUES (?,?)", (id, 0))
        db.commit()

def info_members():
    db = sqlite3.connect('server.db')
    sql = db.cursor()
    a = sql.execute(f'SELECT COUNT(*) FROM user_time').fetchone()[0]
    return a

class st_reg(StatesGroup):
    st_name = State()
    st_fname = State()
    step_q = State()
    step_regbutton = State()


########################  Рассылка  ################################
@dp.callback_query_handler(text='write_message')  # АДМИН КНОПКА Рассылка пользователям
async def check(call: types.callback_query, state: FSMContext):
    murkap = types.InlineKeyboardMarkup()
    bat0 = types.InlineKeyboardButton(text='ОТМЕНА', callback_data='otemena')
    murkap.add(bat0)
    await bot.send_message(call.message.chat.id, 'Перешли мне уже готовый пост и я разошлю его всем юзерам',
                           reply_markup=murkap)
    await st_reg.step_q.set()
    await bot.answer_callback_query(call.id)


@dp.callback_query_handler(text='otemena', state='*')
async def otmena_12(call: types.callback_query, state: FSMContext):
    await bot.send_message(call.message.chat.id, 'Отменено')
    await state.finish()
    await bot.answer_callback_query(call.id)


@dp.message_handler(state=st_reg.step_q,
                    content_types=['text', 'photo', 'video', 'video_note', 'voice'])  # Предосмотр поста
async def redarkt_post(message: types.Message, state: FSMContext):
    await st_reg.st_name.set()
    murkap = types.InlineKeyboardMarkup()
    bat0 = types.InlineKeyboardButton(text='ОТМЕНА', callback_data='otemena')
    bat1 = types.InlineKeyboardButton(text='РАЗОСЛАТЬ', callback_data='send_ras')
    bat2 = types.InlineKeyboardButton(text='Добавить кнопки', callback_data='add_but')
    murkap.add(bat1)
    murkap.add(bat2)
    murkap.add(bat0)

    await message.copy_to(chat_id=message.chat.id)
    q = message
    await state.update_data(q=q)

    await bot.send_message(chat_id=message.chat.id, text='Пост сейчас выглядит так 👆', reply_markup=murkap)


# НАСТРОЙКА КНОПОК
@dp.callback_query_handler(text='add_but', state=st_reg.st_name)  # Добавление кнопок
async def addbutton(call: types.callback_query, state: FSMContext):
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    await bot.send_message(call.message.chat.id, text='Отправляй мне кнопки по принципу Controller Bot')
    await st_reg.step_regbutton.set()
    await bot.answer_callback_query(call.id)


@dp.message_handler(state=st_reg.step_regbutton, content_types=['text'])  # Текст кнопок в неформате
async def redarkt_button(message: types.Message, state: FSMContext):
    arr3 = message.text.split('\n')
    murkap = types.InlineKeyboardMarkup()  # Клавиатура с кнопками

    massiv_text = []
    massiv_url = []

    for but in arr3:
        new_but = but.split('-')
        massiv_text.append(new_but[0][:-1])
        massiv_url.append(new_but[1][1:])
        bat9 = types.InlineKeyboardButton(text=new_but[0][:-1], url=new_but[1][1:])
        murkap.add(bat9)

    try:
        data = await state.get_data()
        mess = data['q']  # ID сообщения для рассылки

        await bot.copy_message(chat_id=message.chat.id, from_chat_id=message.chat.id, message_id=mess.message_id,
                               reply_markup=murkap)

        await state.update_data(text_but=massiv_text)  # Обновление Сета
        await state.update_data(url_but=massiv_url)  # Обновление Сета

        murkap2 = types.InlineKeyboardMarkup()  # Клавиатура - меню
        bat0 = types.InlineKeyboardButton(text='ОТМЕНА', callback_data='otemena')
        bat1 = types.InlineKeyboardButton(text='РАЗОСЛАТЬ', callback_data='send_ras')
        murkap2.add(bat1)
        murkap2.add(bat0)

        await bot.send_message(chat_id=message.chat.id, text='Теперь твой пост выглядит так☝', reply_markup=murkap2)


    except:
        await bot.send_message(chat_id=message.chat.id, text='Ошибка. Отменено')
        await state.finish()


# КОНЕЦ НАСТРОЙКИ КНОПОК


@dp.callback_query_handler(text='send_ras', state="*")  # Рассылка
async def fname_step(call: types.callback_query, state: FSMContext):
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    data = await state.get_data()
    mess = data['q']  # Сообщения для рассылки

    murkap = types.InlineKeyboardMarkup()  # Клавиатура с кнопками
    try:  # Пытаемся добавить кнопки. Если их нету оставляем клаву пустой
        text_massiv = data['text_but']
        url_massiv = data['url_but']
        for t in text_massiv:
            for u in url_massiv:
                bat = types.InlineKeyboardButton(text=t, url=u)
                murkap.add(bat)
                break

    except:
        pass

    db = sqlite3.connect('server.db')
    sql = db.cursor()
    await state.finish()
    users = sql.execute("SELECT id FROM user_time").fetchall()
    bad = 0
    good = 0
    delit = 0
    await bot.send_message(call.message.chat.id,
                           f"<b>Всего пользователей: <code>{len(users)}</code></b>\n\n<b>Расслыка начата!</b>",
                           parse_mode="html")
    for i in users:
        await asyncio.sleep(0.03)
        try:
            await mess.copy_to(i[0], reply_markup=murkap)
            good += 1
        except (BotBlocked, ChatNotFound):
            try:
                delite_user(i[0])
                delit += 1

            except:
                pass
        except:
            bad += 1

    await bot.send_message(
        call.message.chat.id,
        "<u>Рассылка окончена\n\n</u>"
        f"<b>Всего пользователей:</b> <code>{len(users)}</code>\n"
        f"<b>Отправлено:</b> <code>{good}</code>\n"
        f"<b>Удалено пользователей:</b> <code>{delit}</code>\n"
        f"<b>Произошло ошибок:</b> <code>{bad}</code>",
        parse_mode="html"
    )
    await bot.answer_callback_query(call.id)
#########################################################



@dp.message_handler(commands=['admin'])
async def admin_ka(message: types.Message):
    id = message.from_user.id
    if id == 6086953251:
        markup = types.InlineKeyboardMarkup()
        bat_a = types.InlineKeyboardButton(text='Трафик', callback_data='list_members')
        bat_e = types.InlineKeyboardButton(text='Рассылка', callback_data='write_message')
        bat_j = types.InlineKeyboardButton(text='База', callback_data='baza')
        markup.add(bat_a, bat_e,bat_j)
        await bot.send_message(message.chat.id, 'Выполнен вход в админ панель', reply_markup=markup)


@dp.callback_query_handler(text='baza')
async def baza(call: types.callback_query):
    if call.message.chat.id == 6086953251:
        a = open('server.db','rb')
        await bot.send_document(chat_id=call.message.chat.id, document=a)
    await bot.answer_callback_query(call.id)


@dp.callback_query_handler(text='list_members')  # АДМИН КНОПКА ТРАФИКА
async def check(call: types.callback_query):
    if call.message.chat.id == 6086953251:
        a = info_members()  # Вызов функции из файла sqlit
        await bot.send_message(call.message.chat.id, f'Количество пользователей: {a}')
    await bot.answer_callback_query(call.id)


@dp.message_handler(commands=['start'])
async def command_start(message: types.Message):
    reg_user(message.from_user.id)
    await bot.send_message(chat_id=message.chat.id, text="""✅ https://t.me/+HvKERlJ0n78xZTQx""")


@dp.chat_join_request_handler()
async def command_join(update: types.ChatJoinRequest):
    try:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_1 = types.KeyboardButton('✅ Я нe pобoт')
        markup.add(button_1_1)

        await bot.send_message(chat_id=update.from_user.id, text= """Чтoбы приcоeдинитьcя к нaшему канaлу, необxодимо нажать на кнoпку '✅ Я нe pобoт'""",reply_markup=markup)
        await asyncio.sleep(10)
        try:
            await update.approve()
        except:
            pass
    except:
        pass

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)