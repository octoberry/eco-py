from tornado.web import StaticFileHandler
from ecogame.handler.auth_handler import *
from ecogame.handler.game_handler import *
from ecogame.handler.pages_handler import *
from ecogame.handler.quest_handler import *

routing = [
    (r'/favicon.ico', StaticFileHandler),
    (r'/static/(.*)', StaticFileHandler),
    (r'/game', GameDashboardHandler),
    (r'/quest/([a-z0-9]+)/accept', QuestAcceptHandler),
    (r'/quest/([a-z0-9]+)/complete', QuestCompleteHandler),
    (r'/quests/my', QuestMyHandler),
    (r'/quests', QuestsHandler),
    (r'/zombies', ZombiesHandler),
    (r'/pollutions', PollutionHandler),
    (r'/robots', RobotHandler),
    (r'/robot/([a-z0-9]+)/move', RobotMoveHandler),
    (r'/boom', BoomHandler),
    (r'/status', StatusHandler),
    (r'/auth/vkontakte', VKAuthHandler),
    (r'/', LandingPageHandler),
]
