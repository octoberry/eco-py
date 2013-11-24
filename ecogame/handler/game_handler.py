from tornado.escape import json_encode
from tornado import web, gen
from ecogame.handler.common_handler import AuthCommonHandler


class GameDashboardHandler(AuthCommonHandler):
    @web.authenticated
    def get(self):
        self.render('game.html')


class QuestsHandler(AuthCommonHandler):
    @web.authenticated
    @gen.coroutine
    def get(self):
        quests = yield self.model_loader.quest_manager.find()
        json_q = [quest.as_view() for quest in quests]
        self.write(json_encode(json_q))
        self.finish()
