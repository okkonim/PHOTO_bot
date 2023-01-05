import logging
import sqlite3

import aiogram_calendar
from aiogram import Bot, Dispatcher
from aiogram import types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils import executor
from aiogram_calendar import simple_cal_callback, SimpleCalendar
from telegram.ext import Updater

import config
import media
import messages

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
updater = Updater(config.API_TOKEN, use_context=True)


class BotStatesGroup(StatesGroup):
    examples = State()
    advices = State()
    questionnaire = State()
    questionnaire_time = State()


async def on_startup(_):
    print('Бот запущен.')


def menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(messages.to_menu))


def time_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(types.KeyboardButton(text='12:00'),
                                                                                 types.KeyboardButton(text='14:00'),
                                                                                 types.KeyboardButton(text='16:00'),
                                                                                 types.KeyboardButton(text='18:00'),
                                                                                 types.KeyboardButton(
                                                                                     text=messages.to_menu))


@dp.message_handler(commands=['start'])
async def start(message: types.Message, state: FSMContext):
    people_id = message.chat.id
    conn = sqlite3.connect(config.DATABASE, check_same_thread=False)
    cursor = conn.cursor()
    try:

        print("Подключен к SQLite")
        cursor.execute('SELECT user_id FROM clients WHERE user_id = "{}"'.format(people_id))
        conn.commit()
        data = cursor.fetchone()
        conn.commit()
        if data is None:
            cursor.execute('INSERT INTO clients(user_id, user_name, username) VALUES (?, ?, ?)',
                           (message.from_user.id, message.from_user.first_name,
                            message.from_user.username))
            conn.commit()
            await bot.send_message(message.chat.id,
                                   text=messages.start_message.format(message.from_user))
            await menu(message, state)
        else:
            await bot.send_message(message.chat.id, text=messages.comeback_message.format(message.from_user))
            await menu(message, state)
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if conn:
            conn.close()
        print("Соединение с SQLite закрыто")


@dp.message_handler(text=messages.to_menu)
async def menu(message: types.Message, state: FSMContext):
    await state.finish()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    types_button = types.KeyboardButton(messages.types_of_photography)
    examples_button = types.KeyboardButton(messages.work_examples)
    contacts_button = types.KeyboardButton(messages.contact_with_the_photographer)
    advice_button = types.KeyboardButton(messages.advice)
    enroll_button = types.KeyboardButton(messages.enroll)
    keyboard.add(types_button, examples_button, contacts_button, advice_button, enroll_button)
    await message.answer(
        text="Что Вы хотите сделать?",
        reply_markup=keyboard)
    await message.delete()


