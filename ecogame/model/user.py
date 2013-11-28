from tornado import gen
from ecogame.model.model import ModelManager, ModelObject, ModelList
from ecogame.model.social_helper import fill_zombie_from_vk


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
    def accept_quest(self, quest):
        """
        Сохраняет квест в списке активных для пользователя

        :param quest: Quest to accept
        :type quest: ecogame.model.quest.Quest
        """
        yield self._update_record({'$addToSet': {"quests_ids": quest.id}})
        self.quests_ids.append(quest.id)

    @gen.coroutine
    def update_social_token(self, social: str, token: str):
        """
        Сохраняет токен пользователя
        :param social: Название социальной сети, (например "vk")
        :param token: access token социальной сети
        """
        yield self._update_record({'$set': {"social.%s.access_token" % social: token}})

    @gen.coroutine
    def quests(self) -> ModelList:
        """Возвращает список принятых квестов"""
        quests = yield self.loader.quest_manager.find({'_id': {'$in': self.quests_ids}})
        return quests

    @gen.coroutine
    def compete_quest(self, quest):
        """
        Завершает выполнение квеста.

        Заносит выполненный квест в список выполненных.

        Убирает из списка активных.

        Обновляет баланс пользователья.
        :param quest: Quest to accept
        :type quest: ecogame.model.quest.Quest
        """
        completed = quest.as_completed()
        self.quests_ids.remove(quest.id)
        quest_updates = {'$push': {"quests_competed": completed}, '$set': {"quests_ids": self.quests_ids}}
        yield [self._update_record(quest_updates),
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

    @gen.coroutine
    def save_social_zombies(self):
        """Загружает зомби из друзей соц. сетей и сохраняет их в БД"""
        access_token = self.social['vk']['access_token']
        query_params = {'user_id': self.social['vk']['id'], 'fields': 'uid,first_name,photo_50,sex'}
        response = yield self.loader.vk.request('friends.get', query_params, access_token)
        if response['items']:
            zombies_to_create = []
            zombies_to_update = []
            friend_social_ids = [friend['id'] for friend in response['items']]
            existed_zombies = yield self.loader.zombie_manager.find_by_social('vk', friend_social_ids)
            #проеряем, есть ли зомби в списке существующих, и добавляем в список на update/создание
            for friend in response['items']:
                #итератор, что бы прервать выполнение на первом же зомби
                zombie_iterator = (zombie for zombie in existed_zombies if zombie.social['vk']['id'] == friend['id'])
                zombie_exist = next(zombie_iterator, False)
                if zombie_exist:
                    zombies_to_update.append(zombie_exist)
                else:
                    zombie = self.loader.zombie_manager.new_object()
                    zombie.users.append(self.id)
                    fill_zombie_from_vk(zombie, friend)
                    zombies_to_create.append(zombie)
            if zombies_to_create:
                yield self.loader.zombie_manager.insert_multiple(zombies_to_create)
            if zombies_to_update:
                yield self.loader.zombie_manager.attach_user(self, zombies_to_update)


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
        yield self.save(user)
        yield user.save_social_zombies()
