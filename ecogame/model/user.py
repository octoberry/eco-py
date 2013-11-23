from ecogame.model.model import ModelManager, ModelObject


class User(ModelObject):
    db_collection_name = 'user'

    def __init__(self, loader):
        super().__init__(loader)
        self.name = None
        self.cords = None
        self.social = None

    def load_from_db(self, data: dict):
        super().load_from_db(data)
        self.name = data['name']
        self.social = data['social']


class UserManager(ModelManager):
    model_type = User

