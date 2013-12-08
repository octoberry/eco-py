(function(window, angular) {'use strict';


angular.module('ecoGame.Boom', ['ng'])

.factory('Boom', ['GameStream', function (GameStream) {
    var Service = {};
    Service.selected = false;

    Service.boom = function (latlng) {
        var data = { 'cords': {lat: latlng.lat, 'lng': latlng.lng} };
        GameStream.sendRequest("boom.boom", data);
    };

    return Service;
}])


})(window, window.angular);
