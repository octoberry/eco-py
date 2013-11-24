# coding=utf-8
from bson import ObjectId
from motor import Op, MotorDatabase, MotorCollection
from tornado import gen


class ModelObject(object):
    """Базовый класс объекта"""

    db_collection_name = 'objects'

    def __init__(self, loader):
        self.id = None
        self.loader = loader

    def _id_selector(self) -> dict:
        """
        Возвращает dict - селектор текущего объекта по ID
        """
        if not self.id:
            raise KeyError('Object Id is empty')
        return {'_id', ObjectId(self.id)}

    @gen.coroutine
    def _update_record(self, value: dict):
        """
        Выполняет find_and_modify запрос к записи по ее _id
        """
        yield Op(self.object_db.find_and_modify, self._id_selector(), value)

    @property
    def db(self):
        return self.loader.db

    @property
    def object_db(self) -> MotorCollection:
        """Возвращает указатель на коллекцию в Mongo соответсвующую объекту"""
        return getattr(self.db, self.db_collection_name)

    def load_from_db(self, data: dict):
        self.id = data['_id']
        if 'cords' in data and data['cords']:
            self.cords = ModelCords(data['cords']['lat'], data['cords']['lng'])


class ModelManager(object):
    """Базовый класс менеджера объектов"""
    model_type = ModelObject

    def __init__(self, db: MotorDatabase, loader):
        self.db = db
        self.loader = loader

    @property
    def object_db(self) -> MotorCollection:
        """Возвращает указатель на коллекцию в Mongo соответсвующую объекту"""
        return getattr(self.db, self.model_type.db_collection_name)

    @gen.coroutine
    def get(self, object_id, **kwargs) -> ModelObject:
        """
        Возвращает объект по его id

        Дополнительными параметрами можно передать критерии поиска
        """
        query = {'_id': ObjectId(object_id)}
        if kwargs:
            query.update(kwargs)

        object_data = yield Op(self.object_db.find_one, query)

        model_object = None
        if object_data:
            model_object = self.model_type(self.loader)
            model_object.load_from_db(object_data)

        return model_object


class ModelCords(object):
    def __init__(self, lat=None, lng=None):
        self.lat = lat
        self.lng = lng
