import random
import vk_api
import json

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from texts import *
from config import *
from keyboards import *
from models import *


def write_message(chat_id, message):  # Функция написания сообщения
    vk_session.method('messages.send', {
                      'chat_id': chat_id, 'message': message, 'random_id': 0})


# Функция написания сообщения с клавиатурой
def write_message_with_keyboard(chat_id, message, keyboard):
    vk_session.method('messages.send', {
                      'chat_id': chat_id, 'message': message, 'random_id': 0, 'keyboard': keyboard})


def command_problem(chat_id):  # Функция вывода сообщения о некорректном написании команды
    vk_session.method('messages.send', {
                      'chat_id': chat_id, 'message': problem_text, 'random_id': 0})


def user_registration(user_id):  # Функция регистрации игрока
    mess_text = received_message.replace('/рег ', '')

    if mess_text.find(' ') > 0:  # Если команда написана почти корректно
        # Получение данных из сообщения
        game_name = mess_text[:mess_text.find(' ') + 1]

        mess_text = received_message.replace(' ', '')
        mess_text = received_message.replace(game_name, '')

        game_code = mess_text[mess_text.find(' '):]
        game_code = ''.join([val for val in game_code if val.isnumeric()])
        game_code = game_code.replace(game_name, '')
        game_code = int(game_code)

        user = PogoUser.get_or_none(user_id=user_id)
        user_with_game_code = PogoUser.get_or_none(game_code=game_code)

        # Корректное написнаие команды
        if game_name != '' and 1000000000000000 < game_code < 9999999999999999:
            # Существование игрового кода в БД
            if user_with_game_code is not None and user is None:
                write_message(
                    chat_id, 'Игрок с таким игровым кодом уже существует! Введите другие данные!')
            # Обновление информации игрока
            elif user is not None:
                update_user(user, game_name, game_code)
                write_message(
                    chat_id, f'@id{user_id}({user_full_name}), ваша информация обновлена упешно!')
            # Регистрация игрока
            elif user is None:
                create_user(user_id=user_id, game_name=game_name,
                            game_code=game_code)
                write_message(
                    chat_id, f'@id{user_id}({user_full_name}), вы успешно зарегистрированы!')
        else:  # Некорректное написание команды
            write_message(
                chat_id, f'@id{user_id}({user_full_name}), Команда написана некорректно!\nПример использования: /рег hellopogo 1111 2222 3333 4444\nЕще пример использования: /рег hellopogo 1111222233334444')

    else:  # Некорректное написание команды
        write_message(
            chat_id, f'@id{user_id}({user_full_name}), Команда написана некорректно!\nПример использования: /рег hellopogo 1111 2222 3333 4444\nЕще пример использования: /рег hellopogo 1111222233334444')


def get_user_info(user_id):  # Функция получения информации об игроке
    user = PogoUser.get_or_none(user_id=user_id)
    if user is None:
        write_message(
            chat_id, f'@id{user_id}({user_full_name})' + unregistred_user_text)
    else:
        write_message(
            chat_id, f'@id{user_id}({user_full_name})\nНик: {user.game_name}\nКод: {user.game_code}')


# Функция удаления данных игрока
def user_data_delete(chat_id, user_id, user_full_name):
    delete_all_user_data(user_id)
    write_message(
        chat_id, f'@id{user_id}({user_full_name}),ваши данные успешно удалены!')


def question(chat_id):  # Функция-шутка для вопроса
    rand_list = ['Доктор стоун', 'Михаилыч', 'ФедораП', 'Грач']
    rand_text = random.choice(rand_list)
    write_message(chat_id, rand_text)


def create_raid(chat_id, text_list, user_id, user_full_name, game_name, game_code):  # Функция создания рейда
    pokemon_name = text_list[1]
    max_participants = text_list[2]

    if 1 < int(max_participants) < 7:
        create_info_raid(
            organizer_id=user_id,
            participant_id=user_id,
            pokemon_name=pokemon_name,
            max_participants=max_participants,
        )

        print(user_full_name, 'Создал рейд')

        message = f'''@all
    Объявлен сбор на рейд: {pokemon_name}
    Создатель рейда: @id{user_id}({user_full_name})
    Ник и код в игре: {game_name} ({game_code})
    В лобби: 1 ({max_participants})'''

        write_message_with_keyboard(
            chat_id, message, keyboard_raid.get_keyboard())
    else:
        write_message(
            chat_id, 'Максимальное количество участников не может быть меньше 2 и больше 6!')


