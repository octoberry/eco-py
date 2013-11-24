from tornado.web import StaticFileHandler
from ecogame.handler.game_handler import GameDashboardHandler, QuestsHandler
from ecogame.handler.pages_handler import *

handlers = [
    (r'/favicon.ico', StaticFileHandler),
    (r'/game', GameDashboardHandler),
    (r'/quests', QuestsHandler),
    (r'/status', StatusHandler),
    (r'/', LandingPageHandler),
]
