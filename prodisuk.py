# ПроДисУК - программа дистанционного управления компьютером
# Ссылка на бота: https://vk.com/public203031537
# Сотников Салим, 2021.

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.upload import VkUpload
import random

import datetime
import json

import os
import sys
import platform

from design import Ui_MainWindow
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtWidgets import QInputDialog

import threading

import pyautogui

TOKEN = 'c933c1127f5b19863fd784985cbc05cd5d0641fd27ad49078c902f4a90668cc0156f6d36b92b1bcd300d4'

vk_session = vk_api.VkApi(
    token=TOKEN)
vk = vk_session.get_api()

commands = {'/cmd': True,  # Список команд
            '/msg': True,
            '/screenshot': False,
            '/stop': True,
            '/shutdown': True,
            '/add_confidant': True,
            '/remove_confidant': True,
            '/confidants': False,
            '/change_name': True,
            '/system_info': False,
            '/dir': False,
            '/cd': False,
            '/open_file': False,
            '/slist': False}

# Если программа запускается в первый раз, то имя сессии по умолчанию становится равно имени пользователя.

with open('session_data.json') as file:
    data = json.load(file)
    if data["user_data"]["is_it_first_start"]:
        data["user_data"]["session_name"] = os.environ.get("USERNAME")
        data["user_data"]["is_it_first_start"] = False
with open('session_data.json', 'w') as file:
    json.dump(data, file)

del data


# Функции для отправки фото

def upload_photo(upload, photo):
    response = upload.photo_messages(photo)[0]

    owner_id = response['owner_id']
    photo_id = response['id']
    access_key = response['access_key']

    return owner_id, photo_id, access_key


def send_photo(vk, peer_id, owner_id, photo_id, access_key):
    attachment = 'photo{}_{}_{}'.format(owner_id, photo_id, access_key)
    vk.messages.send(
        random_id=random.randint(0, 2 ** 64),
        peer_id=peer_id,
        attachment=attachment
    )


# Вспомогательные функции

def get_session_name():
    """ Функция получения имени сессии """
    with open('session_data.json') as file:
        data = json.load(file)
    return data["user_data"]["session_name"]


# Классы исключений

class ArgumentCountError(Exception):
    """ Ошибка количества аргументов """

    def __str__(self):
        return 'Неправильное количество аргументов!'


class ArgumentTypeError(Exception):
    """ Ошибка формата или типа аргумента """

    def __str__(self):
        return 'Неправильные аргументы!'


