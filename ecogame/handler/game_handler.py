from tornado.escape import json_encode
from tornado import web, gen
from ecogame.handler.common_handler import AuthCommonHandler


class GameDashboardHandler(AuthCommonHandler):
    @web.authenticated
    def get(self):
        self.render('game.html')
