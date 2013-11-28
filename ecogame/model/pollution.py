from motor import Op
from tornado import gen
from ecogame.model.model import ModelManager, ModelObject, ModelCordsMixin

class Pollution(ModelObject):
    """
    Загрязнение.

    Точка на карте с загрязнением
    """
    db_collection_name = 'pollution'

    def __init__(self, loader):
        super().__init__(loader)
        self.cords = None


class PollutionManager(ModelCordsMixin, ModelManager):
    model_type = Pollution
