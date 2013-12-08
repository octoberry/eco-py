'use strict';

//Declare app level module which depends on filters, and services
angular.module('ecoGame', [
  'ngRoute',
  'ngResource',
  'ui.bootstrap',
//  'ngSanitize',
  'ecoGame.filters',
  'ecoGame.services',
  'ecoGame.directives',
  'ecoGame.controllers',
  'ecoGame.Pollution',
  'ecoGame.Robot',
  'ecoGame.Boom'
]).config(['$routeProvider', '$httpProvider', function($routeProvider, $httpProvider) {
  $routeProvider.when('/map', {templateUrl: 'static/partials/map.html', controller: 'MapsCtrl'});
  $routeProvider.otherwise({redirectTo: '/map'});

  $httpProvider.defaults.xsrfCookieName = '_xsrf';
  $httpProvider.defaults.xsrfHeaderName = 'X-XSRFToken';
}]);
