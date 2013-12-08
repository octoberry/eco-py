(function(window, angular) {'use strict';


angular.module('ecoGame.Robot', ['ng'])

//Robot service
.factory('Robot', ['$rootScope', 'GameStream', 'leafletData', 'User', 'Boom',
    function ($rootScope, GameStream, leafletData, User, Boom) {

        var icons = {
            robot: L.icon({ iconUrl: '/static/resources/ecobot_small.png' }),
            robot_alien: L.icon({ iconUrl: '/static/resources/ecobot_small_gray.png' }),
            robot_selected: L.icon({ iconUrl: '/static/resources/ecobot_small_selected.png' })
        };

        var Service = {};
        Service.dataStore = {};
        Service.selected = false;

        Service.map = null;
        leafletData.getMap().then(function (map) {
            Service.map = map;

            map.on('click', function (e) {
                console.log(Boom.selected);
                if (Service.selected && !Boom.selected) {
                    Service.selected.marker.setIcon(icons.robot);
                    Service.move(Service.selected.id, e.latlng);
                    Service.selected = false;
                }
            })
        });

        Service.find = function () {
            GameStream.sendRequest("robots.find");
        };

        Service.move = function (robotId, latLng) {
            var data = {
                'id': robotId,
                'cords': {lat: latLng.lat, 'lng': latLng.lng}
            };
            GameStream.sendRequest("robots.move", data);
        };

        $rootScope.$on('game.robots', function (event, robots) {
            robots.forEach(function (robot) {
                var isOwnUser = robot.user == User.id;
                var robotStartCords = [
                    [robot.cords.lat, robot.cords.lng],
                    [robot.cords.lat, robot.cords.lng]
                ];
                var robotStartLine = L.polyline(robotStartCords);
                robot.marker = L.animatedMarker(robotStartLine.getLatLngs(), {
                    keyboard: false,
                    icon: isOwnUser ? icons.robot : icons.robot_alien,
                    clickable: true,
                    zIndexOffset: 2000,
                    autoStart: false
                });

                robot.marker.on('click', function (e) {
                    if (isOwnUser) {
                        Service.selected = robot;
                        console.log(robot);
                        robot.marker.setIcon(icons.robot_selected);
                    }
                });
                Service.dataStore[robot.id] = robot;
                robot.marker.addTo(Service.map);
            });

        });


        $rootScope.$on('game.robots.move', function (event, robot) {
            var robotToMove = Service.dataStore[robot.id];
            if (robotToMove) {
                var marker = robotToMove.marker;
                var robotStartCords = [
                    [marker.getLatLng().lat, marker.getLatLng().lng],
                    [marker.getLatLng().lat, marker.getLatLng().lng],
                    [robot.cords.lat, robot.cords.lng]
                ];
                var line_new = L.polyline(robotStartCords);
                marker.setLine(line_new.getLatLngs());
                marker._i = 0;
                marker.start();
            }
        });


        return Service;
}]);

})(window, window.angular);
