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
        self._user_manager = None
        self._vk_api = None
        self._managers = {}
        self._quest_manager = None
        self._zombie_manager = None

    @property
    def vk(self) -> VKAPI:
        """vk.com API"""
        if not self._vk_api:
            self._vk_api = self._vk_api = VKAPI(client_id=self.settings["vk_client_id"],
                                                client_secret=self.settings["vk_client_secret"])
        return self._vk_api

    def __getattr__(self, name):
        """Пытается загрузить менеджер по его имени, например quest_manager"""
        return self._load_manager(name)

    def _load_manager(self, name: str, module_name: str=None) -> ModelManager:
        """Динамически создает менеджер и загружает его модуль по имени"""
        if name not in self._managers:
            if name[-8:] != '_manager':
                raise ValueError('Manager name %s is invalid', name)
            manager_name = name[:-8].capitalize() + 'Manager'
            module = importlib.import_module(module_name or 'ecogame.model.objects')
            manager = getattr(module, manager_name)
            self._managers[name] = manager(db=self.db, loader=self)
        return self._managers[name]

    @property
    def user_manager(self) -> ModelManager:
        return self._load_manager('user_manager', 'ecogame.model.user')
