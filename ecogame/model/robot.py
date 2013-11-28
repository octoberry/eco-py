from motor import Op
from tornado import gen
from ecogame.model.model import ModelManager, ModelObject, ModelCordsMixin

class Robot(ModelObject):
    db_collection_name = 'robot'

    def __init__(self, loader):
        super().__init__(loader)
        self.user = None


class RobotManager(ModelCordsMixin, ModelManager):
    model_type = Robot
