from tornado.escape import json_encode
from ecogame.model import ManagerLoader
from tornado import web, gen
import logging
import time
from tornado.httputil import url_concat

import tornado.escape
from tornado import httpclient

from urllib.parse import urlencode

class VKAPI(object):
    _OAUTH_ACCESS_TOKEN_URL = "https://api.vk.com/oauth/access_token?"
    _OAUTH_AUTHORIZE_URL = "http://api.vk.com/oauth/authorize?"
    _OAUTH_REQUEST_URL = "https://api.vk.com/method/"

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        pass

    @gen.coroutine
    def get_access_token(self, code):
        http = httpclient.AsyncHTTPClient()
        url = self._oauth_request_token_url(client_id=self.client_id,
                                            code=code,
                                            client_secret=self.client_secret,
                                            extra_params={'grant_type': 'client_credentials'})
        response = yield http.fetch(url, validate_cert=False)
        return tornado.escape.json_decode(response.body)

    @gen.coroutine
    def get_user(self, access_token, uid=0):
        args = {"uid": uid}
        args = {}
        user = yield self.request(api_method="users.get", access_token=access_token, params=args)
        return user

    def _oauth_request_token_url(self, redirect_uri=None, client_id=None,
                                 client_secret=None, code=None,
                                 extra_params=None):
        url = self._OAUTH_ACCESS_TOKEN_URL
        args = dict(
            redirect_uri=redirect_uri,
            code=code,
            client_id=client_id,
            client_secret=client_secret,
        )
        if extra_params:
            args.update(extra_params)
        return url_concat(url, args)

    @gen.coroutine
    def request(self, api_method, params, access_token):
        args = {"access_token": access_token}

        if params:
            args.update(params)
        #url = self._OAUTH_REQUEST_URL + api_method + ".json?" + urlencode(args)
        url = self._OAUTH_REQUEST_URL + api_method + "?" + urlencode(args)

        http = httpclient.AsyncHTTPClient()
        #todo: check validate_cert
        response = yield http.fetch(url, validate_cert=False)

        return tornado.escape.json_decode(response.body)


class CommonHandler(web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        self.handler_started = time.time()
        self._logger = None
        self._model_loader = None
        super(CommonHandler, self).__init__(application, request, **kwargs)
        self.vk_api = VKAPI(client_id=self.settings["vk_client_id"], client_secret=self.settings["vk_client_secret"])

    def on_finish(self):
        self.logger.info('Handler request finished in %0.3f sec.', time.time() - self.handler_started)

    @property
    def model_loader(self) -> ManagerLoader:
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

    def render(self, template, **kwargs):
        # add any variables we want available to all templates
        kwargs['current_user'] = self.user
        kwargs['xsrf'] = self.xsrf_token
        super(AuthCommonHandler, self).render(template, **kwargs)
