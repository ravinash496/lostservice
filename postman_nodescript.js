var async = require('async'), // https://www.npmjs.com/package/async
    newman = require('newman');

async.series([
  function (next) {
    newman.run({
      collection: './tests/postman/TestingPostman.postman_collection.json',
      reporters: 'cli',
      timeoutRequest: 10000,
      bail: true
    }, next);
  },
  function (next) {
    newman.run({
      collection: './tests/postman/ECRF_Collection_Test.postman_collection.json',
      reporters: 'cli',
      timeoutRequest: 10000,
      bail: true
    }, next);
  }
], process.exit);
