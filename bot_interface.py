from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from bd import *
from my_cod import *
from config import user_token, group_token

tools = VkTools(user_token)

engine = sq.create_engine(DSN)
Session = sessionmaker(bind=engine)
session = Session()

create_tables(engine)

session.close()


class NewData:
    def __init__(self):
        self.town = "Калуга"
        self.city_id = 66
        self.sex = 2
        self.age_from = 25
        self.age_to = 35

    def __getitem__(self, item):
        return [self.town, self.city_id, self.sex, self.age_from, self.age_to]

    def __str__(self):
        return (f'Город: {self.town}| '
                f'Id города: {self.city_id}| '
                f'Пол: {self.sex}| '
                f'Возраст от: {self.age_from}| '
                f'Возраст до: {self.age_to}')


class BotInterface:

    def __init__(self, token):
        self.bot = vk_api.VkApi(token=token)

    def message_send(self, user_id, message=None, attachment=None):
        """
        :rtype: messages sender
        :message: text message
        :attachment: media files (photo files)
        """
        self.bot.method('messages.send',
                        {'user_id': user_id,
                         'message': message,
                         'random_id': get_random_id(),
                         'attachment': attachment
                         }
                        )

    def handler(self):

        longpull = VkLongPoll(self.bot)
        for event in longpull.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                msg_to_me = event.text.lower()
                peer_id = event.user_id
                client = tools.get_profile_info(peer_id)[0]
                print(client)

                start_data = search_params(client)  # 'Получение анкетных данных для поиск в список len=5'
                self_user_data.sex = start_data[2]

                if msg_to_me == 'привет':
                    self.message_send(peer_id, f'Привет, {client["first_name"]}')
                    if self_user_data.town == 0:
                        self.message_send(peer_id, f'{client["first_name"]}, для поиска недостаточно данных.\n'
                                                   f'Введите, пожалуйста город для поиска\n'
                                                   f'В формате: г Иваново')

                    elif self_user_data.age_from == 0:
                        self.message_send(peer_id, f'{client["first_name"]}, для поиска не хватает данных.\n'
                                                   f'Введите, пожалуйста интервал возраста для поиска\n'
                                                   f'В формате: 22-33')
                    else:
                        self.message_send(peer_id, f'Теперь чтобы искать по вашим '
                                                   f'анкетным данным, введите: поиск \n'
                                                   f'А если нужно уточнить город или возраст для поиска,\n'
                                                   f'введите вначале город в формате: г Москва\n'
                                                   f'Потом возраст в формате 28-32\n'
                                                   f'а затем команду: далее')
                    """  Ввод города  """
                elif (msg_to_me.split(' '))[0] == 'г':
                    town = msg_to_me.split(' ')[1].capitalize()
                    new_city_id = tools.find_city_id(f'{town}')
                    self_user_data.town = town
                    self_user_data.city_id = new_city_id
                    print(self_user_data)

                    self.message_send(peer_id, f'Теперь требуется ввести интервал возраста\n'
                                               f'в формате: 25-30')

                    """  Ввод интервала возраста   """

                elif ''.join(msg_to_me.split('-')).isdigit() and len(msg_to_me) == 5:
                    addition = msg_to_me.split('-')
                    self_user_data.age_from = addition[0]
                    self_user_data.age_to = addition[1]
                    print(self_user_data)
                    print(addition)

                    self.message_send(peer_id, f'Теперь введите  команду: далее')

                elif msg_to_me == 'поиск':
                    self_user_data.town = start_data[0]
                    self_user_data.city_id = start_data[1]
                    self_user_data.age_from = start_data[3]
                    self_user_data.age_to = start_data[4]

                    if self_user_data.town == 0 or self_user_data.age_from == 0:

                        self.message_send(peer_id, f'Для поиска недостаточно данных.\n'
                                                   f'--Город:                      {self_user_data.town},\n'
                                                   f'--id города                   {self_user_data.city_id}\n'
                                                   f'--Пол (1-жен., 2-муж.):       {self_user_data.sex}\n'
                                                   f'--Минимальный возраст:        {self_user_data.age_from}\n'
                                                   f'--Максимальный возраст:       {self_user_data.age_to}.')

                    else:
                        self.sender(peer_id, start_data)
                    self.message_send(peer_id, f'Если этих результатов недостаточно, '
                                               f'снова введите: поиск \n'
                                               f'Чтобы остановить поиск, напишите: стоп\n'
                                               f'1. Надо изменить город поиска: г Калуга\n'
                                               f'2. Ввести интервал возраста, например: 28-32\n'
                                               f'3. После этого введите команду: далее')

                elif msg_to_me == 'далее':

                    self.message_send(peer_id,   f'--Город:                      {self_user_data.town},\n'
                                                 f'--id города                   {self_user_data.city_id}\n'
                                                 f'--Пол (1-жен., 2-муж.):       {self_user_data.sex}\n'
                                                 f'--Минимальный возраст:        {self_user_data.age_from}\n'
                                                 f'--Максимальный возраст:       {self_user_data.age_to}.')

                    self.sender(peer_id, self_user_data)

                    self.message_send(peer_id, f'Доступные команды: поиск, далее, стоп\n'
                                               f'Изменение данных поиска в комментарии '
                                               f'к команде: привет')

                elif msg_to_me == 'стоп':
                    break
                else:
                    self.message_send(peer_id, 'Напишите привет, чтобы получить информацию')

    def sender(self, peer_id, data):
        print(data)
        profiles_list = tools.find_users(data)
        for profile in profiles_list:
            info_db = extract_from_db(session, profile['id'])
            if info_db == 1:
                continue
            else:
                add_to_table(session, profile_id=peer_id, account_id=profile['id'])

            photos = tools.find_photos(profile['id'])
            self.message_send(peer_id, f'Ссылка на аккаунт: {profile["name"]}'
                                       f' https://vk.com/id{profile["id"]} '
                                       f'город {data[0][0]}')

            for num, photo in enumerate(photos):
                attachment = f'photo{photo["owner_id"]}_{photo["id"]}'
                self.message_send(peer_id, f'Фото номер {num + 1} ', attachment)
            break


if __name__ == '__main__':
    engine = sq.create_engine(DSN)
    Session = sessionmaker(bind=engine)
    session = Session()

    self_user_data = NewData()
    bot = BotInterface(group_token)
    tools = VkTools(user_token)

    bot.handler()
    session.close()
