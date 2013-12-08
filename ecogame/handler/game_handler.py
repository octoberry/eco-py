from functools import wraps
from tornado import web, gen
from tornado.escape import json_decode
from tornado.web import HTTPError
from ecogame.handler.common_handler import AuthCommonHandler, SocketHandler


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


class GameHandler(SocketHandler):
    @gen.coroutine
    def open(self):
        yield super().open()
        self.send_json('users.me', self.user)

    @gen.coroutine
    def on_message(self, message):
        message = json_decode(message)
        if 'type' in message:
            data = message['data'] if 'data' in message else None
            if message['type'] == 'robots.find':
                robots = yield self.loader.robot_manager.find_visible()
                self.send_json('robots', robots)
            elif message['type'] == 'robots.move':
                robot = yield self.user.get_robot(data['id'])
                yield robot.move(lat=data['cords']['lat'], lng=data['cords']['lng'])
                self.send_json_all('robots.move', robot)
            elif message['type'] == 'pollution.find':
                pollutions = yield self.loader.pollution_manager.find()
                self.send_json('pollutions', pollutions)
            elif message['type'] == 'boom.boom':
                yield self.boom_boom(data=data)

    @gen.coroutine
    def boom_boom(self, data):
        if self.user.balance <= 0:
            self.send_notice_json(msg='Недостаточно кристалов. Приглашайте друзей и выполняйте задания!')
        else:
            pollutions = yield self.user.boom(data['cords']['lat'], data['cords']['lng'])
            self.send_json('boom', {'balance': self.user.balance, 'count': len(pollutions)})
            self.send_json_all('pollution.remove', {'balance': self.user.balance, 'items': pollutions.as_ids_view()})
