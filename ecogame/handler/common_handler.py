from tornado import web, gen
import logging
import time
from ecogame.model import ManagerLoader


class CommonHandler(web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        self.handler_started = time.time()
        self._logger = None
        self._model_loader = None
        super(CommonHandler, self).__init__(application, request, **kwargs)

    def on_finish(self):
        self.logger.info('Handler request finished in %0.3f sec.', time.time() - self.handler_started)

    @property
    def model_loader(self):
        if not self._model_loader:
            self._model_loader = ManagerLoader(db=self.db)
        return self._model_loader

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
        return "5290f3c37fd7e09bba28976b"

    def initialize(self):
        pass

    @gen.coroutine
    def prepare(self):
        if self.current_user:
            self.logger.info('load user (id:%s)', self.current_user)
            user = yield self.model_loader.user_manager.get(self.current_user)
            if user:
                self.user = user
                self.logger.info('user id:%s found', self.current_user)
            else:
                self.clear_cookie("user")
                self.logger.warning('loading current user (hh_id:%s) failed, not found', self.current_user)
                raise web.HTTPError(500)
        pass

    def render(self, template, **kwargs):
        # add any variables we want available to all templates
        kwargs['current_user'] = self.user
        kwargs['xsrf'] = self.xsrf_token
        super(AuthCommonHandler, self).render(template, **kwargs)


