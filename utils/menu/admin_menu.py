from aiogram.utils.callback_data import CallbackData

from utils.menu.MenuNode import MenuNode

set_olympiads_call = CallbackData('set_olympiads')
set_subjects_call = CallbackData('set_subjects')
set_olympiads_dates_call = CallbackData('set_olympiads_dates')
set_admins_call = CallbackData('set_admins')


def set_admin_menu(main_node):
    admin_menu = MenuNode("Меню администратора")
    if main_node:
        main_node.set_child(admin_menu)

    admin_menu.set_childs([
        MenuNode('Данные олимпиад'),
        MenuNode('admin_1'),
        MenuNode('admin_2')
    ])

    admin_menu.child(text='Данные олимпиад').set_childs([
        MenuNode('Добавить предметы', callback=set_subjects_call.new()),
        MenuNode('Добавить олимпиады', callback=set_olympiads_call.new()),
        MenuNode('Установить даты этапов', callback=set_olympiads_dates_call.new()),
    ])

    admin_menu.child(text='admin_1').set_childs([
        MenuNode('admin_1_0'),
        MenuNode('admin_1_1'),
        MenuNode('admin_1_2')
    ])

    admin_menu.child(text='admin_2').set_childs([
        MenuNode('admin_2_0'),
        MenuNode('admin_2_1'),
        MenuNode('admin_2_2')
    ])

    # all_childs = admin_menu.all_childs()

    return admin_menu


def set_group_admin_menu():
    group_admin_menu = MenuNode('Меню')

    group_admin_menu.set_childs([
        MenuNode(text='Установить администраторов', callback=set_admins_call.new())
    ])

    return group_admin_menu
