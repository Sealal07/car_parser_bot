# Импортируем необходимые библиотеки
import asyncio  # Для асинхронного программирования
from aiogram import Bot, Dispatcher, types  # Основные компоненты aiogram для работы с Telegram API
from aiogram.filters import Command  # Для обработки команд (начинающихся с /)
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton  # Для создания клавиатуры
import car_bot  # Наш собственный модуль для парсинга автомобилей

# Токен вашего Telegram бота (здесь пример, в реальном коде нужно использовать свой)
TOKEN = '7739193025:AAGTdhOoaPPsI2flcQjfleBefSEGLzuGeHo'

# Создаем экземпляр бота с нашим токеном
bot = Bot(token=TOKEN)
# Создаем диспетчер для обработки входящих сообщений
dp = Dispatcher()

# Создаем клавиатуру с кнопками выбора марки автомобиля
brands_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        # Первый ряд кнопок
        [KeyboardButton(text="Toyota"), KeyboardButton(text="BMW")],
        # Второй ряд кнопок
        [KeyboardButton(text="Audi"), KeyboardButton(text="Mercedes")],
        # Третий ряд кнопок
        [KeyboardButton(text="Kia"), KeyboardButton(text="Hyundai")],
        # Четвертый ряд - кнопка для показа всех марок
        [KeyboardButton(text="Все марки")]
    ],
    resize_keyboard=True  # Автоматически подгонять размер клавиатуры
)

# Обработчик команды /start
@dp.message(Command("start"))
async def start_command(message: types.Message):
    # Отправляем приветственное сообщение с клавиатурой
    await message.answer(
        "🚗 Привет! Я бот для поиска автомобилей на Avito.\n"
        "Выбери марку автомобиля или нажми /help для списка команд.",
        reply_markup=brands_keyboard  # Прикрепляем нашу клавиатуру
    )

# Обработчик команды /help
@dp.message(Command("help"))
async def help_command(message: types.Message):
    # Отправляем сообщение со списком команд
    await message.answer(
        "Доступные команды:\n"
        "/start - начать работу с ботом\n"
        "/help - показать эту справку\n"
        "/brand <марка> - поиск по конкретной марке\n\n"
        "Или просто выбери марку из кнопок ниже!",
        reply_markup=brands_keyboard  # Снова показываем клавиатуру
    )

# Обработчик команды /brand (например: /brand Toyota)
@dp.message(Command("brand"))
async def get_by_brand_command(message: types.Message):
    try:
        # Разбиваем сообщение на части и берем второй элемент (марку)
        brand = message.text.split()[1]
        # Вызываем функцию отправки списка автомобилей
        await send_car_list(message, brand)
    except IndexError:
        # Если пользователь не указал марку после команды
        await message.answer("Пожалуйста, укажите марку после команды /brand")

# Обработчик нажатий на кнопки с марками автомобилей
@dp.message(lambda message: message.text in ["Toyota", "BMW", "Audi", "Mercedes", "Kia", "Hyundai", "Все марки"])
async def handle_brand_selection(message: types.Message):
    # Если выбрана кнопка "Все марки", передаем пустую строку как марку
    brand = message.text if message.text != "Все марки" else ""
    # Вызываем функцию отправки списка автомобилей
    await send_car_list(message, brand)

# Функция для отправки списка автомобилей пользователю
async def send_car_list(message: types.Message, brand: str):
    try:
        # Отправляем сообщение о начале поиска
        await message.answer(f"🔍 Ищу объявления {f'по марке {brand}' if brand else 'по всем маркам'}...")

        # Получаем данные автомобилей из нашего модуля car_bot
        cars_data = car_bot.get_cars(brand)

        # Если данные получены
        if cars_data:
            # Перебираем все найденные автомобили
            for car_info in cars_data:
                # Формируем текст сообщения с информацией об автомобиле
                response_text = (
                    f"🚘 {car_info['title']}\n"  # Название автомобиля
                    f"💰 Цена: {car_info['price']} ₽\n"  # Цена
                    f"📊 {car_info['params']}\n"  # Параметры (год, пробег и т.д.)
                    f"🔗 {car_info['link']}\n"  # Ссылка на объявление
                    f"{'=' * 30}"  # Разделитель между объявлениями
                )
                # Отправляем сообщение с информацией об автомобиле
                await message.answer(response_text)
        else:
            # Если автомобили не найдены
            await message.answer("Не удалось найти объявления. Попробуйте другую марку.")

    except Exception as e:
        # Если произошла ошибка, отправляем сообщение с описанием ошибки
        await message.answer(f"Произошла ошибка: {str(e)}")

# Основная асинхронная функция для запуска бота
async def main():
    # Запускаем опрос серверов Telegram на новые сообщения
    await dp.start_polling(bot)

# Точка входа в программу
if __name__ == "__main__":
    # Запускаем основную функцию в асинхронном режиме
    asyncio.run(main())