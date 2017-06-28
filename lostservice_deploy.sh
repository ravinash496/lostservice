#!/usr/bin/env bash

# Push only if it's not a pull request
if [ -z "$TRAVIS_PULL_REQUEST" ] || [ "$TRAVIS_PULL_REQUEST" == "false" ]; then
  # Push only if we're testing the master branch
  if [ "$TRAVIS_BRANCH" == "master" ]; then

    # Record docker version.
    docker --version

    # Build the image.
    docker build -t $IMAGE_NAME .

    # This is needed to login on AWS and push the image on ECR
    eval $(aws ecr get-login --region $AWS_DEFAULT_REGION)

    # Push up to ECR container registry.
    echo "Pushing $IMAGE_NAME:latest"
    docker tag $IMAGE_NAME:latest "$REMOTE_IMAGE_URL:latest"
    docker push "$REMOTE_IMAGE_URL:latest"
    echo "Pushed $IMAGE_NAME:latest"

    echo "Deploying $TRAVIS_BRANCH on $TASK_DEFINITION"
    ./ecs-deploy.sh -c $CLUSTER -n $SERVICE -i $REMOTE_IMAGE_URL:latest -D 1 --max-definitions 4 -t 120
    exit $?
  else
    echo "Skipping deploy because branch is not 'master'"
  fi
else
  echo "Skipping deploy because it's a pull request"
fi