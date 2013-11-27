from tornado import gen, httpclient, escape
from tornado.httputil import url_concat

from urllib.parse import urlencode


class VKAPI(object):
    """
    API vk.com
    Реализует работы с авторизацией и методами API

    """
    _OAUTH_ACCESS_TOKEN_URL = "https://api.vk.com/oauth/access_token?"
    _OAUTH_AUTHORIZE_URL = "http://api.vk.com/oauth/authorize?"
    _OAUTH_REQUEST_URL = "https://api.vk.com/method/"
    _API_VERSION = '5.4'

    default_user_fields = 'sex,bdate,city,country,photo_50,photo_200_orig'

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    @gen.coroutine
    def get_access_token(self, code, redirect_url):
        http = httpclient.AsyncHTTPClient()
        url = self._oauth_request_token_url(client_id=self.client_id,
                                            code=code,
                                            client_secret=self.client_secret,
                                            extra_params={'redirect_uri': redirect_url})
        response = yield http.fetch(url, validate_cert=False)
        return escape.json_decode(response.body)

    @gen.coroutine
    def get_users(self, access_token, user_ids=None, fields=None, params=None):
        """
        Получает данные пользователя

        Если user_ids не переданы - запрашивает данные текущего пользователя

        Возвращает массив найденных пользователей
        """
        args = {'fields': fields or self.default_user_fields}
        if user_ids:
            args = {"uid": user_ids}
        if params:
            args.update(params)
        user = yield self.request(api_method="users.get", access_token=access_token, params=args)
        return user

    def authorize_redirect_url(self, client_id=None, scope='', redirect_uri=None):
        """Создает URL запроса авторизации vk.com"""
        args = {
            "response_type": "code",
            "v": self._API_VERSION,
            "redirect_uri": redirect_uri,
            "client_id": client_id
        }
        if scope:
            args['scope'] = scope
        return url_concat(self._OAUTH_AUTHORIZE_URL, args)

    def _oauth_request_token_url(self, redirect_uri=None, client_id=None,
                                 client_secret=None, code=None,
                                 extra_params=None):
        url = self._OAUTH_ACCESS_TOKEN_URL
        args = dict(
            redirect_uri=redirect_uri,
            code=code,
            client_id=client_id,
            client_secret=client_secret,
            v=self._API_VERSION
        )
        if extra_params:
            args.update(extra_params)
        return url_concat(url, args)

    @gen.coroutine
    def request(self, api_method, params, access_token):
        """
        Осуществляет запрос к API VK используюя access_token

        api_method - например users.get
        """
        args = {"access_token": access_token, "v": self._API_VERSION}

        if params:
            args.update(params)
        url = self._OAUTH_REQUEST_URL + api_method + "?" + urlencode(args)

        http = httpclient.AsyncHTTPClient()
        response = yield http.fetch(url)
        response_body = escape.json_decode(response.body)
        if 'response' not in response_body:
            raise RuntimeError('Response should contain response field')
        return response_body['response']


class VKHandlerMixin(object):
    """Реализует метод запроса авторизации"""
    def authorize_redirect(self, client_id=None, redirect_uri=None, scope=''):
        url = self.loader.vk.authorize_redirect_url(client_id=client_id, redirect_uri=redirect_uri, scope=scope)
        self.redirect(url)
