import time
from ecogame.model.model import ModelManager, ModelObject, ModelCordsMixin


QuestTypes = {
    1: "Вторая жизнь вещей",
    2: "Раздельный сбор",
    3: "Групповое задание",
    4: "Экономия электроэнергии"
}


class Quest(ModelObject):
    """
    Объект описывающий квест.

    В награду за выполнение квеста игрок получает эко-кристалы
    """
    db_collection_name = 'quest'

    view_fields = ['title', 'type', 'price', 'short_desc', 'desc']

    def __init__(self, loader):
        super().__init__(loader)
        self.title = ''
        self.type = 0
        self.short_desc = ''
        self.desc = ''
        self.price = 1

    def as_completed(self) -> dict:
        """
        Возвращает объект выполненого квеста с указанием названия, цены и времени выполнения
        """
        return {
            "id": self.id,
            "title": self.title,
            "type": self.type,
            "price": self.price,
            "finished_at": time.time()
        }


class QuestManager(ModelManager):
    model_type = Quest


class Pollution(ModelObject):
    """
    Загрязнение.

    Точка на карте с загрязнением
    """
    db_collection_name = 'pollution'

    def __init__(self, loader):
        super().__init__(loader)
        self.cords = None


class PollutionManager(ModelManager):
    model_type = Pollution


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
        self.social = None


class ZombieManager(ModelManager):
    model_type = Zombie


class Robot(ModelObject):
    db_collection_name = 'robot'

    def __init__(self, loader):
        super().__init__(loader)
        self.user = None


class RobotManager(ModelManager):
    model_type = Quest
