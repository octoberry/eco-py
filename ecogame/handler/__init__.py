from tornado.web import StaticFileHandler
from ecogame.handler.game_handler import *
from ecogame.handler.pages_handler import *
from ecogame.handler.quest_handler import *

routing = [
    (r'/favicon.ico', StaticFileHandler),
    (r'/game', GameDashboardHandler),
    (r'/quests', QuestsHandler),
    (r'/quest/([a-z0-9]+)/accept', QuestAcceptHandler),
    (r'/status', StatusHandler),
    (r'/', LandingPageHandler),
]
