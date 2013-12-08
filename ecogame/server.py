# coding=utf-8
import os.path
from tornado import gen
import tornado.web
import tornado.httpserver
import tornado.ioloop
from tornado.options import parse_config_file, options, parse_command_line
import motor
import logging
from ecogame.handler import routing, SocketHandler
from ecogame import config, ui_methods
from ecogame.model import ManagerLoader


logging.basicConfig(level=logging.INFO)


class Application(tornado.web.Application):
    """
    Приложение при запуске читает конфиг по умолчанию в ``./app_config.py``
    (пример в ``app_config.py.dist``)

    Изменить путь к файлу конфигурации, можно передав параметр config::

        python server.py --config=/path/to/config.py

    Любой парамет конфигурации можно переопределить, передав его как параметр вызова::

        python server.py --debug=True

    Полный список команд запуска можно посмотреть выполнив::

        python server.py --help
    """
    def __init__(self, config_file=None, allow_console=True):
        self.server_log = logging.getLogger(__name__)
        settings = build_app_config(config_file, allow_console)

        mongo = options.group_dict('mongo')
        mongo_client = motor.MotorClient(host=mongo['mongo_host'],
                                         port=mongo['mongo_port'],
                                         connectTimeoutMS=mongo['mongo_timeout_connect'],
                                         socketTimeoutMS=mongo['mongo_timeout_socket'])
        self.db = getattr(mongo_client.open_sync(), mongo['mongo_db'])

        tornado.web.Application.__init__(self, routing, ui_methods=ui_methods, **settings)
        logging_configure()
        self.loader = ManagerLoader(self.settings, db=self.db)

    @gen.coroutine
    def pollution_spawn(self):
        """Инициирует генерацию загрязнений"""
        spawns = yield self.loader.pollution_manager.spawn()
        if spawns:
            SocketHandler.send_json_all('pollutions', spawns)


def build_app_config(config_file=None, allow_console=True):
    """
    Собирает конфиг для eco-game-server
    """
    settings = {
        'template_path': os.path.join(os.path.dirname(__file__), "templates"),
        'static_path': os.path.join(os.path.dirname(__file__), "static"),
        #"login_url": "/",
        'xsrf_cookies': True,
    }

    #parse config from file and override with console arguments
    default_config_name = config_file if config_file else 'app_config.py'
    default_config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', default_config_name))
    if allow_console:
        parse_command_line(final=False)
    config = options.config if options.config else default_config_path
    parse_config_file(config, final=False)
    if allow_console:
        parse_command_line()

    settings.update(options.group_dict('application'))
    return settings


def logging_configure():
    """
    Конфигурация логирования на основе настроек определенных в ``options``
    """
    if options.logfile is not None:
        handler = logging.FileHandler(options.logfile)
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter(options.logformat))
        logging.getLogger().addHandler(handler)

    if options.disable_console_log and len(logging.getLogger().handlers) > 1:
        logging.getLogger().removeHandler(logging.getLogger().handlers[0])


def main():
    app = Application()
    server_log = logging.getLogger(__name__)
    app.listen(int(options.port))
    tornado.ioloop.IOLoop.instance().set_blocking_signal_threshold(2, None)

    pollution_spawn = tornado.ioloop.PeriodicCallback(app.pollution_spawn, app.settings['pollution_spawn_time'])
    pollution_spawn.start()

    server_log.info('Application running on port: %d' % options.port)
    tornado.ioloop.IOLoop.instance().start()
