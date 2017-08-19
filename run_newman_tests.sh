#!/bin/bash

echo "executing postman/newman tests"
node ./postman_nodescript.js

rc=${PIPESTATUS[0]};
if [[ $rc != 0 ]]; then exit $rc; fi


