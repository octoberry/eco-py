'use strict';

/* Controllers */

angular.module('ecoGame.controllers', ['leaflet-directive']).
    controller('MapsCtrl', ['$scope', '$rootScope', 'Notice', 'Zombie', 'Robot', '$log', 'leafletData', 'Boom', 'User', 'Pollution',
        function ($scope, $rootScope, Notice, Zombie, Robot, $log, leafletData, Boom, User, Pollution) {
            $log.info('maps controller');

            setTimeout(function () {
                Robot.find();
                Pollution.find();
            }, 1000);

            $scope.boomSelect = function() {
                Boom.selected = true;
                console.log(Boom.selected, 11);
            };

            $scope.pollutions = Pollution.visible;
            $scope.user = User;

            angular.extend($scope, {
                center: {
                    lat: 55.751,
                    lng: 37.655,
                    zoom: 14
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
                    minZoom: 11,
                    maxZoom: 14,
//                    todo: check why not work
//                    maxBounds: L.latLngBounds(L.latLng(55.670, 37.405), L.latLng(55.833, 37.906)),
                    scrollWheelZoom: false,
                    boxZoom: false
                }
            });

            //todo: try to scale size
            var icons = {
                zombie: L.icon({ iconUrl: '/static/resources/zombie_small.png' })
            };

            $rootScope.$on('game.users.me', function (event, user) {
                if (user) user.loaded = true;
                angular.extend(User, user);
            });

            Zombie.query(function (zombies) {
                $log.info('Zombie loaded');
                leafletData.getMap().then(function (map) {
                    var randomFloatBetween = function (minValue, maxValue, precision) {
                        if (typeof(precision) == 'undefined') {
                            precision = 3;
                        }
                        return parseFloat(Math.min(minValue + (Math.random() * (maxValue - minValue)), maxValue)
                            .toFixed(precision));
                    };
                    var newZombieCords = function (curentLoc) {
                        var cl = [curentLoc.lat, curentLoc.lng];
                        var new_line_cords = [cl, cl];
                        new_line_cords.push([
                            curentLoc.lat + randomFloatBetween(-0.01, 0.01),
                            curentLoc.lng + randomFloatBetween(-0.01, 0.01)
                        ]);
                        return new_line_cords;
                    };

                    zombies.forEach(function (zombie) {
                        var zombieStartLineCords = newZombieCords(zombie.cords);
                        var zombieStartLine = L.polyline(zombieStartLineCords);
                        var marker = L.animatedMarker(zombieStartLine.getLatLngs(), {
                            keyboard: false,
                            icon: icons.zombie,
                            title: zombie.name,
                            zIndexOffset: 1000,
                            onEnd: function () {
                                var new_line_cords = newZombieCords(this.getLatLng());
                                this._i = 0;
                                var line_new = L.polyline(new_line_cords);
                                this.setLine(line_new.getLatLngs());
                                var mrk = this;
                                setTimeout(function () {
                                    mrk.start();
                                }, 1000);
                            }
                        });
                        map.addLayer(marker);
                    });
                });
            });

            leafletData.getMap().then(function (map) {
                map.on('click', function (e) {
                    if (Boom.selected) {
                        Boom.boom(e.latlng);
                        Boom.selected = false;
                    }
                });
            });

            $rootScope.$on('game.boom', function (event, data) {
                if (typeof data.balance != 'undefined') {
                    User.balance = parseInt(data.balance);
                }
                if (data.count) {
                    Notice.msg('Ваш кристал бомбанул! Мир стал чище на ' + data.count + ' ед. загрязнений!');
                } else {
                    Notice.warning('Вы бомбанули кристал, но никуда не попали!');
                }
            });
    }])


    .controller('QuestsCtrl', ['Quest', '$scope', 'User', function (Quest, $scope, User) {

        $scope.reloadQuest = function() {
            $scope.quests = Quest.query();
        };
        $scope.reloadMyQuest = function() {
            $scope.myQuests = Quest.my();
        };

        $scope.acceptQuest = function (quest) {
            var questIndex = $scope.quests.indexOf(quest);
            quest.$accept(function () {
                $scope.quests.splice(questIndex, 1);
                console.log('quest accepted');
            });
        };

        $scope.completeQuest = function (quest) {
            var questIndex = $scope.myQuests.indexOf(quest);
            var qPrice = quest.price;
            quest.$complete(function () {
                $scope.myQuests.splice(questIndex, 1);
                User.balance += parseInt(qPrice);
                console.log('quest completed');
            });
        };

        $scope.reloadQuest();
    }])

    .controller('NavCtrl', ['$scope', '$modal', function($scope, $modal) {
        $scope.openQuest = function () {
            $modal.open({templateUrl: 'static/partials/quests_window.html'});
        };
    }])
;