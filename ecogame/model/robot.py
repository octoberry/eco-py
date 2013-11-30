from motor import Op, MotorDatabase
from tornado import gen
from ecogame.model.model import ModelManager, ModelObject, ModelCordsMixin, ManagerCordsMixin, ModelList


class Robot(ModelCordsMixin, ModelObject):
    db_collection_name = 'robot'

    view_fields = ['cords', 'user']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.placed = False


class RobotManager(ManagerCordsMixin, ModelManager):
    model_type = Robot

    @gen.coroutine
    def find_visible(self) -> ModelList:
        """
        Возвращает список всех роботов
        """
        robots = yield self.find({'placed': True})
        return robots
