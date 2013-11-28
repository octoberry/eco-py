var mapClickMode = false;
var map = null;

$( document ).ready(function() {
    $('#crystal_boom').on('click', function() {
        if (!mapClickMode) {
            mapClickMode = 'crystal';
            map.setOptions({draggableCursor:'url(/static/img/crystal.png) 32 35, default'});
        }
    });
});


function initialize() {
    var mapOptions = {
        center: new google.maps.LatLng(55.751, 37.655),
        zoom: 14,
        mapTypeId: google.maps.MapTypeId.TERRAIN,
        scrollwheel: false,
        navigationControl: false,
        mapTypeControl: false,
        scaleControl: false,
        zoomControl: false,
        maxZoom: 14,
        minZoom: 14
    };
    map = new google.maps.Map(document.getElementById("map_placeholder"),
        mapOptions);

    var selectedEcobot;

//drawing pollutions
    var pollutions = {};
    $.getJSON("/pollutions", function (data) {
        $.each(data, function (key, val) {
            pollutions[val.id] = new google.maps.Marker({
                position: new google.maps.LatLng(val.cords.lat, val.cords.lng),
                map: map,
                icon: '/static/resources/rubbish_small.png'
            });
        });
    });

    $.getJSON("/zombies", function (data) {
        $.each(data, function (key, val) {
            var currentZombie = new google.maps.Marker({
                position: new google.maps.LatLng(val.cords.lat, val.cords.lng),
                map: map,
                icon: '/static/resources/zombie_small.png',
                title: val.name
            });
            currentZombie.xspeed = (Math.random() - 0.5) / 5000;
            currentZombie.yspeed = (Math.random() - 0.5) / 5000;
            setInterval(function () {
                currentZombie.setPosition(new google.maps.LatLng(currentZombie.getPosition().lat() + currentZombie.xspeed, currentZombie.getPosition().lng() + currentZombie.yspeed));
            }, 3000);
        });
    });


    //drawing ecobot.
    $.getJSON("/robots", function (data) {
        $.each(data, function (key, val_robot) {
            var ecobot = new google.maps.Marker({
                position: new google.maps.LatLng(val_robot.cords.lat, val_robot.cords.lng),
                map: map,
                icon: '/static/resources/ecobot_small.png',
                title: 'EcoRobot'
            });
            ecobot.xspeed = 0;//(Math.random() - 0.5) / 5000;
            ecobot.yspeed = 0;//(Math.random() - 0.5) / 5000;
            ecobot.iterations = 0;
            ecobot.robotId = val_robot._id;
            setInterval(function () {
                if (ecobot.iterations > 0) {
                    ecobot.setPosition(new google.maps.LatLng(ecobot.getPosition().lat() + ecobot.xspeed, ecobot.getPosition().lng() + ecobot.yspeed));
                    ecobot.iterations--;
                }
            }, 100);

            google.maps.event.addListener(ecobot, 'click', function () {
                if (!mapClickMode) {
                    ecobot.setIcon('/static/resources/ecobot_small_selected.png');
                    selectedEcobot = ecobot;

                    map.setOptions({draggableCursor: 'crosshair'});

                    mapClickMode = 'robot';
                }
            });
        });
    });

    google.maps.event.addListener(map, 'click', function (event) {
        if (mapClickMode == 'robot' && selectedEcobot) {

            var updateRobotPosition = function () {
                selectedEcobot.setIcon('/static/resources/ecobot_small.png');
                //selectedEcobot.setPosition(event.latLng);

                var x = (selectedEcobot.getPosition().lat() - event.latLng.lat());
                var y = (selectedEcobot.getPosition().lng() - event.latLng.lng());
                length = Math.sqrt(x * x + y * y);
                selectedEcobot.iterations = Math.round((length * 5000));
                selectedEcobot.xspeed = -x / selectedEcobot.iterations;
                selectedEcobot.yspeed = -y / selectedEcobot.iterations;
                map.setOptions({draggableCursor: null});
                selectedEcobot = null;
            };
            $.ajax({
                url: '/robot/position',
                data: {id: selectedEcobot.robotId, cords: {lat: event.latLng.lat(), lng: event.latLng.lng()}},
                method: "post"
            }).done(updateRobotPosition);
        }
    });

    var updateBoomResult = function (data) {
        if (typeof data.status != 'undefined' && !data.status) {
            alert(data.msg);
        } else if (data.items && data.items.length) {
            for (var key in data.items) {
                var pollutionId = data.items[key];
                var pollutionMarker = pollutions[pollutionId];
                if (pollutionMarker) {
                    pollutionMarker.setMap(null);
                    delete pollutions[pollutionId];
                    pollutionMarker = null;
                }
            }
            alert('Ваш кристал бомбанул! Мир стал чище на ' + data.items.length + ' ед. загрязнений!');
        } else {
            alert('Вы бомбанули кристал, но никуда не попали!');
        }
        if (typeof data.balance != 'undefined') {
            $('#user_balance').html(data.balance);
        }
    };

    google.maps.event.addListener(map, 'click', function (event) {
        if (mapClickMode == 'crystal') {
            map.setOptions({draggableCursor: null});
            $.ajax({
                url: '/boom',
                data: {lat: event.latLng.lat(), lng: event.latLng.lng()},
                method: "post"
            }).done(updateBoomResult);
        }
        mapClickMode = false;
    });
}

google.maps.event.addDomListener(window, 'load', initialize);