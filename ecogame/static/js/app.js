'use strict';

//Declare app level module which depends on filters, and services
angular.module('ecoGame', [
  'ngRoute',
  'ngResource',
//  'ngSanitize',
  'ecoGame.filters',
  'ecoGame.services',
  'ecoGame.directives',
  'ecoGame.controllers'
]).config(['$routeProvider', '$httpProvider', function($routeProvider, $httpProvider) {
  $routeProvider.when('/map', {templateUrl: 'static/partials/map.html', controller: 'MapsCtrl'});
  $routeProvider.when('/quests', {templateUrl: 'static/partials/quests.html', controller: 'QuestsCtrl'});
  $routeProvider.when('/my/quests', {templateUrl: 'static/partials/quests_my.html', controller: 'MyQuestsCtrl'});
  $routeProvider.otherwise({redirectTo: '/map'});

  $httpProvider.defaults.xsrfCookieName = '_xsrf';
  $httpProvider.defaults.xsrfHeaderName = 'X-XSRFToken';
}]);