class Session:
    """ Класс сессии """

    def __init__(self):
        self.default_filepath = 'C:/Users/{}/'.format(
            os.environ.get("USERNAME"))
        self.is_run = True

    # feedback - параметр, обозначающий надобность ответного сообщения после выполнения команды.
    # Есть не у всех методов, надобность передачи этого параметра задаётся в словаре commands.

    def cmd(self, event, feedback, args):
        """ Выполняет системную команду """

        os.system(' '.join(args))
        if feedback:
            vk.messages.send(user_id=event.obj.message['from_id'],
                             message="Команда выполнена.",
                             random_id=random.randint(0, 2 ** 64))

    def msg(self, event, feedback, message):
        """ Отправляет сообщение на компьютер """

        os.system('msg {} {}'.format(get_session_name(), ' '.join(message)))
        if feedback:
            vk.messages.send(user_id=event.obj.message['from_id'],
                             message="Сообщение отправлено.",
                             random_id=random.randint(0, 2 ** 64))

    def screenshot(self, event, args):
        """ Отправляет скриншот с компьютера """

        if len(args) == 1:
            pyautogui.screenshot('screenshot.png')

            upload = VkUpload(vk)
            send_photo(vk, event.obj.message['from_id'],
                       *upload_photo(upload, 'screenshot.png'))
            os.remove('screenshot.png')
        else:
            raise ArgumentCountError

    def stop(self, event, feedback, args):
        """ Завершает сессию """

        if len(args) == 1:
            with open('session_data.json') as file:
                data = json.load(file)
            if feedback:
                for index in data['confidants']:
                    for confidant in data['confidants'][index]:
                        vk.messages.send(
                            user_id=confidant,
                            message='Сессия {} завершена.'.format(
                                get_session_name()),
                            random_id=random.randint(0, 2 ** 64))
            self.is_run = False
            window.close()
        else:
            raise ArgumentCountError

    def shutdown(self, event, feedback, args):
        """ Выключает, перезагружает компьютер или выходит из системы """

        if len(args) == 2:
            mode = args[0]
            if mode in ['s' 'r', 'q']:
                modes = {'s': ('/s', 'завершил работу.'),
                         'r': ('/r', 'перезапущен.'),
                         'q': ('/l', 'вышел из системы.')}
                if feedback:
                    vk.messages.send(user_id=event.obj.message['from_id'],
                                     message="Компьютер {} {}".format(
                                         get_session_name(),
                                         modes[mode][0]),
                                     random_id=random.randint(0, 2 ** 64))

                os.system('shutdown {}'.format(modes[mode][0]))
            else:
                raise ArgumentTypeError
        else:
            raise ArgumentCountError

    def add_confidant(self, event, feedback, args):
        """ Добавляет доверенное лицо

        role - роль (администратор или пользователь)
        Администратор может добавлять других доверенных лиц,
        а пользователь нет. Доверенные лица могут управлять сессией."""

        if len(args) == 3:
            if args[0][:15] == 'https://vk.com/' or args[0][:7] == 'vk.com/':
                user_id = args[0].replace('https://', '').replace('vk.com/',
                                                                  '')
                user_id = vk.users.get(user_ids=[user_id])[0]['id']
                role = args[1]
                roles = {'admin': ('Administrators', 'администратор', 'Users'),
                         'user': ('Users', 'пользователь', 'Administrators')}
                with open('session_data.json') as file:
                    data = json.load(file)
                if user_id in data['confidants'][roles[role][2]]:
                    data["confidants"][roles[role][2]].remove(user_id)
                if not feedback or (
                                event.obj.message['from_id'] in
                                data["confidants"][
                                    'Administrators'] and user_id not in
                            data["confidants"][
                                roles[role][0]]):
                    data["confidants"][roles[role][0]].append(user_id)
                    with open('session_data.json', 'w') as file:
                        json.dump(data, file)
                    user = vk.users.get(user_id=user_id)
                    name = ' '.join(
                        [user[0]['first_name'], user[0]['last_name']])
                    if feedback:
                        vk.messages.send(user_id=event.obj.message['from_id'],
                                         message="{} теперь {} сессии {}.".format(
                                             name, roles[role][1],
                                             get_session_name()),
                                         random_id=random.randint(0, 2 ** 64))
                    try:
                        vk.messages.send(user_id=user_id,
                                         message="Вы теперь {} сессии {}.".format(
                                             roles[role][1],
                                             get_session_name()),
                                         random_id=random.randint(0, 2 ** 64))
                    except vk_api.exceptions.ApiError:
                        pass
                else:
                    vk.messages.send(user_id=event.obj.message['from_id'],
                                     message="Нельзя.",
                                     random_id=random.randint(0, 2 ** 64))
            else:
                raise ArgumentTypeError
        else:
            raise ArgumentCountError

    def remove_confidant(self, event, feedback, args):
        """ Удаляет доверенное лицо """

        if len(args) == 3:
            if args[0][:15] == 'https://vk.com/' or args[0][:7] == 'vk.com/':
                user_id = args[0].replace('https://', '').replace('vk.com/',
                                                                  '')
                user_id = vk.users.get(user_ids=[user_id])[0]['id']
                role = args[1]
                roles = {'admin': ('Administrators', 'администратор'),
                         'user': ('Users', 'пользователь')}
                with open('session_data.json') as file:
                    data = json.load(file)
                if not feedback or (
                                event.obj.message['from_id'] in
                                data["confidants"][
                                    'Administrators'] and user_id in
                            data["confidants"][
                                roles[role][0]]):
                    data["confidants"][roles[role][0]].remove(user_id)
                    with open('session_data.json', 'w') as file:
                        json.dump(data, file)
                    window.reinit()
                    user = vk.users.get(user_id=user_id)
                    name = ' '.join(
                        [user[0]['first_name'], user[0]['last_name']])
                    if feedback:
                        vk.messages.send(user_id=event.obj.message['from_id'],
                                         message="{} больше не {} сессии {}.".format(
                                             name, roles[role][1],
                                             get_session_name()),
                                         random_id=random.randint(0, 2 ** 64))
                    try:
                        vk.messages.send(user_id=user_id,
                                         message="Вы больше не {} сессии {}.".format(
                                             roles[role][1],
                                             get_session_name()),
                                         random_id=random.randint(0, 2 ** 64))
                    except vk_api.exceptions.ApiError:
                        pass
                else:
                    vk.messages.send(user_id=event.obj.message['from_id'],
                                     message="Нельзя.",
                                     random_id=random.randint(0, 2 ** 64))
            else:
                raise ArgumentTypeError
        else:
            raise ArgumentCountError

    def confidants(self, event, args):
        """ Отправляет список всех доверенных лиц сессии """

        if len(args) == 1:
            with open('session_data.json') as file:
                data = json.load(file)["confidants"]
                text = []
            for index in data:
                text.append('{}:'.format(index))
                if data[index]:
                    for user_id in data[index]:
                        user = vk.users.get(user_id=user_id,
                                            fields='screen_name')
                        name = ' '.join(
                            [user[0]['first_name'], user[0]['last_name']])
                        short_name = user[0]['screen_name']
                        text.append(
                            '{} - https://vk.com/{}'.format(name, short_name))
                else:
                    text.append('Отсутствуют.')
            vk.messages.send(user_id=event.obj.message['from_id'],
                             message='\n'.join(text),
                             random_id=random.randint(0, 2 ** 64))
        else:
            raise ArgumentCountError

    def change_name(self, event, feedback, args):
        """ Меняет имя сессии """

        if len(args) == 2:
            old_name = get_session_name()
            name = args[0]
            with open('session_data.json') as file:
                data = json.load(file)
                data["user_data"]["session_name"] = name
            with open('session_data.json', 'w') as file:
                json.dump(data, file)
            if feedback:
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message="Название сессии {} изменено на {}.".format(
                                     old_name, name),
                                 random_id=random.randint(0, 2 ** 64))
        else:
            raise ArgumentCountError

    def system_info(self, event, args):
        """ Отправляет информацию о компьютере """

        if len(args) == 1:
            text = ['Имя компьютера:   {}'.format(platform.node()),
                    'Тип машины:       {}'.format(platform.machine()),
                    'Процессор:        {}'.format(platform.processor()),
                    'Система:          {} {}'.format(platform.system(),
                                                     platform.release()),
                    'Версия:           {}'.format(platform.version()),
                    'Платформа:        {}'.format(platform.platform())]
            vk.messages.send(user_id=event.obj.message['from_id'],
                             message='\n'.join(text),
                             random_id=random.randint(0, 2 ** 64))
        else:
            raise ArgumentCountError

    def dir(self, event, args):
        """ Отправляет список файлов и папок в текущей директории """

        filepath = ' '.join(args[:-1]).strip()
        if filepath == '':
            filepath = self.default_filepath
        elif filepath[1:3] != ':/':
            filepath = self.default_filepath + filepath
        elif filepath[-1] != '/':
            filepath += '/'
        vk.messages.send(user_id=event.obj.message['from_id'],
                         message='\n'.join(os.listdir(filepath)),
                         random_id=random.randint(0, 2 ** 64))

    def cd(self, event, args):
        """ Меняет текущую директорию """

        filepath = ' '.join(args[:-1]).strip()
        try:
            if filepath == '..':
                self.default_filepath = '/'.join(
                    self.default_filepath.split('/')[:-1]) + '/'
            else:
                if filepath[-1] != '/':
                    filepath += '/'
                if filepath[1:3] != ':/':
                    self.default_filepath += filepath
                else:
                    self.default_filepath = filepath
                self.dir(event, [self.default_filepath])
        except Exception:
            vk.messages.send(user_id=event.obj.message['from_id'],
                             message='Неправильный путь к файлу.',
                             random_id=random.randint(0, 2 ** 64))

    def open_file(self, event, args):
        """ Отправляет файл (только текстовый или графический) """

        text_formats = ['txt', 'json', 'rtf', 'json', 'ui', 'py']
        image_formats = ['png', 'jpeg', 'jpg', 'gif', 'bmp']
        filepath = args[0]
        if len(args) == 3:
            x = int(args[1]) + 1
            y = x + 1
        elif len(args) == 4:
            x = int(args[1]) + 1
            y = int(args[2]) + 1
        elif len(args) == 2:
            x = 0
            y = 20
        else:
            raise ArgumentCountError
        if filepath[1:3] != ':/':
            filepath = self.default_filepath + filepath
        if os.path.isfile(filepath):
            if filepath.split('.')[1] in text_formats:
                with open(filepath, 'r') as file:
                    text = file.readlines()
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=' '.join(text[x:y]),
                                 random_id=random.randint(0, 2 ** 64))
            elif filepath.split('.')[1] in image_formats:
                upload = VkUpload(vk)
                send_photo(vk, event.obj.message['from_id'],
                           *upload_photo(upload, filepath))

    def slist(self, event):
        """ Отправляет список сессий (не требует имени сессии в синтаксисе)"""

        vk.messages.send(
            message=get_session_name(),
            random_id=random.randint(0, 2 ** 64),
            peer_id=event.obj.message['from_id'],
        )


