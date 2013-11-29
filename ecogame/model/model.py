# coding=utf-8
from bson import ObjectId
from motor import Op, MotorDatabase, MotorCollection
from tornado import gen


class ModelError(Exception):
    """
    Ошибка в обработке модели
    """
    pass


class ModelObject(object):
    """Базовый класс объекта"""

    db_collection_name = 'objects'
    """Имя коллекции объектов в MongoDB"""

    view_fields = []
    """Список публичных полей, возвращаемых методом as_view"""

    def __init__(self, loader):
        """
        Создает объект модели

        :param loader: загрузчик объектов
        :type loader: ecogame.model.ManagerLoader
        """
        super().__init__()
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
        return self._view_to_json(result)

    def _view_to_json(self, view_data):
        """Подготоваливает поля в view к преобразованию в json"""
        if isinstance(view_data, dict):
            result = {key: self._view_to_json(value) for key, value in view_data.items()}
        elif isinstance(view_data, list):
            result = [self._view_to_json(value) for value in view_data]
        elif isinstance(view_data, ObjectId):
            result = str(view_data)
        else:
            result = view_data
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

    def as_db_dict(self) -> dict:
        """
        Возвращает dict для сохранения в базе данных

        По умолчанию возвращает все свойства объекта типа: dict, list, str, int, float, bool

        Может быть переопреден в конкретных реализациях
        """
        allowed_types = (dict, list, str, int, float, bool)
        result = {key: value for key, value in vars(self).items() if isinstance(value, allowed_types)}
        #подменяем id на _id при сохранении
        if 'id' in result:
            if result['id']:
                result['_id'] = result['id']
            result.pop("id", None)
        return result


class ModelList(list):
    """Класс-обертка для списков, реализующий доп. методы"""
    def as_view(self) -> dict:
        """Возвращает список as_view представлений моделей"""
        return [obj.as_view() for obj in self]

    def as_ids_view(self) -> list:
        """
        Возвращает список ID моделей в строковом представлении, а не ObjectID!
        """
        return [str(obj.id) for obj in self]


class ModelManager(object):
    """Базовый класс менеджера объектов"""
    model_type = ModelObject

    def __init__(self, db: MotorDatabase, loader):
        """
        Менеджер модели, преднозначен для поиска моделей и групповых операций

        :param db: mongo db
        :type db: MotorDatabase
        :param loader: загрузчик объектов
        :type loader: ecogame.model.ManagerLoader
        """
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
            model_object = self.new_object()
            model_object.load_from_db(object_data)

        return model_object

    def new_object(self) -> ModelObject:
        """Создает пустой экземпляр модели"""
        model_object = self.model_type(self.loader)
        return model_object

    @gen.coroutine
    def save(self, model: ModelObject):
        """
        Создает или обновляет целиком модель в базе.

        ! Не рекомендуется к использованию для обновления объектов
        """
        model_data = model.as_db_dict()
        oid = yield Op(self.object_db.save, model_data)
        model.id = ObjectId(oid)

    @gen.coroutine
    def insert_multiple(self, models: list):
        """
        Создает набор коллекций моделей в базе.
        """
        models_operation = [Op(self.object_db.save, model.as_db_dict()) for model in models]
        yield models_operation

    @gen.coroutine
    def find(self, query: dict=None) -> ModelList:
        """Осуществляет поиск моделей в коллекции удовлетворяющих условию query"""
        objects = ModelList()
        cursor = self.object_db.find(query)
        while (yield cursor.fetch_next):
            obj_data = cursor.next_object()
            model = self.new_object()
            model.load_from_db(obj_data)
            objects.append(model)

        return objects

    @gen.coroutine
    def find_one(self, query: dict=None) -> ModelObject:
        """Осуществляет поиск одной модели в коллекции удовлетворяющих условию query"""
        model = None
        object_data = yield Op(self.object_db.find_one, query)
        if object_data:
            model = self.new_object()
            model.load_from_db(object_data)
        return model

    @gen.coroutine
    def count(self, query: dict=None) -> int:
        """Осуществляет подсчет моделей в коллекции удовлетворяющих условию query"""
        objects_count = yield Op(self.object_db.find(query).count)
        return objects_count


class ModelCordsMixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cords = None

    def load_from_db(self, data: dict):
        super().load_from_db(data)
        if 'cords' in data and data['cords']:
            self.cords = dict(lat=data['cords'][0], lng=data['cords'][1])

    def as_db_dict(self) -> dict:
        result = super().as_db_dict()
        if self.cords:
            result['cords'] = [self.cords['lat'], self.cords['lng']]
        elif 'cords' in result:
            del result['cords']
        return result


class ManagerCordsMixin(ModelManager):
    @staticmethod
    def _cords_query(lat: float, lng: float, radius: float, query: dict=None):
        query_cords = {"cords": {"$geoWithin": {
            "$center": [[round(lat, 6), round(lng, 6)], radius]
        }}}
        if query:
            query_cords.update(query)
        return query_cords

    @gen.coroutine
    def find_in_cords(self, lat: float, lng: float, radius: float, query: dict=None) -> ModelList:
        """
        Осуществляет поиск объектов в указанных координатах, с заданным радиусом поиска

        :param lat: latitude
        :param lng: longitude
        :param radius: радиус поиска
        :param query: дополнительные параметры запроса
        :return: Список ModelObject
        """
        objects = yield self.find(self._cords_query(lat=lat, lng=lng, radius=radius, query=query))
        return objects

    @gen.coroutine
    def remove_in_cords(self, lat: float, lng: float, radius: float, query: dict=None):
        """
        Удаляет набор моделей в заданных координатах.
        :param lat: latitude
        :param lng: longitude
        :param radius: радиус поиска
        :param query: дополнительные параметры запроса
        """
        yield Op(self.object_db.remove, self._cords_query(lat=lat, lng=lng, radius=radius, query=query))
