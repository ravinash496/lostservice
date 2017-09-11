//File paths to the various newmane files for testing.
var testBase = './tests/postman/';
var testFilePath = testBase + 'Tests/';
var iterationFilePath = testBase + 'PostmanData/';
var envFilePath = testBase + 'Environments/';


var fs = require('fs'),         // https://nodejs.org/api/fs.html
    newman = require('newman'),
    path = require('path'); //https://www.npmjs.com/package/newman

//This function will check in the PostmanData folder to see if the file for iterating data exists.
//Returns a file name, or empty string.
function checkIterationFile(file, iterationFile) {
   var fileNameOnly = file.split('.').slice();
    return new Promise((resolve, reject) => {
        if(fs.existsSync(iterationFilePath + fileNameOnly[0] + '_Data.json')) {
            iterationFile = iterationFilePath + fileNameOnly[0] + '_Data.json';
            resolve(iterationFile);
        } else {
            iterationFile = '';
            resolve(iterationFile);
        }
    });
}

var getFiles = function () {fs.readdir(testFilePath, (err, files) => {
    //TODO: Assign environment file.
    files.forEach(file => {
        //Run our promise for the iterationData
        checkIterationFile(file)
        .then(function (res) {
            newman.run({
              collection: testFilePath + file,
              iterationData: res,
              reporters: 'cli',
              timeoutRequest: 10000,
              bail: true
        }, function (err) {
            if (err) { 
                throw err;
                console.log('i hit an error boss');
                process.exit
            }
            });
        })
        .catch(function (error) {
            console.log(error.message);
        });
    });
 });
}

getFiles();