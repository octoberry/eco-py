from ecogame.model.user import UserManager


class ManagerLoader(object):
    """
    Загрузчик менеджеров, используется в хэндлерах и моделях
    """
    def __init__(self, db):
        self.db = db
        self._user_manager = None

    @property
    def user_manager(self):
        if not self._user_manager:
            self._user_manager = UserManager(db=self.db, loader=self)
        return self._user_manager



