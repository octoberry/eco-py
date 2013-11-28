from motor import Op
from tornado import gen
from ecogame.model.model import ModelManager, ModelObject, ModelCordsMixin


class Zombie(ModelCordsMixin, ModelObject):
    """
    Создаются на базе друзей пользователя из социальных сетей.

    Видны только пользователям, у которых находится в друзьях соц. сетей.
    todo: change mixin inherit to right direction
    """

    db_collection_name = 'zombie'

    view_fields = ['name', 'cords']

    def __init__(self, loader):
        super().__init__(loader)
        self.users = []
        self.name = None
        self.social = {}


class ZombieManager(ModelManager):
    model_type = Zombie

    @gen.coroutine
    def find_by_social(self, social: str, social_ids: list) -> dict:
        """Осуществляет поиск зомби в базе по его ID в социальной сети"""
        social_key = 'social.%s.id' % social
        query = {social_key: {'$in': social_ids}}
        zombies = yield self.find(query)
        return zombies

    @gen.coroutine
    def attach_user(self, user, zombies: list):
        """
        Добавляет ко всем зомби в списке пользователя

        :param user: User for zombies
        :type user: ecogame.model.user.User
        :param zombies: list of Zombies
        :type zombies: list of Zombie
        """
        zombies_ids = []
        for zombie in zombies:
            zombies_ids.append(zombie.id)
            zombie.users.append(user.id)

        query = {'_id': {'$in': zombies_ids}}
        yield Op(self.object_db.update, query, {'$addToSet': {"users": user.id}}, multi=True)
