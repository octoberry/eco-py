import random


def random_moscow_cords():
    """Случайные координаты в Москве"""
    lng = random.randint(0, 100000)
    lat = random.randint(0, 100000)
    return dict(lng=(37.605+lng/1000000), lat=(55.701+lat/1000000))


def fill_zombie_from_vk(zombie, vk_data: dict):
    """Создает пользователя из данных vk.com"""
    zombie.social['vk'] = vk_data
    zombie.photo = vk_data['photo_50']
    zombie.name = vk_data['first_name']
    zombie.cords = random_moscow_cords()


def fill_user_from_vk(user, vk_data: dict):
    """Создает пользователя из данных vk.com"""
    user.social['vk'] = vk_data
    user.avatar = vk_data['photo_50']
    user.photo = vk_data['photo_200_orig']
    user.name = vk_data['first_name']
