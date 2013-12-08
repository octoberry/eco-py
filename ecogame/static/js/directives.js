'use strict';

/* Directives */


angular.module('ecoGame.directives', [])
    .directive('notifications', ['$rootScope', '$timeout', 'Notice', function($rootScope, $timeout, Notice) {
        return {
            restrict: 'E',
            template: '<div ng-repeat="msg in notifications" ng-animate="notice" class="alert" ng-class="msg.type">{{ msg.text }}</div>',

            link: function(scope) {
                $rootScope.$on('notification.update', function () {
                    scope.notifications = Notice.messages;
                    Notice.messages.forEach(function(msg) {
                        if (!msg.deleted) {
                            msg.deleted = true;
                            //auto-hide messages
                            $timeout(function() {
                                var index = Notice.messages.indexOf(msg);
                                index != -1 && Notice.messages.splice(index, 1);
                            }, 2500);
                        }
                    });
                });
            }
        };

    }])
;