'use strict';

/* Services */


angular.module('ecoGame.services', []).
    //Quests Resources
    factory('Quest', ['$resource',
        function($resource) {
            return $resource('quests/:questId/:status', {}, {
                accept: {method:'POST', params: {questId: '@id', status: 'accept'}},
                complete: {method:'POST', params: {questId: '@id', status: 'complete'}},
                my: {method:'GET', params: {status: 'my'}, isArray: true}
            });
        }
    ]).
    value('version', '0.1');