from tornado.web import StaticFileHandler

handlers = [
    (r'/favicon.ico', StaticFileHandler),
    #(r'/dashboard', hanler_path),
    #(r'/', hanler_path),
]
