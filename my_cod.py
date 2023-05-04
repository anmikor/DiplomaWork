import vk_api
from config import user_token
from vk_api.exceptions import ApiError
import datetime


class VkTools:
    def __init__(self, token):
        self.ext_api = vk_api.VkApi(token=token)

    def get_profile_info(self, user_id):

        try:
            inform = self.ext_api.method('users.get',
                                         {'user_id': user_id,
                                          'fields': 'bdate,city,sex'})
        except ApiError:
            return

        return inform

    def find_users(self, params, offset=None):
        """
        :param params: список из 4 параметров
        :param offset: параметр, смещающий область поиска вправо
        :return: словарь с общими данными, имя, фамилия, id
        """
        #  params = [town, city_id, sex, age_from, age_to]
        try:
            profiles = self.ext_api.method('users.search',
                                           {'town': params[0],
                                            'city_id': params[1],
                                            'sex': params[2],
                                            'age_from': params[3],
                                            'age_to': params[4],
                                            'status': 1,
                                            'has_photo': 1,
                                            'count': 30,
                                            'offset': offset
                                            })

        except ApiError:
            return

        profiles = profiles['items']

        result = []
        for profile in profiles:
            if profile['is_closed']:
                continue

            result.append({'name': f'{profile["first_name"]} {profile["last_name"]}',
                           'id': profile['id']})

        return result

    def find_city_id(self, q: str):
        city_obj = self.ext_api.method('database.getCities',
                                       {'country_id': 1,
                                        'q': q,
                                        'count': 1
                                        })
        city_id = city_obj['items'][0]['id']
        return city_id

    def find_photos(self, user_id):
        photos_dict = self.ext_api.method('photos.get',
                                          {'album_id': 'profile',
                                           'owner_id': user_id,
                                           'extended': 1,
                                           })
        try:
            photos_list = photos_dict['items']
        except KeyError:
            return

        result = []
        photos_list.sort(key=lambda k: k['likes']['count'])
        for photo in photos_list:
            result.append({'owner_id': photo['owner_id'],
                           'id': photo['id']})
        best_result = result[-3:]

        return best_result


def gend(client):
    pair_sex = 1
    if client['sex'] == 1:
        pair_sex = 2
    else:
        pass
    return pair_sex


def search_params(client):
    """
    :param client: parameter list for search with function find_users() from client profile
    :return: calculated result
    """
    s_param = []
    if "city" in client:
        town = client["city"]["title"]
        s_param.append(f'{town}')
        city_id = client["city"]["id"]
        s_param.append(city_id)

    else:
        s_param.append(0)
        s_param.append(0)
    sex = gend(client)
    s_param.append(sex)
    b_year = client['bdate'].split('.')[-1]
    if len(b_year) != 4:
        s_param.append(0)
        s_param.append(0)
    else:
        b_year = int(b_year)
        age = datetime.date.today().year - b_year
        if gend(client) == 2:
            age_from = age
            age_to = age + 10
        else:
            age_from = age - 10
            if age_from < 18:
                age_from = 18
            age_to = age

        s_param.append(age_from)
        s_param.append(age_to)
    return s_param


if __name__ == '__main__':
    tools = VkTools(user_token)

    info = tools.get_profile_info(876657138)
    if info:
        print(info)
    param = search_params(info[0])
    print(param)
    found_profiles = tools.find_users(param)
    print(found_profiles, len(found_profiles))
