from tornado import gen
from tornado.escape import json_encode
from ecogame.handler.common_handler import CommonHandler, AuthCommonHandler

import logging

import tornado.web
import tornado.escape
from tornado.auth import OAuth2Mixin
from tornado import httpclient

from urllib.parse import urlencode


class VKMixin(OAuth2Mixin):
    _OAUTH_ACCESS_TOKEN_URL = "https://api.vkontakte.ru/oauth/access_token?"
    _OAUTH_AUTHORIZE_URL = "http://api.vk.com/oauth/authorize?"
    _OAUTH_REQUEST_URL = "https://api.vkontakte.ru/method/"

    @gen.coroutine
    def get_access_token(self, code):
        http = httpclient.AsyncHTTPClient()
        url = self._oauth_request_token_url(client_id=self.vk_api.client_id,
                                            code=code,
                                            client_secret=self.vk_api.client_secret,
                                            extra_params={'grant_type': 'client_credentials'})
        result = yield http.fetch(url, validate_cert=False)
        return result

    def get_authenticated_user(self, code, callback=None):
        http = httpclient.AsyncHTTPClient()
        http.fetch(self._oauth_request_token_url(client_id=self.vk_api.client_id,
                                                 code=code,
                                                 client_secret=self.vk_api.client_secret,
                                                 extra_params={'grant_type': 'client_credentials'}),
                   self.async_callback(self._on_access_token, callback), validate_cert=False)


    def get_authenticated_user(self, callback=None):
        code = self.get_argument("code")
        http = httpclient.AsyncHTTPClient()
        http.fetch(self._oauth_request_token_url(client_id=self.vk_api.client_id,
                                                 code=code,
                                                 client_secret=self.vk_api.client_secret,
                                                 extra_params={'grant_type': 'client_credentials'}),
                   self.async_callback(self._on_access_token, callback), validate_cert=False)

    def vk_request(self, callback, api_method, params, access_token=None):
        if access_token is None:
            logging.warning("Access token required")
            callback()
            return

        args = {"access_token": access_token}

        if params:
            args.update(params)
        url = self._OAUTH_REQUEST_URL + api_method + ".json?" + urlencode(args)

        http = httpclient.AsyncHTTPClient()
        http.fetch(url, self.async_callback(self._on_vk_request, callback), validate_cert=False)

    def _on_vk_request(self, callback, response):
        if response.error:
            logging.warning("Could not fetch on _on_vk_request")
            #logging.warning(response.error)
            callback(None)
            return
        callback(tornado.escape.json_decode(response.body))

    def _on_access_token(self, callback, response):
        if response.error:
            logging.warning("Error response %s fetching %s", response.error, response.request.url)
            callback(None)
            return
        token = self._oauth_parse_response(response.body)

        if token is None:
            logging.warning("access_token is broken")
            callback(None)
            return

        access_token = token['access_token'] # get access_token
        uid = token['user_id'] # get uid
        self._oauth_get_user(self.async_callback(self._on_oauth_get_user, access_token, callback), uid=uid, access_token=access_token)

    def _oauth_get_user(self, callback, access_token=None, uid=0):
        args = {"uid": uid}
        self.vk_request(api_method="getProfiles", access_token=access_token, params=args, callback=callback)

    def _on_oauth_get_user(self, access_token, callback, user):
        if not user:
            raise tornado.web.HTTPError(500, "Auth failed")
            callback(None)
            return
        user["access_token"] = access_token
        callback(user)

    def _oauth_parse_response(self, response):
        if response:
            feed = tornado.escape.json_decode(response)
            return feed
        return None


class VKAuthHandler(AuthCommonHandler, VKMixin):
    @gen.coroutine
    def get(self):
        redirect_url = 'http://127.0.0.1:8001/auth/vkontakte'
        if self.get_argument("code", False):
            token = yield self.vk_api.get_access_token(self.get_argument("code"), redirect_url=redirect_url)
            user = yield self.vk_api.get_users(access_token=token['access_token'])
            print(user)
            print(user)
            print(user)
            print(user)

            if not user:
                self.logger.warning('Empty VK auth response')
                self.redirect('/')

            #else:
            #    yield self.user_manager.sync_user(hh_user)
            #    self.set_secure_cookie('user_id', hh_user['id'])
            #    self.redirect('/dashboard')
        else:
            #todo: remove redirect_uri arg

            yield self.authorize_redirect(
                redirect_uri=redirect_url,
                client_id=self.vk_api.client_id,
                extra_params={'scope': 'friends', 'response_type': 'code'})
