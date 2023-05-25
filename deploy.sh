#!/bin/bash
set -euo pipefail

DOCKER_IMAGE_NAME="voice-summary"
DOCKERFILE_PATH="./container-images/Dockerfile"
AWS_REGION="ap-south-1"
ACCOUNT_ID="967661707579"
ECR_REPOSITORY_NAME="voice-summary-ecr-repository"
SAM_STACK_NAME="voice-summary-stack"
SAM_TEMPLATE_PATH="./template.yaml"

handle_error() {
  echo "Error on line $1"
  exit 1
}

trap 'handle_error $LINENO' ERR

check_variables() {
  if [[ -z "$DOCKER_IMAGE_NAME" || -z "$DOCKERFILE_PATH" || -z "$AWS_REGION" || -z "$ACCOUNT_ID" || -z "$ECR_REPOSITORY_NAME" || -z "$SAM_STACK_NAME" || -z "$SAM_TEMPLATE_PATH" ]]; then
    printf "One or more required variables are not set. Exiting\n"
    exit 1
  fi
}

create_repository() {
  printf "Creating ECR repository $ECR_REPOSITORY_NAME in region $AWS_REGION\n"
  REPO=$(aws ecr describe-repositories --repository-names $ECR_REPOSITORY_NAME --region $AWS_REGION 2> /dev/null)
  if [ -z "$REPO" ]; then
    aws ecr create-repository --repository-name $ECR_REPOSITORY_NAME --region "$AWS_REGION" --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE
    printf "Repository created successfully.\n"
  else
    printf "Repository already exists.\n"
  fi
}


ecr_login() {
  printf "Logging into ECR repository - $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com\n"
  aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
  printf "Logged in successfully!\n"
}

build_and_push_image() {
  printf "Building Docker image $DOCKER_IMAGE_NAME from $DOCKERFILE_PATH\n"
  docker build -t $DOCKER_IMAGE_NAME --platform linux/amd64 -f $DOCKERFILE_PATH .
  printf "Docker image built successfully!\n"

  docker tag $DOCKER_IMAGE_NAME:latest $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME:latest
  printf "Tagged Docker image $DOCKER_IMAGE_NAME as $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME:latest\n"

  printf "Pushing $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME:latest to ECR repository...\n"
  docker push $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME:latest
  printf "Pushed successfully!\n"
}

build_deploy_sam_stack() {
  printf "Deploying SAM stack $SAM_STACK_NAME using $SAM_TEMPLATE_PATH...\n"
  sam build --cached --parallel
  sam deploy --region $AWS_REGION --parameter-overrides ECRRepositoryName=$ECR_REPOSITORY_NAME --capabilities CAPABILITY_NAMED_IAM  --stack-name $SAM_STACK_NAME --template-file $SAM_TEMPLATE_PATH --image-repository "$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME" --no-confirm-changeset
  printf "Deployed successfully!\n"
}



check_variables
create_repository
ecr_login
build_and_push_image
build_deploy_sam_stack
