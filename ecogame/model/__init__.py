from motor import MotorDatabase
from ecogame.vk import VKAPI
import importlib
from ecogame.model.model import ModelManager


class ManagerLoader(object):
    """
    Загрузчик менеджеров, используется в хэндлерах и моделях
    """
    def __init__(self, settings: dict, db: MotorDatabase):
        self.db = db
        self.settings = settings
        self._vk_api = None
        self._managers = {}

    @property
    def vk(self) -> VKAPI:
        """vk.com API"""
        if not self._vk_api:
            self._vk_api = self._vk_api = VKAPI(client_id=self.settings["vk_client_id"],
                                                client_secret=self.settings["vk_client_secret"])
        return self._vk_api

    def __getattr__(self, name):
        """
        Пытается загрузить менеджер по его имени, например quest_manager
        :returns: loaded model manager
        :rtype: ModelManager
        """
        return self._load_manager(name)

    def _load_manager(self, name: str) -> ModelManager:
        """Динамически создает менеджер и загружает его модуль по имени"""
        if name not in self._managers:
            if name[-8:] != '_manager':
                raise ValueError('Manager name %s is invalid' % name)
            manager_name = name[:-8].capitalize() + 'Manager'
            module = importlib.import_module('ecogame.model.%s' % name[:-8])
            manager = getattr(module, manager_name)
            self._managers[name] = manager(db=self.db, loader=self)
        return self._managers[name]

    @property
    def user_manager(self) -> ModelManager:
        """
        :rtype: ecogame.model.user.UserManager
        """
        return self._load_manager('user_manager')

    @property
    def zombie_manager(self) -> ModelManager:
        """
        :rtype: ecogame.model.zombie.ZombieManager
        """
        return self._load_manager('zombie_manager')

    @property
    def quest_manager(self) -> ModelManager:
        """
        :rtype: ecogame.model.quest.QuestManager
        """
        return self._load_manager('quest_manager')

    @property
    def pollution_manager(self) -> ModelManager:
        """
        :rtype: ecogame.model.pollution.PollutionManager
        """
        return self._load_manager('pollution_manager')

    @property
    def robot_manager(self) -> ModelManager:
        """
        :rtype: ecogame.model.robot.RobotManager
        """
        return self._load_manager('robot_manager')
