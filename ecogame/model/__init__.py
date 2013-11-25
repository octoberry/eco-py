from ecogame.model.objects import QuestManager, ZombieManager
from ecogame.model.user import UserManager


class ManagerLoader(object):
    """
    Загрузчик менеджеров, используется в хэндлерах и моделях
    """
    def __init__(self, db):
        self.db = db
        self._user_manager = None
        self._quest_manager = None
        self._zombie_manager = None

    @property
    def user_manager(self):
        if not self._user_manager:
            self._user_manager = UserManager(db=self.db, loader=self)
        return self._user_manager

    @property
    def quest_manager(self):
        if not self._quest_manager:
            self._quest_manager = QuestManager(db=self.db, loader=self)
        return self._quest_manager

    @property
    def zombie_manager(self):
        if not self._zombie_manager:
            self._zombie_manager = ZombieManager(db=self.db, loader=self)
        return self._zombie_manager



