var async = require('async'), // https://www.npmjs.com/package/async
    newman = require('newman');

async.series([
  function (next) {
    newman.run({
      collection: './tests/Postman/Tests/ECRF_Collection_Test.postman_collection.json',
      reporters: 'cli',
      bail: true
    }, next);
  },
  function (next) {
    newman.run({
      collection: './tests/Postman/Tests/TestingPostman.postman_collection.json',
      reporters: 'cli',
      bail: true
    }, next);
  }
], process.exit);