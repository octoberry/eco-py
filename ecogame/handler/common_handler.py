from tornado.escape import json_encode
from ecogame.model import ManagerLoader
from tornado import web, gen
import logging
import time
from ecogame.vk import VKAPI


class CommonHandler(web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        self.handler_started = time.time()
        super(CommonHandler, self).__init__(application, request, **kwargs)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.vk_api = VKAPI(client_id=self.settings["vk_client_id"], client_secret=self.settings["vk_client_secret"])
        self.db = self.application.db
        self.model_loader = ManagerLoader(db=self.db)

    def on_finish(self):
        self.logger.info('Handler request finished in %0.3f sec.', time.time() - self.handler_started)

    def send_json(self, data):
        """Отправляет dict как json. Автоматически вызывает as_view"""
        if hasattr(data, 'as_view'):
            self.write(json_encode(data.as_view()))
        else:
            self.write(json_encode(data))
        self.finish()


class AuthCommonHandler(CommonHandler):
    def __init__(self, application, request, **kwargs):
        self.user = None
        super(AuthCommonHandler, self).__init__(application, request, **kwargs)

    def get_current_user(self):
        return self.get_secure_cookie("user").decode(encoding='UTF-8')

    def initialize(self):
        pass

    @gen.coroutine
    def prepare(self):
        if self.current_user:
            self.logger.info('load user id:%s', self.current_user)
            user = yield self.model_loader.user_manager.get(self.current_user)
            if user:
                self.user = user
                self.logger.info('user id:%s found', self.current_user)
            else:
                self.clear_cookie("user")
                self.logger.warning('loading current user id:%s failed, not found', self.current_user)
                raise web.HTTPError(500)

    def render(self, template, **kwargs):
        # add any variables we want available to all templates
        kwargs['current_user'] = self.user
        kwargs['xsrf'] = self.xsrf_token
        super(AuthCommonHandler, self).render(template, **kwargs)
