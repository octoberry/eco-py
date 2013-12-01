from tornado import web, gen
from tornado.web import HTTPError
from ecogame.handler.common_handler import AuthCommonHandler


class QuestsHandler(AuthCommonHandler):
    @web.authenticated
    @gen.coroutine
    def get(self):
        quests = yield self.loader.quest_manager.find_for_user(self.user)
        self.send_json(quests)


class QuestAcceptHandler(AuthCommonHandler):
    @web.authenticated
    @gen.coroutine
    def post(self, quest_id):
        """Обрабатывает accept квеста пользователем в работу"""
        quest = yield self.loader.quest_manager.get(quest_id)
        if not quest:
            raise HTTPError(404)
        yield self.user.accept_quest(quest)
        self.send_json({'status': True, 'id': str(quest.id)})


class QuestCompleteHandler(AuthCommonHandler):
    @web.authenticated
    @gen.coroutine
    def post(self, quest_id):
        """Помечает квест как готовый"""
        quest = yield self.loader.quest_manager.get(quest_id)
        if not quest:
            raise HTTPError(404)
        yield self.user.compete_quest(quest)
        self.send_json({'status': True, 'id': str(quest.id)})


class QuestMyHandler(AuthCommonHandler):
    @web.authenticated
    @gen.coroutine
    def get(self):
        """Обрабатывает accept квеста пользователем в работу"""
        quests = yield self.user.quests()
        self.send_json(quests)
