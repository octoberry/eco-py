from tornado import web, gen
from tornado.web import HTTPError
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


class BoomHandler(AuthCommonHandler):
    @web.authenticated
    @gen.coroutine
    def post(self, *args, **kwargs):
        """Удаляет загрязнений в указанных координатах"""
        try:
            lat = float(self.get_argument('lat'))
            lng = float(self.get_argument('lng'))
        except ValueError:
            raise HTTPError(400)

        if self.user.balance <= 0:
            self.send_error_json('Недостаточно кристалов. Приглашайте друзей и выполняйте задания!', {'balance': 0})
        else:
            removed_ids = yield self.user.boom(lat, lng)
            self.send_json({'balance': self.user.balance, 'items': removed_ids.as_ids_view()})
