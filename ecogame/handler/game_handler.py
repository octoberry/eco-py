from tornado import web, gen
from ecogame.handler.common_handler import AuthCommonHandler


class GameDashboardHandler(AuthCommonHandler):
    @web.authenticated
    def get(self):
        self.render('game.html')


class ZombiesHandler(AuthCommonHandler):
    @web.authenticated
    @gen.coroutine
    def get(self):
        """Возвращает зомби доступных пользователю"""
        zombies = yield self.user.zombies()
        self.send_json(zombies)


class PollutionHandler(AuthCommonHandler):
    @web.authenticated
    @gen.coroutine
    def get(self):
        """Возвращает загрязнения"""
        pollutions = yield self.loader.pollution_manager.find()
        self.send_json(pollutions)
