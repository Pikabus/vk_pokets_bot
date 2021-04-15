from peewee import *

# Подключение к БД
conn = SqliteDatabase('vkPokeBot.sqlite3')

# Создание курсора
cursor = conn.cursor()


class BaseModel(Model):  # Базовая модель для наследования
    class Meta:
        database = conn


class PogoUser(BaseModel):  # Модель игрока
    user_id = IntegerField(
        null=False, column_name='VkUserId', unique=True)
    game_name = TextField(null=False, column_name='UserGameName', unique=True)
    game_code = BigIntegerField(
        null=False, column_name='UserGameCode', unique=True)

    class Meta:
        table_name = 'PogoUser'


# Модель рейда
class PogoRaid(BaseModel):
    organizer_id = IntegerField(null=False, column_name='VkOrganizerId')
    participant_id = ForeignKeyField(
        PogoUser, related_name='VkParticipantId')
    pokemon_name = TextField(null=False, column_name='PokemonName')
    max_participants = IntegerField(null=False, column_name='MaxParticipants')

    class Meta:
        table_name = 'PogoRaid'


def create_user(user_id, game_name, game_code):  # Регистрация игрока
    row = PogoUser(
        user_id=user_id,
        game_name=game_name,
        game_code=game_code,
    )
    row.save()


def update_user(user, game_name, game_code):  # Обновление данных игрока
    user.game_name = game_name
    user.game_code = game_code
    user.save()


# Присоединение к рейду
def create_info_raid(organizer_id, participant_id, pokemon_name, max_participants):
    row = PogoRaid(
        organizer_id=organizer_id,
        participant_id=participant_id,
        pokemon_name=pokemon_name,
        max_participants=max_participants,
    )
    row.save()


def raid_member_delete(user_id):  # Удаление игрока из рейда
    user = PogoRaid.get(participant_id=user_id)
    user.delete_instance()


# Удаление всех строк из-за полностью сформированнного рейда
def raid_all_members_delete(organizer_id):
    PogoRaid.delete().where(PogoRaid.organizer_id == organizer_id).execute()


def delete_all_user_data(user_id):  # Удаление всех данных игрока
    user = PogoUser.get(user_id=user_id)
    user.delete_instance()


# Закрывем соединение с БД
conn.close()
