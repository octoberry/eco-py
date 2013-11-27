from ecogame.model.objects import QuestManager, ZombieManager
from ecogame.model.user import UserManager
from motor import MotorDatabase
from ecogame.vk import VKAPI


class ManagerLoader(object):
    """
    Загрузчик менеджеров, используется в хэндлерах и моделях
    """
    def __init__(self, settings: dict, db: MotorDatabase):
        self.db = db
        self.settings = settings
        self._user_manager = None
        self._vk_api = None
        self._quest_manager = None
        self._zombie_manager = None

    @property
    def vk(self) -> VKAPI:
        """vk.com API"""
        if not self._vk_api:
            self._vk_api = self._vk_api = VKAPI(client_id=self.settings["vk_client_id"],
                                                client_secret=self.settings["vk_client_secret"])
        return self._vk_api

    @property
    def user_manager(self) -> UserManager:
        if not self._user_manager:
            self._user_manager = UserManager(db=self.db, loader=self)
        return self._user_manager

    @property
    def quest_manager(self) -> QuestManager:
        if not self._quest_manager:
            self._quest_manager = QuestManager(db=self.db, loader=self)
        return self._quest_manager

    @property
    def zombie_manager(self) -> ZombieManager:
        if not self._zombie_manager:
            self._zombie_manager = ZombieManager(db=self.db, loader=self)
        return self._zombie_manager