# Функция получения списка участников рейда
def get_raid_members(organizer_id):
    # Получение списка словрей участников рейда
    members_in_raid = []
    for member in PogoUser.select(PogoUser.user_id, PogoUser.game_code, PogoUser.game_name).join(PogoRaid, on=(PogoUser.user_id == PogoRaid.participant_id)).where(PogoRaid.organizer_id == organizer_id):
        members_in_raid.append({
            'participant_id': member.user_id,
            'game_name': member.game_name,
            'game_code': member.game_code,
        })

    # Перевод полученного списка словарей участников рейда в формат строки
    str_members_in_raid = ''
    for member in members_in_raid:
        str_members_in_raid += str(member['game_name']) + \
            '(' + str(member['game_code']) + ')\n'

    return str_members_in_raid


# Функция присоединения к рейду
def raid_join(user_id, user_full_name, organizer_id, max_participants):
    user = PogoUser.get_or_none(user_id=user_id)
    user_in_raid = PogoRaid.get_or_none(participant_id=user_id)
    oraganizer_in_raid = PogoRaid.get_or_none(organizer_id=organizer_id)

    organizer = vk_session.method("users.get", {"user_ids": organizer_id})
    organizer_full_name = organizer[0]['first_name'] + \
        ' ' + organizer[0]['last_name']

    if user is None:  # Незарегистрированный игрок
        write_message(
            3, f'@id{user_id}({user_full_name})' + unregistred_user_text)
    elif oraganizer_in_raid is None:
        write_message(3, 'Этот рейд уже сформирован!')
    elif user_in_raid is not None:  # Игрок уже состоит в рейде
        write_message(3, 'Вы уже состоите в рейде!')
    # Присоединение к рейду
    elif PogoRaid.select().where(PogoRaid.organizer_id == organizer_id).count() < int(max_participants):
        pokemon_name = PogoRaid.get(organizer_id=organizer_id)
        pokemon_name = pokemon_name.pokemon_name
        write_message(3, f'@id{user_id}({user_full_name}) &#9989;Вход')
        create_info_raid(
            organizer_id=organizer_id,
            participant_id=user_id,
            pokemon_name=pokemon_name,
            max_participants=max_participants,
        )

        # Рейд полностью сформирован
        if PogoRaid.select().where(PogoRaid.organizer_id == organizer_id).count() < int(max_participants):
            # Получение участников рейда
            str_members_in_raid = get_raid_members(organizer_id)
            pokemon_name = PogoRaid.get(organizer_id=organizer_id)
            pokemon_name = pokemon_name.pokemon_name
            write_message_with_keyboard(
                3, f'Продолжается набор на рейд: {pokemon_name}\nСоздатель рейда: @id{organizer_id}({organizer_full_name})\nИгроки в лобби:\n{str_members_in_raid}', keyboard_raid.get_keyboard())
        else:
            str_members_in_raid = get_raid_members(organizer_id)
            pokemon_name = PogoRaid.get(organizer_id=organizer_id)
            pokemon_name = pokemon_name.pokemon_name
            write_message(
                3, f'@id{organizer_id}({organizer_full_name}), рейд на {pokemon_name} полностью сформирован!\nИгроки, ожидающие рейда:\n\n{str_members_in_raid}')
            raid_all_members_delete(organizer_id)


def raid_leave(user_id, user_full_name, organizer_id, max_participants):  # Функция выхода из рейда
    user = PogoUser.get_or_none(user_id=user_id)
    user_is_organizer_or_not = PogoRaid.get_or_none(organizer_id=user_id)
    oraganizer_in_raid = PogoRaid.get_or_none(organizer_id=organizer_id)
    user_in_raid = PogoRaid.get_or_none(
        organizer_id=organizer_id, participant_id=user_id)

    organizer = vk_session.method("users.get", {"user_ids": organizer_id})
    organizer_full_name = organizer[0]['first_name'] + \
        ' ' + organizer[0]['last_name']

    str_members_in_raid = get_raid_members(organizer_id)

    if user is None:  # Незарегистрированный игрок
        write_message(
            3, f'@id{user_id}({user_full_name})' + unregistred_user_text)
    elif oraganizer_in_raid is None:
        write_message(3, 'Этот рейд уже сформирован!')
    elif user_is_organizer_or_not is not None:  # Выход из рейда его организатора
        pokemon_name = PogoRaid.get(organizer_id=organizer_id)
        pokemon_name = pokemon_name.pokemon_name
        write_message(
            3, f'@id{organizer_id}({organizer_full_name}), рейд на {pokemon_name} полностью сформирован!\nИгроки, ожидающие рейда:\n{str_members_in_raid}')
        raid_all_members_delete(organizer_id)
    elif user_in_raid is not None:  # Выход участника рейда из него
        raid_member_delete(user_id)
        str_members_in_raid = get_raid_members(organizer_id)
        pokemon_name = PogoRaid.get(organizer_id=organizer_id)
        pokemon_name = pokemon_name.pokemon_name
        write_message_with_keyboard(
            3, f'@id{user_id}({user_full_name}) покинул(а) лобби ожидания на рейд: {pokemon_name}\nСоздатель рейда: @id{organizer_id}({organizer_full_name})\nОставшиеся игроки в лобби:\n{str_members_in_raid}', keyboard_raid.get_keyboard())
    else:  # Игрок не состоит в рейде
        write_message(
            3, f'@id{user_id}({user_full_name}), вы не состоите в этом рейде чтобы его покидать!')


