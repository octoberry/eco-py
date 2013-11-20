from tornado.web import StaticFileHandler
from ecogame.handler.pages_handler import *

handlers = [
    (r'/favicon.ico', StaticFileHandler),
    #(r'/dashboard', hanler_path),
    (r'/status', StatusHandler),
    (r'/', LandingPageHandler),
]
