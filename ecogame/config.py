# coding=utf-8
from tornado.options import define
import collections


#MONGO CONFIG
#define("mongoconf", 'localhost', str, "MongoDB host", group='mongo')

#COMMON APP SETTINGS
define("config", type=str, help="path to config file")
define("debug", default=False, help="Debug mode", group='application')
define("cookie_secret", help="Cookie secret code", group='application')
define("port", 8888, int, "Server port listen")
define("static_url", '/static', str, "Static files url path", group='application')

#LOGGING
define('suppressed_loggers', ['tornado.curl_httpclient'], list)
define('logformat', '[%(process)s] %(asctime)s %(levelname)s %(name)s: %(message)s', str)
define('logfile', None, str, 'Path to log file')
define('disable_console_log', False, bool, 'Disable console log (if any other log handler available)')
