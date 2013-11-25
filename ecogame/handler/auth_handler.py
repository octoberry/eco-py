from tornado import gen
from ecogame.handler.common_handler import CommonHandler
from ecogame.model.user import fill_user_from_vk
from ecogame.vk import VKHandlerMixin


class VKAuthHandler(CommonHandler, VKHandlerMixin):
    @gen.coroutine
    def get(self):
        redirect_url = 'http://127.0.0.1:8001/auth/vkontakte'
        if self.get_argument("code", False):
            token = yield self.vk_api.get_access_token(self.get_argument("code"), redirect_url=redirect_url)
            users = yield self.vk_api.get_users(access_token=token['access_token'])
            if not users:
                self.logger.warning('Empty VK auth response')
                self.redirect('/')
            else:
                user = yield self.model_loader.user_manager.find_by_social('vk', users[0]['id'])
                if not user:
                    user = self.model_loader.user_manager.new_object()
                    fill_user_from_vk(user, users[0])
                    yield self.model_loader.user_manager.register(user)
                self.set_secure_cookie('user', str(user.id))
                self.redirect('/game')
        else:
            self.authorize_redirect(redirect_uri=redirect_url, client_id=self.vk_api.client_id, scope='friends')
