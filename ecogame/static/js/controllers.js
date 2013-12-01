'use strict';

/* Controllers */

angular.module('ecoGame.controllers', ['leaflet-directive']).
    controller('MapsCtrl', ['$scope', function($scope) {
        console.log('controller called');
        angular.extend($scope, {
            center: {
                lat: 55.751,
                lng: 37.655,
                zoom: 12
            },
            defaults: {
                tileLayer: 'http://{s}tile.stamen.com/watercolor/{z}/{x}/{y}.png',
                tileLayerOptions: {
                    subdomains: ['', 'a.', 'b.', 'c.', 'd.'],
                    attribution: 'EcoGame',
                    errorTileUrl: "",
                    tileSize: 256,
                    unloadInvisibleTiles: false,
                    updateWhenIdle: false,
                    zoomOffset: 0
                },
                scrollWheelZoom: false,
                doubleClickZoom: false,
                boxZoom: false
            }
        });

  }])
  .controller('QuestsCtrl', ['Quest', '$scope', '$location', function(Quest, $scope, $location) {
        $scope.quests = Quest.query();

        $scope.isShow = function (quest) {
            return !(quest.accepted == true);
        };

        $scope.acceptQuest = function(quest) {
            quest.$accept(function() {
                quest.accepted = true;
                 return $location.url('/my/quests');
            });
        };
  }])
  .controller('MyQuestsCtrl', ['Quest', '$scope', function(Quest, $scope) {
        console.log('some log msg');
        $scope.quests = Quest.my();

//        $scope.isShow = function (quest) {
//            return !(quest.accepted == true);
//        };

//        $scope.acceptQuest = function(quest) {
//            quest.$accept(function(){
//                quest.accepted = true;
//            });
//        };
  }])
  .controller('MyCtrl2', [function() {

  }]);