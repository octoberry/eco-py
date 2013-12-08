from motor import Op
from tornado import gen
from ecogame.model.model import ModelManager, ModelObject, ModelCordsMixin, ManagerCordsMixin
from ecogame.model.social_helper import random_moscow_cords
from bson import ObjectId

class Pollution(ModelCordsMixin, ModelObject):
    """
    Точка на карте с загрязнением.
    """
    db_collection_name = 'pollution'

    view_fields = ['cords']

    def __init__(self, loader):
        super().__init__(loader)


class PollutionManager(ManagerCordsMixin, ModelManager):
    model_type = Pollution

    @gen.coroutine
    def spawn(self):
        """
        Генерит загрязенения исходя из кол-ва зомби и настроек
        :return list of ObjectId
        :rtype list[Pollution]
        """
        pollutions_count = yield self.count()
        if pollutions_count >= self.loader.settings['pollution_max_count']:
            return None
        zombies_count = yield self.loader.zombie_manager.count()
        pollutions_to_generate = round(zombies_count * self.loader.settings['pollution_spawn_rtg'])
        pollutions_to_create = []
        for i in range(0, pollutions_to_generate):
            pollution = self.new_object()
            pollution.cords = random_moscow_cords()
            pollutions_to_create.append(pollution)
        if pollutions_to_create:
            result = yield self.loader.pollution_manager.insert_multiple(pollutions_to_create)
            if result:
                spawns = yield self.gets(result)
                return spawns
        return None
