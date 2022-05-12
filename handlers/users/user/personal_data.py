from aiogram import Dispatcher, types

from utils.db.get import get_user
from utils.menu.user_menu import show_personal_data_call


def register_personal_data_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(show_personal_data, show_personal_data_call.filter())


async def show_personal_data(callback: types.CallbackQuery):
    await callback.answer()
    user = get_user(callback.from_user.id)
    grade = 'Класс: {}'.format(str(user['grade']) + user['literal'])
    first_name = 'Имя: {}'.format(user['first_name'])
    last_name = 'Фамилия: {}'.format(user['last_name'])
    await callback.message.answer("Ваши данные:\n{}\n{}\n{}".format(last_name, first_name, grade))
