# coding=utf-8
from tornado.options import define
import collections


#MONGO CONFIG
define("mongo_db", 'ecodev', str, "MongoDB DB name", group='mongo')
define("mongo_host", 'localhost', str, "MongoDB host", group='mongo')
define("mongo_port", 27017, int, "MongoDB port", group='mongo')
define("mongo_timeout_connect", 10000, int, "MongoDB connection timeout", group='mongo')
define("mongo_timeout_socket", 500, int, "MongoDB socket timeout", group='mongo')

#COMMON APP SETTINGS
define("config", type=str, help="path to config file")
define("debug", default=False, help="Debug mode", group='application')
define("cookie_secret", help="Cookie secret code", group='application')
define("port", 8001, int, "Server port listen")
define("static_url", '/static', str, "Static files url path", group='application')

#POLLUTION
define("pollution_spawn_time", 1000 * 10, int, "Pollution spawn cycle", group='application')
define("pollution_spawn_rtg", 0.01, int, "Pollution per zombie", group='application')
define("pollution_boom_radius", 50, int, "Pollution boom radius (meters)", group='application')

#LOGGING
define('suppressed_loggers', ['tornado.curl_httpclient'], list)
define('logformat', '[%(process)s] %(asctime)s %(levelname)s %(name)s: %(message)s', str)
define('logfile', None, str, 'Path to log file')
define('disable_console_log', False, bool, 'Disable console log (if any other log handler available)')

#VK.COM
define('vk_client_id', None, str, 'vk client id', group='application')
define('vk_client_secret', None, str, 'vk client secret', group='application')
