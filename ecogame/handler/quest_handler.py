from tornado.escape import json_encode
from tornado import web, gen
from tornado.web import HTTPError
from ecogame.handler.common_handler import AuthCommonHandler


class QuestsHandler(AuthCommonHandler):
    @web.authenticated
    @gen.coroutine
    def get(self):
        quests = yield self.model_loader.quest_manager.find()
        json_q = [quest.as_view() for quest in quests]
        self.write(json_encode(json_q))
        self.finish()


class QuestAcceptHandler(AuthCommonHandler):
    @web.authenticated
    @gen.coroutine
    def post(self, quest_id):
        """Обрабатывает accept квеста пользователем в работу"""
        quest = yield self.model_loader.quest_manager.get(quest_id)
        if not quest:
            raise HTTPError(404)
        yield self.user.accept_quest(quest)
        self.write(json_encode({'status': True, 'id': str(quest.id)}))
        self.finish()
