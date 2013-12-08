'use strict';

/* Services */

angular.module('ecoGame.services', []).
    //Quests Resources
    factory('Quest', ['$resource', function ($resource) {
        return $resource('quests/:questId/:status', {}, {
            accept: {method: 'POST', params: {questId: '@id', status: 'accept'}},
            complete: {method: 'POST', params: {questId: '@id', status: 'complete'}},
            my: {method: 'GET', params: {status: 'my'}, isArray: true}
        });
    }])

    .value('User', {loaded: false, name: '', balance: 0, avatar: 0 })

    .factory('Zombie', ['$resource', function ($resource) {
        return $resource('zombies', {}, {});
    }])

    //Game socket service
    .factory('GameStream', ['$rootScope', 'Notice', function ($rootScope, Notice) {
        // We return this object to anything injecting our service
        var Service = {};
        var ws = new ReconnectingWebSocket("ws://127.0.0.1:8001/stream");

        ws.onopen = function () {
            console.log("Socket has been opened!");
        };

        ws.onmessage = function (message) {
            var data = JSON.parse(message.data);
            console.log("Received data from websocket: ", data);
            if (data['event']) {
                if (data['event'] == 'notice') {
                    Notice.add(data['data'].msg, data['data'].type);
                } else {
                    $rootScope.$emit('game.' + data['event'], data['data']);
                }
            }
        };

        Service.sendRequest = function (action, data) {
            var sendData = data ? data : null;
            var request = { type: action, 'data': sendData };
            console.log('Sending ws request', request);
            ws.send(JSON.stringify(request));
        };

        return Service;
    }])


    .factory('Notice', ['$rootScope', function ($rootScope) {
        $rootScope.notifications = false;
        var Service = {
            messages: [],
            add: function (message, type) {
                Service.messages.push({text: message, type: "alert-" + type});
                $rootScope.notifications = Service.messages;
                $rootScope.$emit('notification.update');
            },
            msg: function(msg) {
                Service.add(msg, 'success')
            },
            info: function(msg) {
                Service.add(msg, 'info')
            },
            error: function(msg) {
                Service.add(msg, 'danger')
            },
            warning: function(msg) {
                Service.add(msg, 'warning')
            }
        };

        return Service;
    }])

;