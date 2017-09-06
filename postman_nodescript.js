var async = require('async'), // https://www.npmjs.com/package/async
    newman = require('newman');

async.series([
  function (next) {
    newman.run({
      collection: './tests/postman/Tests/ECRF_Collection_Test.postman_collection.json',
      reporters: 'cli',
      timeoutRequest: 10000,
      bail: true
    }, next);
  },
  function (next) {
    newman.run({
      collection: './tests/postman/Tests/TestingPostman.postman_collection.json',
      reporters: 'cli',
      timeoutRequest: 10000,
      bail: true
    }, next);
  },
  /*function (next) {
    newman.run({
      collection: './tests/postman/Tests/SR_Geodetic_FindService_ByValue.postman_collection.json',
      iterationData: './tests/postman/PostmanData/SR_Geodetic_FindService_ByValue_Data.json',
      reporters: 'cli',
      timeoutRequest: 10000,
      bail: true
    }, next);
  },*/
  function (next) {
    newman.run({
      collection: './tests/postman/Tests/SR_Geodetic_ListServicesByLocation.postman_collection.json',
      iterationData: './tests/postman/PostmanData/SR_Geodetic_ListServicesByLocation_data.json',
      reporters: 'cli',
      timeoutRequest: 10000,
      bail: true
    }, next);
  },
  function (next) {
    newman.run({
      collection: './tests/postman/Tests/SR_ListServices.postman_collection.json',
      iterationData: './tests/postman/PostmanData/SR_ListServices_sos_data.json',
      reporters: 'cli',
      timeoutRequest: 10000,
      bail: true
    }, next);
  },
  function (next) {
    newman.run({
      collection: './tests/postman/Tests/SR_ListServices.postman_collection.json',
      iterationData: './tests/postman/PostmanData/SR_ListServices_responder_data.json',
      reporters: 'cli',
      timeoutRequest: 10000,
      bail: true
    }, next);
  }
]);
