import datetime
from motor import Op
from tornado import gen
from ecogame.model.model import ModelManager, ModelObject

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
            "finished_at": datetime.datetime.utcnow()
        }


class QuestManager(ModelManager):
    model_type = Quest
