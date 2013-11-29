from tornado import gen
from ecogame.handler.common_handler import CommonHandler
from ecogame.model.social_helper import fill_user_from_vk
from ecogame.vk import VKHandlerMixin


class VKAuthHandler(CommonHandler, VKHandlerMixin):
    @gen.coroutine
    def get(self):
        redirect_url = 'http://127.0.0.1:8001/auth/vkontakte'
        if self.get_argument("code", False):
            token = yield self.loader.vk.get_access_token(self.get_argument("code"), redirect_url=redirect_url)
            access_token = token['access_token']
            users = yield self.loader.vk.get_users(access_token=access_token)
            if not users:
                self.logger.warning('Empty VK auth response')
                self.redirect('/')
            else:
                socail_data = users[0]
                socail_data['access_token'] = access_token
                user = yield self.loader.user_manager.find_by_social('vk', socail_data['id'])
                if not user:
                    user = self.loader.user_manager.new_object()
                    fill_user_from_vk(user, socail_data)
                    yield self.loader.user_manager.register(user)
                yield user.logined(social='vk', token=access_token)
                self.set_secure_cookie('user', str(user.id))
                self.redirect('/game')
        else:
            self.authorize_redirect(redirect_uri=redirect_url, client_id=self.loader.vk.client_id, scope='friends')
