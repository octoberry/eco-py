var quests = [{
    "title": "Задание \"Вторая жизнь вещей\"",
    "type": 1,
    "short_desc": "Сдай ненужные вещи",
    "desc": "Подключить родителей. Собрать ненужную одежду, игрушки, гаджеты и отвезти на пункты приемы/в детдома/в центры социального обслуживания/церковь",
    "price": 2
}, {
    "title": "Задание \"Утилизация отходов\"",
    "type": 2,
    "short_desc": "Начни собирать отходы",
    "desc": "<p>1.Выдели место в квартире или своей комнате, где ты будешь собирать бумагу</p><p>2. Собири несколько килограммов макулатуры из того что появляется в тоей комнате, пришли фотографию где мама или папа держит безмен с бумагой а ты рядом</p><p>3. Отнеси в один из ближайших пунктов, пришли фото</p>",
    "price": 4
}, {
    "title": "Организуй субботник ",
    "type": 3,
    "short_desc": "Организуй субботник",
    "desc": "<p>1.	Посмотри вокруг - какая часть твоего района нуждается в очистке большевсего?</p><p>2. Поставь точку на карте</p><p>3. Напиши один абзац текста о том, почему ты так считаешь</p><p>4. Можешь добавить фотки на сайт</p><p>5. Расшарь свои мысли с друзьями и узнай кто из них разделяет твою точку зрения</p><p>6. Обсуди с друзьями какие инструменты вам понадобятся для расчистки этой территории</p><p>7. Поговори с родителями и учителями - найди того, кто согласится стать куратором ваших действий</p><p>8. Назначьте дату расчистки и отметьте её в календаре</p><p>9. Зачекиньтесь на месте во время вашей расчистки. Сфотографируйте место до и после ваших действий</p>",
    "price": 10
}, {
    "title": "Экономия электроэнергии",
    "type": 4,
    "short_desc": "Перейди на энергосберегающие лампочки",
    "desc": "<p>1. возвращая из школы поднимись по лестнице пешком</p><p>2. посчитай количество обычных лампочек</p><p>3. сыграй в игру “веселый электрик” (показываешь мышкой лампочки, которые видел, электрик меняет их энергосберегающие, говорит тебе сколько ты сэкономил за год в пересчете на мороженное ), приз ща игру какой то виртуальный эко-предмет, близ не зависит от кол-ва лампочек</p><p>4. отправь своего эко-робота поставить полученный эко-предмет на виртуальную карту рядом со своим домом.</p>",
    "price": 5
}];

var user = {
    "_id" : ObjectId("5290f3c37fd7e09bba28976b"),
    "name": "Tom",
    "balance": 0,
    "social": {
        "vk": {
            "id": 205387401,
            "first_name": "Tom",
            "last_name": "Cruise",
            "city": "5331",
            "photo_50": "http://cs402330.vk.me/v402330401/9760/pV6sZ5wRGxE.jpg",
            "verified": 1
        }
    }
};

var zombies = [{
    name: "Леонид Агутин",
    users: [ObjectId("5290f3c37fd7e09bba28976b"), ObjectId("ololo")],
    social: {},
    cords: {lng: 37.652071, lat: 55.746463}
}];