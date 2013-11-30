from functools import wraps
from tornado import web, gen
from tornado.web import HTTPError
from ecogame.handler.common_handler import AuthCommonHandler


def require_cords(method):
    """
    Allow AJAX requests only

    Usage:
       @require_ajax
       def my_view(request):
           pass
    """

    @wraps(method)
    def wrapper(handler, *args, **kwargs):
        try:
            lat = float(handler.get_argument('lat'))
            lng = float(handler.get_argument('lng'))
        except ValueError:
            raise HTTPError(400)
        kwargs['lat'] = round(lat, 6)
        kwargs['lng'] = round(lng, 6)
        return method(handler, *args, **kwargs)
    return wrapper


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


class RobotHandler(AuthCommonHandler):
    @web.authenticated
    @gen.coroutine
    def get(self):
        """Возвращает загрязнения"""
        robots = yield self.loader.robot_manager.find_visible()
        self.send_json(robots)


class RobotMoveHandler(AuthCommonHandler):
    @web.authenticated
    @gen.coroutine
    @require_cords
    def post(self, robot_id, lat, lng, *args, **kwargs):
        """Перемещает робота на указанные координаты"""
        robot = yield self.user.get_robot(robot_id)
        robot.move(lat, lng)
        self.send_json({'result': True})


class BoomHandler(AuthCommonHandler):
    @web.authenticated
    @gen.coroutine
    @require_cords
    def post(self, lat, lng, *args, **kwargs):
        """Удаляет загрязнений в указанных координатах"""
        if self.user.balance <= 0:
            self.send_error_json('Недостаточно кристалов. Приглашайте друзей и выполняйте задания!', {'balance': 0})
        else:
            removed_ids = yield self.user.boom(lat, lng)
            self.send_json({'balance': self.user.balance, 'items': removed_ids.as_ids_view()})
