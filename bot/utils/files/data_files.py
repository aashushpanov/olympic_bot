import pandas as pd

from ...utils.db.get import get_olympiads, get_subjects, get_users, get_all_olympiads_status, get_answers, \
    get_class_managers, get_admins


def make_users_file(user_id):
    file_path = 'data/files/to_send/users.xlsx'
    users = get_users(user_id)
    columns = ['Фамилия', 'Имя', 'Класс']
    users['grade_label'] = users['grade'].astype(str) + users['literal']
    users_file = users[['last_name', 'first_name', 'grade_label', 'is_admin']]
    users_file = users_file[users_file['is_admin'] == 0]
    users_file.drop(columns=['is_admin'], inplace=True)
    users_file.columns = columns
    users_file.to_excel(file_path, index=False)
    return file_path, users_file


def make_class_managers_file():
    file_path = 'data/files/to_send/class_managers.xlsx'
    class_managers = get_class_managers()
    columns = ['Фамилия', 'Имя', 'Классы']
    class_managers_file = pd.DataFrame(columns=columns)
    for _, row in class_managers.iterrows():
        grade_list = row['grades'].replace(' ', '')
        class_manager = pd.DataFrame([[row['l_name'], row['f_name'], ', '.join(grade_list)]], columns=columns)
        class_managers_file = pd.concat([class_managers_file, class_manager], axis=0)
    class_managers_file.to_excel(file_path, index=False)
    return file_path, class_managers_file


def make_olympiads_with_dates_file():
    file_path = 'data/files/to_send/all_olympiads.xlsx'
    olympiads = get_olympiads()
    subjects = get_subjects()
    olympiads = olympiads.join(subjects.set_index('id'), on='subject_id')
    olympiads_groups = olympiads.groupby(['name', 'start_date', 'end_date'])
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
        active = 'Да' if group['is_active'].iloc[0] else 'Нет'
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
    return file_path, olympiads_file


def make_olympiads_status_file(user_id):
    file_path = 'data/files/to_send/status_file.xlsx'
    users = get_users()
    olympiads = get_olympiads()
    subjects = get_subjects()
    olympiads_status = get_all_olympiads_status(user_id)
    olympiads_status = olympiads_status.join(olympiads.set_index('id'), on='olympiad_id', rsuffix='real')
    olympiads_status = olympiads_status.join(subjects.set_index('id'), on='subject_id')
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
        key = olympiad_status['key']
        match olympiad_status['status_code']:
            case 0:
                status = 'Добавлена'
            case 1:
                status = 'Зарегистрирован'
            case 2:
                status = 'Пройдена'
            case -1:
                status = 'Пропущена'
            case _:
                status = 'Не определен'
        new_olympiad_status = pd.DataFrame([[f_name, l_name, grade, olympiad_name, subject, key, status]],
                                           columns=columns)
        status_file = pd.concat([status_file, new_olympiad_status], axis=0)
    status_file.to_excel(file_path, index=False)
    return file_path, status_file


def make_answers_file():
    file_path = 'data/files/to_send/answers_file.xlsx'
    answers = get_answers()
    admins = get_admins()
    answers = answers.join(admins.set_index('admin_id'), on='to_admin')
    columns = ['Номер вопроса', 'Вопрос', 'Ответ', 'Дал ответ']
    answers_file = pd.DataFrame(columns=columns)
    for _, row in answers.iterrows():
        question_no = row['no']
        question = row['message']
        answer = row['answer']
        from_admin = '{} {}'.format(row['last_name'], row['first_name'])
        answer_row = pd.DataFrame([[question_no, question, answer, from_admin]], columns=columns)
        answers_file = pd.concat([answers_file, answer_row], axis=0)
    answers_file.to_excel(file_path, index=False)
    return file_path, answers_file
