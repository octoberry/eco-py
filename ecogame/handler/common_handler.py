from tornado.escape import json_encode, json_decode
from tornado import web, websocket, gen
import logging
import time
from tornado.web import MissingArgumentError
from ecogame.model.model import ModelError


class AbstractHandler(object):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.db = self.application.db

    @staticmethod
    def _response_as_json(data):
        """Формирует json ответ из данных. Автоматически вызывает as_view"""
        if not data:
            data = False
        return json_encode(data.as_view() if hasattr(data, 'as_view') else data)

    @property
    def loader(self):
        """
        :rtype: ecogame.model.ManagerLoader
        """
        return self.application.loader


class SocketHandler(AbstractHandler, websocket.WebSocketHandler):
    connections = set()

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)

    def get_current_user(self):
        return self.get_secure_cookie("user").decode(encoding='UTF-8')

    @gen.coroutine
    def open(self):
        self.logger.info("WebSocket opened")
        if self.current_user:
            self.logger.info('load user id:%s', self.current_user)
            user = yield self.loader.user_manager.get(self.current_user)
            if user:
                self.user = user
                self.logger.info('user id:%s found', self.current_user)
                SocketHandler.connections.add(self)
            else:
                self.clear_cookie("user")
                self.logger.warning('loading current user id:%s failed, not found', self.current_user)
                self.close()

    def on_close(self):
        """Удаляет хэндлер из списка подключенных, при отключении пользователя"""
        SocketHandler.connections.remove(self)

    def send_json(self, event, data):
        """Отправляет dict как json. Автоматически вызывает as_view"""
        json = {'event': event, 'data': data.as_view() if hasattr(data, 'as_view') else data}
        try:
            self.write_message(message=json)
        except Exception as e:
            self.logger.exception(e)

    def send_notice_json(self, msg, type_msg=None):
        """
        Отправляет уведомление пользователю
        :param msg: Текст уведомления
        :param type_msg: Тип уведомления, может быть success, info, danger, warning
        """
        data = {'msg': msg, 'type': type_msg or 'danger'}
        self.send_json(event='notice', data=data)

    @classmethod
    def send_json_all(cls, event, data):
        """Отправляет dict как json. Автоматически вызывает as_view"""
        for handler in cls.connections:
            if handler:
                handler.send_json(event, data)


class CommonHandler(AbstractHandler, web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        self.handler_started = time.time()
        super().__init__(application, request, **kwargs)
        self.request_j = self._arguments_to_json()

    def _arguments_to_json(self) -> dict:
        """
        Возвращает данные пришедшие в виде json_объекта как сериализованный объект
        """
        result = None
        content_type = self.request.headers.get("Content-Type", "")
        if content_type.startswith("application/json"):
            result = json_decode(self.request.body)
        return result

    _ARG_DEFAULT = []

    def get_argument(self, name, default=_ARG_DEFAULT, strip=True):
        content_type = self.request.headers.get("Content-Type", "")
        if content_type.startswith("application/json"):
            if name not in self.request_j:
                if default == self._ARG_DEFAULT:
                    raise MissingArgumentError(name)
                else:
                    return default
            else:
                return self.request_j[name]
        else:
            return super().get_argument(name, default, strip)

    def on_finish(self):
        self.logger.info('Handler request finished in %0.3f sec.', time.time() - self.handler_started)

    def send_error_json(self, msg: str, data=None):
        """Отправляет json с сообщением об ошибке"""
        error_data = {'status': False, 'msg': msg}
        if data:
            error_data.update(data)
        self.send_json(error_data)

    def send_json(self, data):
        """Отправляет dict как json. Автоматически вызывает as_view"""
        self.set_header('Content-Type', 'application/json')
        self.write(self._response_as_json(data))
        self.finish()

    def write_error(self, status_code, **kwargs):
        overrided_error = False
        if 'exc_info' in kwargs:
            exception = kwargs['exc_info'][1]
            if isinstance(exception, ModelError):
                msg = str(ModelError)
                self.set_status(400)
                self.send_json({'msg': msg})
                overrided_error = True
        if not overrided_error:
            super().write_error(status_code, **kwargs)


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
            user = yield self.loader.user_manager.get(self.current_user)
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