session = Session()


class ControlPanel(QMainWindow, Ui_MainWindow):
    """ Панель управления """

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.addressee = None  # Адресат для отправки сообщений

        self.setWindowTitle(
            'Панель управления - {}'.format(get_session_name()))

        with open(
                'session_data.json') as file:  # Заполнение списков доверенных лиц
            data = json.load(file)
        user_datas = vk.users.get(
            user_ids=data['confidants']['Administrators'])
        for user in user_datas:
            self.admins.addItem(user['first_name'] + ' ' + user['last_name'])
        user_datas = vk.users.get(user_ids=data['confidants']['Users'])
        for user in user_datas:
            self.users.addItem(user['first_name'] + ' ' + user['last_name'])

        self.admins.itemDoubleClicked.connect(self.remove_admin)
        self.users.itemDoubleClicked.connect(self.remove_user)

        self.admins.itemClicked.connect(self.on_click_admins)
        self.users.itemClicked.connect(self.on_click_users)

        self.add_admin_button.clicked.connect(self.add_confidant)
        self.add_user_button.clicked.connect(self.add_confidant)

        self.change_name_button.clicked.connect(self.change_name)

        self.send_message_button.clicked.connect(self.send_message)

    def send_message(self):
        """ Отправка сообщений """

        try:
            text = self.textEdit.toPlainText()
            if self.addressee:
                user = vk.users.get(user_id=self.addressee)
                name = ' '.join([user[0]['first_name'], user[0]['last_name']])

                self.textEdit.setText('')

                vk.messages.send(user_id=self.addressee,
                                 message='Сообщение от {}: \n {}'.format(
                                     get_session_name(), text),
                                 random_id=random.randint(0, 2 ** 64))
                self.listWidget.addItems(['[{}] Вы -> {}: {}'.format(
                    datetime.datetime.now(), name, text)])
        except Exception as exc:
            self.listWidget.addItem(
                '[{}] Ошибка при отправке: {}'.format(datetime.datetime.now(),
                                                      str(exc)))

    def add_confidant(self):
        """ Добавление доверенного лица """

        roles = {'Добавить админа': 'admin',
                 'Добавить пользователя': 'user'}
        url, ok_pressed = QInputDialog.getText(self, self.sender().text(),
                                               "Введите адрес страницы: ")
        if ok_pressed:
            try:
                session.add_confidant(None, False,
                                      [url, roles[self.sender().text()], ''])
                self.reinit()
            except Exception:
                pass

    def remove_user(self):
        """ Удаление пользователя """

        with open('session_data.json') as file:
            data = json.load(file)
        session.remove_confidant(None, False, ['vk.com/id{}'.format(
            data['confidants']['Users'][self.users.currentRow()]), 'user', ''])
        self.reinit()

    def remove_admin(self):
        """ Удаление администратора """

        with open('session_data.json') as file:
            data = json.load(file)
        session.remove_confidant(None, False, ['vk.com/id{}'.format(
            data['confidants']['Administrators'][self.admins.currentRow()]),
            'admin', ''])
        self.reinit()

    def change_name(self):
        """ Изменение имени сессии """

        name, ok_pressed = QInputDialog.getText(self, 'Изменить имя сессии',
                                                "Введите новое имя: ")
        if ok_pressed:
            try:
                session.change_name(None, False, [name, ''])
                self.reinit()
            except Exception:
                pass

    def on_click_admins(self):
        """ Реакция на выбор элемента в списке администраторов """

        with open('session_data.json') as file:
            data = json.load(file)
        self.addressee = data['confidants']['Administrators'][
            self.admins.currentRow()]  # Адресат меняется на выбранного пользователя
        self.users.setCurrentRow(-1)

    def on_click_users(self):
        """ Реакция на выбор элемента в списке пользователей """

        with open('session_data.json') as file:
            data = json.load(file)
        self.addressee = data['confidants']['Users'][self.users.currentRow()]
        self.admins.setCurrentRow(-1)

    def reinit(self):
        """ Реинициализация окна """

        self.users.clear()
        self.admins.clear()
        self.setWindowTitle(
            'Панель управления - {}'.format(get_session_name()))

        with open('session_data.json') as file:
            data = json.load(file)

        user_datas = vk.users.get(
            user_ids=data['confidants']['Administrators'])
        for user in user_datas:
            self.admins.addItem(user['first_name'] + ' ' + user['last_name'])
        user_datas = vk.users.get(user_ids=data['confidants']['Users'])
        for user in user_datas:
            self.users.addItem(user['first_name'] + ' ' + user['last_name'])

    def closeEvent(self, *args, **kwargs):
        """ Реакция на закрытие окна """
        session.stop(None, True, [''])


