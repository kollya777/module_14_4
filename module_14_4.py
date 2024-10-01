from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3

api = "7721417736:AAFGUAn2ezjLIh-LBa2g46GdiOftdPCkTHE"
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())
kb = ReplyKeyboardMarkup(resize_keyboard=True)
button_1 = KeyboardButton(text='Рассчитать')
button_2 = KeyboardButton(text='Информация')
kb.row(button_1, button_2)
button_3 = KeyboardButton(text='Купить')
kb.add(button_3)
kb_inl = InlineKeyboardMarkup()
kb_inl2 = InlineKeyboardMarkup()
button_kb_1 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button_kb_2 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
kb_inl.add(button_kb_1)
kb_inl.add(button_kb_2)


def initiate_db():
    connection = sqlite3.connect('database2.db')
    c = connection.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS Products
                 (id INTEGER PRIMARY KEY, 
                 title TEXT NOT NULL, 
                 description TEXT NOT NULL, 
                 price INTEGER NOT NULL)''')
    c.execute('DELETE FROM Products')
    connection.commit()
    connection.close()


def get_all_products():
    connection = sqlite3.connect('database2.db')
    c = connection.cursor()
    c.execute('SELECT * FROM Products')
    products = c.fetchall()
    connection.close()
    return products


initiate_db()


def add_product(product_id, title, description, price):
    connection = sqlite3.connect('database2.db')
    c = connection.cursor()
    c.execute('INSERT INTO Products (id, title, description, price) VALUES (?, ?, ?, ?)',
              (product_id, title, description, price))
    connection.commit()
    connection.close()


products = [
    (1, 'Product 1', 'Description 1', 100),
    (2, 'Product 2', 'Description 2', 200),
    (3, 'Product 3', 'Description 3', 300),
    (4, 'Product 4', 'Description 4', 400),
]

for product in products:
    add_product(*product)


@dp.message_handler(text='Купить')
async def get_buying_list(message):
    products = get_all_products()
    images = ['image1.png', 'image2.png', 'image3.png', 'image4.png']
    captions = []
    for product in products:
        captions.append(f'Название: {product[1]} | Описание: {product[2]} | Цена: {product[3]}')
    for i in range(len(images)):
        with open(images[i], 'rb') as img:
            await message.answer_photo(img, caption=captions[i], parse_mode='Markdown')
    await message.answer('Выберите продукт для покупки:', reply_markup=kb_inl2)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')


@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer('Привет! Я бот помогающий твоему здоровью.', reply_markup=kb)


@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию', reply_markup=kb_inl)


@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('Формула Миффлина-Сан Жеора: 10 * вес + 6.25 * рост - 5 * возраст - 161')


@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст')
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age_param=message.text)
    await message.answer('Введите свой рост')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth_param=message.text)
    await message.answer('Введите свой вес')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)