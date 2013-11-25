from motor import Op
from tornado import gen
from ecogame.model.model import ModelManager, ModelObject, ModelList
from ecogame.model.objects import Quest


class User(ModelObject):
    db_collection_name = 'user'

    def __init__(self, loader):
        super().__init__(loader)
        self.name = None
        self.avatar = None
        self.photo = None
        self.cords = None
        self.social = {}
        self.quests_ids = []
        self.quests_competed = []
        self.balance = 2

    @gen.coroutine
    def accept_quest(self, quest: Quest):
        """
        Сохраняет квест в списке активных для пользователя
        """
        yield self._update_record({'$addToSet': {"quests_ids": quest.id}})
        self.quests_ids.append(quest.id)

    @gen.coroutine
    def quests(self) -> ModelList:
        """Возвращает список принятых квестов"""
        quests = yield self.loader.quest_manager.find({'_id': {'$in': self.quests_ids}})
        return quests

    @gen.coroutine
    def compete_quest(self, quest: Quest):
        """
        Завершает выполнение квеста.

        Заносит выполненный квест в список выполненных.

        Убирает из списка активных.

        Обновляет баланс пользователья.
        """
        completed = quest.as_completed()
        self.quests_ids.remove(quest.id)
        yield [self._update_record({'$push': {"quests_competed": completed}}),
               self._update_record({'$set': {"quests_ids": self.quests_ids}}),
               self.inc_balance(int(quest.price))]
        self.quests_competed.append(completed)

    @gen.coroutine
    def inc_balance(self, inc: int):
        """
        Изменяет пользовательски баланс на указанное значение
        """
        yield self._update_record({'$inc': {"balance": int(inc)}})
        self.balance += inc

    @gen.coroutine
    def zombies(self) -> ModelList:
        """Возвращает зомби видимых пользователю"""
        zombies = yield self.loader.zombie_manager.find({'users': self.id})
        return zombies


class UserManager(ModelManager):
    model_type = User

    @gen.coroutine
    def find_by_social(self, social: str, social_id: str):
        """Осуществляет поиск пользователя по его ID в социальной сети"""
        social_key = 'social.%s.id' % social
        query = {social_key: social_id}
        user = yield self.find_one(query)
        return user

    @gen.coroutine
    def register(self, user: User):
        """Регистрирует пользователя"""
        #todo: генерить зомбаков после создания
        yield self.save(user)


def fill_user_from_vk(user: User, vk_data: dict):
    """Создает пользователя из данных vk.com"""
    user.social['vk'] = vk_data
    user.avatar = vk_data['photo_50']
    user.photo = vk_data['photo_200_orig']
    user.name = vk_data['first_name']