class MainThread(threading.Thread):
    """ Класс для независимой работы функции main() """

    def __init__(self, window):
        threading.Thread.__init__(self)
        self.window = window

    def run(self):
        main(self.window)


def main(window):
    """ Основная функция """
    global TOKEN
    global vk_session
    global vk
    global session

    longpoll = VkBotLongPoll(vk_session, '203031537')
    with open('session_data.json') as file:
        confidants = json.load(file)["confidants"]
    for index in confidants:
        for user_id in confidants[index]:
            try:
                vk.messages.send(user_id=user_id,
                                 message="Сессия {} запущена, время: {}".format(
                                     get_session_name(),
                                     datetime.datetime.now()),
                                 random_id=random.randint(0, 2 ** 64))
            except vk_api.exceptions.ApiError:
                pass
    for event in longpoll.listen():
        if not session.is_run:  # Это нужно для прекращения функции и корректного закрытия программы
            break
        if event.type == VkBotEventType.MESSAGE_NEW:
            with open('session_data.json') as file:
                confidants = json.load(file)["confidants"]
            if event.obj.message['from_id'] in confidants['Users'] + \
                    confidants['Administrators']:
                text = event.obj.message['text'].split()
                command, session_name, *arguments = text + ['']
                user = vk.users.get(user_id=event.obj.message['from_id'])
                if session_name == get_session_name() and command != '/slist':
                    if command in commands:
                        try:
                            if command != '/stop':
                                if commands[command]:
                                    exec('session.{}(event, True, {})'.format(
                                        command[1:], arguments))
                                else:
                                    exec('session.{}(event, {})'.format(
                                        command[1:], arguments))
                                window.listWidget.addItem(
                                    '[{}] {}: {} {}'.format(
                                        datetime.datetime.now(), ' '.join(
                                            [user[0]['first_name'],
                                             user[0]['last_name']]), command,
                                        ' '.join(arguments)))
                                window.reinit()
                            else:
                                session.stop(event, False, arguments)
                        except Exception as exc:
                            vk.messages.send(
                                user_id=event.obj.message['from_id'],
                                message="ОШИБКА: {}".format(str(exc)),
                                random_id=random.randint(0, 2 ** 64))
                            window.listWidget.addItem(
                                '[{}] {}: Попытка: {} {}, ошибка: {}'.format(
                                    datetime.datetime.now(), ' '.join(
                                        [user[0]['first_name'],
                                         user[0]['last_name']]), command,
                                    ' '.join(arguments), str(exc)))
                    else:
                        vk.messages.send(user_id=event.obj.message['from_id'],
                                         message="Не существует такой команды.",
                                         random_id=random.randint(0, 2 ** 64))
                        window.listWidget.addItem(
                            '[{}] {}: Попытка: {} {}, ошибка: несуществующая команда.'.format(
                                datetime.datetime.now(), ' '.join(
                                    [user[0]['first_name'],
                                     user[0]['last_name']]), command,
                                ' '.join(arguments)))

                elif command == '/slist':
                    session.slist(event)


if __name__ == '__main__':
    session = Session()
    app = QApplication(sys.argv)
    window = ControlPanel()
    window.show()
    t = MainThread(window)
    t.start()
    sys.exit(app.exec_())