@dp.message_handler(text=messages.types_of_photography)
async def types_handler(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    menu_button = types.KeyboardButton(text=messages.to_menu)
    enroll_button = types.KeyboardButton(messages.enroll)
    contacts_button = types.KeyboardButton(messages.contact_with_the_photographer)
    keyboard.add(menu_button, enroll_button, contacts_button)
    await message.answer(
        text=messages.uslugi_message, reply_markup=keyboard)
    await message.delete()


@dp.message_handler(text=messages.work_examples)
async def primeri_rabot_handler(message: types.Message):
    await BotStatesGroup.examples.set()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    portrait_button = types.KeyboardButton(text=messages.portrait)
    family_photoset_button = types.KeyboardButton(text=messages.family_photoset)
    pets_photoset_button = types.KeyboardButton(text=messages.pets_photoset)
    grade_photoet_button = types.KeyboardButton(text=messages.grade_photoset)
    retouch_button = types.KeyboardButton(text=messages.retouch)
    menu_button = types.KeyboardButton(text=messages.to_menu)
    keyboard.add(portrait_button, family_photoset_button, pets_photoset_button, grade_photoet_button, retouch_button,
                 menu_button)
    await message.answer(text=messages.examples_question,
                         reply_markup=keyboard)


@dp.message_handler(state=BotStatesGroup.examples, text=messages.portrait)
async def portrait_examples(message: types.Message, state: FSMContext):
    await bot.send_photo(message.chat.id, photo=media.portrait_example1)
    await bot.send_photo(message.chat.id, photo=media.portrait_example2)
    await bot.send_photo(message.chat.id, photo=media.portrait_example3)
    await state.finish()
    await bot.send_message(message.chat.id, text=messages.back_message, reply_markup=menu_keyboard())


@dp.message_handler(state=BotStatesGroup.examples, text=messages.family_photoset)
async def family_photoset_examples(message: types.Message, state: FSMContext):
    await bot.send_photo(message.chat.id, photo=media.family_photoset_example1)
    await bot.send_photo(message.chat.id, photo=media.family_photoset_example2)
    await state.finish()
    await bot.send_message(message.chat.id, text=messages.back_message, reply_markup=menu_keyboard())


@dp.message_handler(state=BotStatesGroup.examples, text=messages.pets_photoset)
async def family_photoset_examples(message: types.Message, state: FSMContext):
    await bot.send_photo(message.chat.id, photo=media.pets_photoset_example1)
    await bot.send_photo(message.chat.id, photo=media.pets_photoset_example2)
    await state.finish()
    await bot.send_message(message.chat.id, text=messages.back_message, reply_markup=menu_keyboard())


@dp.message_handler(state=BotStatesGroup.examples, text=messages.grade_photoset)
async def grade_photoset_examples(message: types.Message, state: FSMContext):
    await bot.send_photo(message.chat.id, photo=media.grade_photoset_example1)
    await bot.send_photo(message.chat.id, photo=media.grade_photoset_example2)
    await state.finish()
    await bot.send_message(message.chat.id, text=messages.back_message, reply_markup=menu_keyboard())


@dp.message_handler(state=BotStatesGroup.examples, text=messages.retouch)
async def retouch_examples(message: types.Message, state: FSMContext):
    await bot.send_photo(message.chat.id, photo=media.retouch_example1)
    await state.finish()
    await bot.send_message(message.chat.id, text=messages.back_message, reply_markup=menu_keyboard())


@dp.message_handler(text=messages.contact_with_the_photographer)
async def contacts_handler(message: types.Message):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    telega = InlineKeyboardButton(text=messages.link_tg_message, url=messages.link_tg)
    vk = InlineKeyboardButton(text=messages.link_vk_message, url=messages.link_vk)
    keyboard.add(telega, vk)
    await message.answer(text="Контакты фотографа ниже:", reply_markup=keyboard)
    await message.delete()
    await message.answer(text=messages.back_message, reply_markup=menu_keyboard())


@dp.message_handler(text=messages.advice)
async def advices_handler(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button1 = types.KeyboardButton(text=messages.advice1)
    button2 = types.KeyboardButton(text=messages.advice2)
    button3 = types.KeyboardButton(text=messages.advice3)
    button4 = types.KeyboardButton(text=messages.advice4)
    button5 = types.KeyboardButton(text=messages.advice5)
    button6 = types.KeyboardButton(text=messages.advice6)
    button7 = types.KeyboardButton(text=messages.advice7)
    keyboard.add(button1, button2, button3, button4, button5, button6, button7)
    await BotStatesGroup.advices.set()
    await message.answer(
        text=messages.advice_message_main, reply_markup=keyboard)
    # await message.answer(text=messages.back_message, reply_markup=menu_keyboard())
    await message.delete()


@dp.message_handler(text=messages.advice1, state=BotStatesGroup.advices)
async def advice1_handler(message: types.Message, state: FSMContext):
    await message.answer(text=messages.advice1_text)
    await state.finish()
    await bot.send_message(message.chat.id, text=messages.back_message, reply_markup=menu_keyboard())


@dp.message_handler(text=messages.advice2, state=BotStatesGroup.advices)
async def advice2_handler(message: types.Message, state: FSMContext):
    await message.answer(text=messages.advice2_text)
    await state.finish()
    await bot.send_message(message.chat.id, text=messages.back_message, reply_markup=menu_keyboard())


@dp.message_handler(text=messages.advice3, state=BotStatesGroup.advices)
async def advice3_handler(message: types.Message, state: FSMContext):
    await message.answer(text=messages.advice3_text)
    await state.finish()
    await bot.send_message(message.chat.id, text=messages.back_message, reply_markup=menu_keyboard())


@dp.message_handler(text=messages.advice4, state=BotStatesGroup.advices)
async def advice4_handler(message: types.Message, state: FSMContext):
    await message.answer(text=messages.advice4_text)
    await state.finish()
    await bot.send_message(message.chat.id, text=messages.back_message, reply_markup=menu_keyboard())


@dp.message_handler(text=messages.advice5, state=BotStatesGroup.advices)
async def advice5_handler(message: types.Message, state: FSMContext):
    await message.answer(text=messages.advice5_text)
    await state.finish()
    await bot.send_message(message.chat.id, text=messages.back_message, reply_markup=menu_keyboard())


@dp.message_handler(text=messages.advice6, state=BotStatesGroup.advices)
async def advice6_handler(message: types.Message, state: FSMContext):
    await message.answer(text=messages.advice6_text)
    await state.finish()
    await bot.send_message(message.chat.id, text=messages.back_message, reply_markup=menu_keyboard())


@dp.message_handler(text=messages.advice7, state=BotStatesGroup.advices)
async def advice7_handler(message: types.Message, state: FSMContext):
    await message.answer(text=messages.advice7_text)
    await state.finish()
    await bot.send_message(message.chat.id, text=messages.back_message, reply_markup=menu_keyboard())


@dp.message_handler(text=messages.enroll)
async def enroll_handler(message: types.Message):
    await BotStatesGroup.questionnaire.set()
    await message.answer(messages.calendar_message,
                         reply_markup=await aiogram_calendar.SimpleCalendar().start_calendar())


@dp.callback_query_handler(simple_cal_callback.filter(), state=BotStatesGroup.questionnaire)
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: dict):
    selected, calendar_date = await SimpleCalendar().process_selection(callback_query, callback_data)
    ch_date = calendar_date.strftime("%d:%m:%Y")
    if selected:
        conn = sqlite3.connect(config.DATABASE, check_same_thread=False)
        cursor = conn.cursor()
        try:

            print("Подключен к SQLite")
            cursor.execute(
                "UPDATE clients  SET  date = ? WHERE user_id = ?", (ch_date, callback_query.from_user.id))
            conn.commit()
            print("Запись о дате записи пользователя '{}' успешно обновлена".format(callback_query.from_user.username))
            await callback_query.message.answer(
                text=f'Вы выбрали  {ch_date}. Пожалуйста, выберите время',
                reply_markup=time_keyboard()
            )
            cursor.close()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
        finally:
            if conn:
                conn.close()
            print("Соединение с SQLite закрыто")
            await BotStatesGroup.questionnaire_time.set()


@dp.message_handler(state=BotStatesGroup.questionnaire_time)
async def select_time(message: types.Message, state: FSMContext):
    ch_time = message.text
    conn = sqlite3.connect(config.DATABASE, check_same_thread=False)
    cursor = conn.cursor()
    try:

        print("Подключен к SQLite")
        cursor.execute(
            "UPDATE clients  SET  time = '{}' WHERE user_id = '{}'".format(ch_time, message.chat.id))
        conn.commit()
        print("Запись о времени записи пользователя '{}' успешно обновлена".format(message.from_user.username))
        await state.finish()
        await message.answer(text=messages.enroll_sucsess, reply_markup=menu_keyboard())
        cursor.execute('SELECT date FROM clients WHERE user_id = "{}"'.format(message.from_user.id))
        conn.commit()
        ch_date = cursor.fetchone()
        conn.commit()
        await bot.send_message('687155947', text="Пользователь {} (@{}) запросил запись на {}, - {}".format(
            message.from_user.first_name, message.from_user.username, ch_date, ch_time))
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if conn:
            conn.close()
        print("Соединение с SQLite закрыто")


if __name__ == '__main__':
    if config.API_TOKEN == "":
        print("Нет токена. Вставьте токен.")
    else:
        executor.start_polling(dp, skip_updates=True)
