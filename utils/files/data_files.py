import pandas as pd

from utils.db.get import get_olympiads, get_subjects, get_users, get_all_olympiads_status


def make_olympiads_with_dates_file():
    file_path = 'data/files/to_send/all_olympiads.xlsx'
    olympiads = get_olympiads()
    subjects = get_subjects()
    olympiads = olympiads.join(subjects.set_index('code'), on='subject_code')
    olympiads_groups = olympiads.groupby(['name', 'start_date', 'finish_date'])
    columns = ['Название', 'Предмет', 'Этап', 'Дата начала', 'Дата окончания', 'мл. класс', 'ст. класс',
               'Активна', 'Ключ', 'Предварительная регистрация', 'Ссылка на сайт олимпиады', 'Ссылка на регистрацию']
    olympiads_file = pd.DataFrame(columns=columns)
    for name, group in olympiads_groups:
        min_grade = group['grade'].min()
        max_grade = group['grade'].max()
        urls = group['urls'].iloc[0]
        site_url = urls.get('site_url')
        reg_url = urls.get('reg_url')
        subject_name = group['subject_name'].iloc[0]
        active = 'Да' if group['active'].iloc[0] else 'Нет'
        key_needed = 'Да' if group['key_needed'].iloc[0] else 'Нет'
        pre_registration = 'Да' if group['pre_registration'].iloc[0] else 'Нет'
        stage = group['stage'].iloc[0]
        start_date = name[1].strftime('%d.%m.%y')
        finish_date = name[2].strftime('%d.%m.%y')
        olympiad = pd.DataFrame([[name[0], subject_name, stage, start_date, finish_date, min_grade, max_grade, active,
                                  key_needed, pre_registration, site_url, reg_url]], columns=columns)
        olympiads_file = pd.concat([olympiads_file, olympiad], axis=0)
        # olympiads_file.to_csv(file_path, index=False, sep=';')
    olympiads_file.to_excel(file_path, index=False)
    return file_path


def make_olympiads_status_file():
    file_path = 'data/files/to_send/status_file.xlsx'
    users = get_users()
    olympiads = get_olympiads()
    subjects = get_subjects()
    olympiads_status = get_all_olympiads_status()
    olympiads_status = olympiads_status.join(olympiads.set_index('code'), on='olympiad_code', rsuffix='real')
    olympiads_status = olympiads_status.join(subjects.set_index('code'), on='subject_code')
    olympiads_status = olympiads_status.join(users.set_index('user_id'), on='user_id', rsuffix='user')
    columns = ['Имя', 'Фамилия', 'Класс', 'Олимпиада', 'Предмет', 'Ключ', 'Статус']
    status_file = pd.DataFrame(columns=columns)
    for _, olympiad_status in olympiads_status.iterrows():
        f_name = olympiad_status['first_name']
        l_name = olympiad_status['last_name']
        literal = olympiad_status['literal'] if olympiad_status['literal'] else ''
        grade = str(olympiad_status['grade']) + literal
        olympiad_name = olympiad_status['name']
        subject = olympiad_status['subject_name']
        key = olympiad_status['taken_key']
        match olympiad_status['status']:
            case 'idle':
                status = 'Добавлена'
            case 'reg':
                status = 'Зарегистрирован'
            case 'done':
                status = 'Пройдена'
            case 'missed':
                status = 'Пропущена'
            case _:
                status = 'Не определен'
        new_olympiad_status = pd.DataFrame([[f_name, l_name, grade, olympiad_name, subject, key, status]], columns=columns)
        status_file = pd.concat([status_file, new_olympiad_status], axis=0)
    status_file.to_excel(file_path, index=False)
    return file_path