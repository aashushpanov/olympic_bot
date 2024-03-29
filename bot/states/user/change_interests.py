from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from filters import TimeAccess
from utils.db.add import add_interests, add_olympiads_to_track, change_users_files
from utils.db.get import get_user, get_subjects, get_olympiads, get_tracked_olympiads
from utils.menu.menu_structure import list_menu, interest_menu
from utils.menu.user_menu import add_new_interests_call, add_interest_call, confirm
from utils.menu.generator_functions import del_interest_call


class AddNewInterests(StatesGroup):
    get_interest = State()


def register_add_interests_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(start, add_new_interests_call.filter(), TimeAccess(), state='*')
    dp.register_callback_query_handler(add_new_interests, add_interest_call.filter(), TimeAccess(), state=AddNewInterests.get_interest)
    dp.register_callback_query_handler(parsing_interests, confirm.filter(), state=AddNewInterests.get_interest)
    dp.register_callback_query_handler(delete_interest, del_interest_call.filter(), TimeAccess())


async def start(callback: types.CallbackQuery, state: FSMContext):
    await AddNewInterests.get_interest.set()
    await state.update_data({'interest': set()})
    message = callback.message
    await message.delete()
    await list_menu(message, menu=interest_menu, title='''Добавьте предметы, которыми вы интересуетесь, после выбора нажмите "готово"''')


async def add_new_interests(callback: types.CallbackQuery, state: FSMContext, callback_data: dict = None):
    user = str(callback.from_user.id)
    state.storage.data.get(user).get(user).get('data').get('interest').add(callback_data.get('data'))
    await callback.answer('Запомним')


async def parsing_interests(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = await state.get_data()
    interests_new = data.get('interest')
    interests_exist = set(get_user(user_id)['interest'])
    interests_add = interests_new.union(interests_exist)
    status = add_interests(user_id, list(interests_add))
    if status == 0:
        await callback.message.answer('Что-то пошло не так.')
    user = get_user(user_id)
    current_interests = user['interest']
    subjects = get_subjects()
    interests_name = list(subjects[subjects['id'].isin(current_interests)]['name'].values)
    await callback.message.delete()
    await callback.message.answer('Текущие отслеживаемые предметы:\n{}'.format('\n'.join(interests_name)))
    new_olympiads, status = update_olympiads_to_track(user_id)
    if status:
        if not new_olympiads.empty:
            await callback.message.answer('Следующие олимпиады за ваш класс добавлены в отслеживаемые:\n{}'
                                          .format('\n'.join(list(new_olympiads['name']))))
            change_users_files(user_id, ['status_file'])
        else:
            await callback.message.answer('К сожалению, новых олимпиад по этим предметам нет.')
    else:
        await callback.message.answer('Что-то пошло не так.')
    await state.finish()


async def delete_interest(callback: types.CallbackQuery, callback_data: dict):
    user_id = callback.from_user.id
    interest_id = callback_data.get('data')
    interest = list(get_user(user_id)['interest'])
    try:
        interest.remove(interest_id)
        status = add_interests(user_id, interest)
        if status:
            await callback.answer('Удалено')
        else:
            await callback.answer('Что-тот пошло не так.')
    except ValueError:
        pass


def update_olympiads_to_track(user_id):
    olympiads = get_olympiads()
    user = get_user(user_id)
    tracked = list(get_tracked_olympiads(user_id)['olympiad_id'].values)
    new_olympiads = olympiads[(olympiads['subject_id'].isin(user['interest'])) &
                              (olympiads['grade'] == int(user['grade'])) &
                              (olympiads['is_active'] == 1) & (~olympiads['id'].isin(tracked))]
    if not new_olympiads.empty:
        status = add_olympiads_to_track(new_olympiads, user_id)
    else:
        status = 1
    return new_olympiads, status


