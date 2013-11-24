from tornado import gen
from ecogame.model.model import ModelManager, ModelObject
from ecogame.model.objects import Quest


class User(ModelObject):
    db_collection_name = 'user'

    def __init__(self, loader):
        super().__init__(loader)
        self.name = None
        self.cords = None
        self.social = None
        self.quests = []
        self.quests_competed = []
        self.balance = 0


    @gen.coroutine
    def accept_quest(self, quest: Quest):
        """
        Сохраняет квест в списке активных для пользователя
        """
        yield self._update_record({'$addToSet': {"quests": quest.id}})
        self.quests.append(quest.id)

    @gen.coroutine
    def compete_quest(self, quest: Quest):
        """
        Завершает выполнение квеста.

        Заносит выполненный квест в список выполненных.

        Убирает из списка активных.

        Обновляет баланс пользователья.
        """
        completed = quest.as_completed()
        self.quests.remove(quest.id)
        yield [self._update_record({'$push': {"quests_competed": completed}}),
               self._update_record({'$set': {"quests": self.quests}}),
               self.inc_balance(quest.price)]
        self.quests_competed.append(completed)

    @gen.coroutine
    def inc_balance(self, inc: int):
        """
        Изменяет пользовательски баланс на указанное значение
        """
        yield self._update_record({'$addToSet': {'$inc': {"balance": inc}}})
        self.balance += inc

    def load_from_db(self, data: dict):
        super().load_from_db(data)
        self.name = data['name']
        self.social = data['social']


class UserManager(ModelManager):
    model_type = User

