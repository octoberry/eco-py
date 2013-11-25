# coding=utf-8
from bson import ObjectId
from motor import Op, MotorDatabase, MotorCollection
from tornado import gen


class ModelObject(object):
    """Базовый класс объекта"""

    db_collection_name = 'objects'
    """Имя коллекции объектов в MongoDB"""

    view_fields = []
    """Список публичных полей, возвращаемых методом as_view"""

    def __init__(self, loader):
        self.id = None
        self.loader = loader

    def _id_selector(self) -> dict:
        """Возвращает dict - селектор текущего объекта по ID"""
        if not self.id:
            raise KeyError('Object Id is empty')
        return {'_id': self.id}

    @gen.coroutine
    def _update_record(self, value: dict):
        """Выполняет find_and_modify запрос к записи по ее _id"""
        yield Op(self.object_db.update, self._id_selector(), value)

    @property
    def db(self):
        return self.loader.db

    def as_view(self) -> dict:
        """Возвращает dict-представление модели, с разрашенными в view_fields свойствами"""
        result = {'id': str(self.id)}
        result.update({field: getattr(self, field) for field in self.view_fields})
        return result

    @property
    def object_db(self) -> MotorCollection:
        """Возвращает указатель на коллекцию в Mongo соответсвующую объекту"""
        return getattr(self.db, self.db_collection_name)

    def load_from_db(self, data: dict):
        """
        Загружает данные из бд в модель

        Заполняет все поля при совпадении имени поля в БД и имени свойства в модели.

        Может быть переопреден в конкретных реализациях
        """
        self.id = data['_id']
        for field, value in data.items():
            if field != 'cords' and hasattr(self, field):
                setattr(self, field, value)


class ModelList(list):
    """Класс-обертка для списков, реализующий доп. методы"""
    def as_view(self) -> dict:
        """Возвращает список as_view представлений моделей"""
        return [obj.as_view() for obj in self]


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
    def get(self, object_id: ObjectId, **kwargs) -> ModelObject:
        """
        Возвращает объект по его id

        Дополнительными параметрами можно передать критерии поиска
        """
        m_id = object_id if isinstance(object_id, ObjectId) else ObjectId(object_id)
        query = {'_id': m_id}
        if kwargs:
            query.update(kwargs)

        object_data = yield Op(self.object_db.find_one, query)

        model_object = None
        if object_data:
            model_object = self.model_type(self.loader)
            model_object.load_from_db(object_data)

        return model_object

    @gen.coroutine
    def find(self, query: dict=None) -> ModelList:
        objects = ModelList()
        cursor = self.object_db.find(query)
        while (yield cursor.fetch_next):
            obj_data = cursor.next_object()
            model = self.model_type(self.loader)
            model.load_from_db(obj_data)
            objects.append(model)

        return objects


class ModelCordsMixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cords = None

    def load_from_db(self, data: dict):
        super().load_from_db(data)
        if 'cords' in data and data['cords']:
            self.cords = dict(lat=data['cords']['lat'], lng=data['cords']['lng'])
