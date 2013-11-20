from tornado import web
import logging
import time


class CommonHandler(web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        self.handler_started = time.time()
        self._logger = None
        super(CommonHandler, self).__init__(application, request, **kwargs)

    def on_finish(self):
        self.logger.info('Handler request finished in %0.3f sec.', time.time() - self.handler_started)

    @property
    def logger(self):
        if not self._logger:
            self._logger = logging.getLogger(__name__)
            self._logger.setLevel(logging.INFO)
        return self._logger

    @property
    def db(self):
        return self.application.db

    def render(self, template, **kwargs):
        super(CommonHandler, self).render(template, **kwargs)


class AuthCommonHandler(CommonHandler):
    def __init__(self, application, request, **kwargs):
        self.user = None
        super(AuthCommonHandler, self).__init__(application, request, **kwargs)

    def get_current_user(self):
        return self.get_secure_cookie("user_id")

    def initialize(self):
        pass

    def render(self, template, **kwargs):
        # add any variables we want available to all templates
        kwargs['current_user'] = self.user
        super(AuthCommonHandler, self).render(template, **kwargs)


