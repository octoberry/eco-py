(function(window, angular) {'use strict';

angular.module('ecoGame.Pollution', ['ng'])
.factory('Pollution', ['$rootScope', 'GameStream', 'leafletData', function ($rootScope, GameStream, leafletData) {
    var Service = {};
    Service.dataStore = {};
    Service.visible = {};

    Service.clear = function(ids) {
        ids.forEach(function(objectId) {
            if (Service.dataStore[objectId]) delete Service.dataStore[objectId];
            if (Service.visible[objectId])  delete Service.visible[objectId];
        });
    };

    Service.find = function () {
        GameStream.sendRequest("pollution.find");
    };

    $rootScope.$on('game.pollutions', function (event, pollutions) {
        pollutions.forEach(function (pollution) {
            Service.dataStore[pollution.id] = pollution;
        });
        Service.fillVisibleMarkers();
    });

    $rootScope.$on('game.pollution.remove', function (event, data) {
        Service.clear(data.items);
    });

    Service.map = null;
    leafletData.getMap().then(function (map) {
        Service.map = map;
    });

    var isFitInBound = function(bounds, cords) {
        var northEast = bounds._northEast;
        var southWest = bounds._southWest;
        return (southWest.lat - 0.01 < cords.lat && northEast.lat + 0.01 > cords.lat &&
            southWest.lng - 0.01 < cords.lng && northEast.lng + 0.01 > cords.lng);
    };

    //filling visible pollutions list
    Service.fillVisibleMarkers = function() {
        leafletData.getMap().then(function (map) {
            var bounds = map.getBounds();
            angular.forEach(Service.dataStore, function(object) {
                var cords = object.cords;
                var visibleObject = Service.visible[object.id];
                if (isFitInBound(bounds, cords)) {
                    if (!visibleObject) {
                        Service.visible[object.id] = object;
                    }
                } else if (visibleObject) {
                    delete Service.visible[object.id];
                }
            });
        });
    };

    return Service;
}])


.directive('pollutionMap', ['leafletData', 'Pollution', function(leafletData, Pollution) {
    return {
        restrict: "A",
        scope: false,
        replace: false,
        require: 'leaflet',

        link: function(scope) {
            var icon = L.icon({ iconUrl: '/static/resources/rubbish_small.png' });

            var markers = {};
            leafletData.getMap().then(function(map) {
                //update visible pollution markers
                scope.$watch('pollutions', function (visibleObjects, oldVisible) {
                    angular.forEach(visibleObjects, function(object) {
                        if (!markers[object.id]) {
                            markers[object.id] = L.marker([object.cords.lat, object.cords.lng], {
                                keyboard: false,
                                icon: icon
                            });
                            markers[object.id].addTo(map);
                        }
                    });
                    angular.forEach(oldVisible, function(object, id) {
                        if (!visibleObjects[id] && markers[id]) {
                            map.removeLayer(markers[id]);
                            delete markers[id];
                        }
                    });
                }, true);

                //force update visible pollution on change zoom or drag
                map.on('dragend', Pollution.fillVisibleMarkers);
                map.on('zoomend', Pollution.fillVisibleMarkers);
            });
        }
    }
}]);

})(window, window.angular);