# Авторизация бота
vk_session = vk_api.VkApi(token=BOT_TOKEN)

# Работа с сообщениями
longpoll = VkBotLongPoll(vk_session, group_id=203487075)

print("Server started")

# Основной цикл
for event in longpoll.listen():

    # Если пришло новое сообщение
    if event.type == VkBotEventType.MESSAGE_NEW and event.from_chat and event.message.get('text') != '':

        # получение данных из сообщения
        received_message = event.message.get('text')
        chat_id = event.chat_id
        user_id = event.message.from_id
        user = vk_session.method("users.get", {"user_ids": user_id})
        user_full_name = user[0]['first_name'] + ' ' + user[0]['last_name']

        # Команда ПОМОЩЬ
        if received_message == '/помощь':
            write_message(event.chat_id, help_text)

        # Команда РЕГистрации игрока
        elif received_message.startswith('/рег '):
            user_registration(user_id)

        # Команда УДАЛИТЬ МОИ ДАННЫЕ для удаления данных игрока
        elif received_message == '/удалить мои данные':
            user_data_delete(chat_id, user_id, user_full_name)

        # Команда вывода информации О СЕБЕ
        elif received_message == '/о себе':
            get_user_info(user_id)

        # Команда-шутка ВОПРОС
        elif received_message.startswith('/вопрос '):
            question(chat_id)

        # Команда создания РЕЙДа
        elif received_message.startswith('/рейд '):
            # Проверка существования игрока и организатора в каких-либо рейдах
            user = PogoUser.get_or_none(user_id=user_id)
            raid_user = PogoRaid.get_or_none(organizer_id=user_id)
            text_list = received_message.split(' ')

            if user is None:  # Незарегистрированный игрок
                write_message(
                    chat_id, f'@id{user_id}({user_full_name})' + unregistred_user_text)
            elif len(text_list) != 3:  # Команда написана некорректно
                command_problem(chat_id)
            elif raid_user is not None:  # Игрок уже состоит в каком-либо рейде
                write_message(chat_id, existing_user_text)
            else:  # Вызов функции создания рейда
                create_raid(chat_id, text_list, user_id,
                            user_full_name, user.game_name, user.game_code)

    # Обработка нажатий на кнопки
    elif event.type == VkBotEventType.MESSAGE_EVENT:
        # получение данных из сообщения
        user_id = event.object.user_id
        user = vk_session.method("users.get", {"user_ids": user_id})
        user_full_name = user[0]['first_name'] + ' ' + user[0]['last_name']

        # Получение текста сообщения, где была нажата кнопка
        message_ids = event.object.conversation_message_id
        raid_message = vk_session.method(
            "messages.getByConversationMessageId", {"peer_id": 2000000003, "conversation_message_ids": message_ids})
        raid_message = raid_message["items"][0]["text"]

        # Получение организатора рейда
        organizer_id_text = raid_message[raid_message.find(
            'Создатель рейда: [id') + 20:raid_message.find('Создатель рейда: [id') + 30]
        organizer_id = ''.join(
            [val for val in organizer_id_text if val.isnumeric()])

        # Получение имени рейдового покемона
        pokemon_name = raid_message[32:raid_message.find('С') - 1]

        # Получение максимального количества человек в рейде
        max_participants = raid_message[-2]

        # Вызов функции присоединения к рейду
        if event.object.payload['type'] == 'Callback_raid_join':
            raid_join(user_id, user_full_name, organizer_id, max_participants)

        # Вызов функции выхода из рейда
        elif event.object.payload['type'] == 'Callback_raid_leave':
            raid_leave(user_id, user_full_name, organizer_id, max_participants)
