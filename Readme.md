## Deploy 

Uploading the image to ECR which then can be used in AWS App Runner

Make sure you build the image locally first using:
```
docker build -t voice-backend:latest .
```

Then in order to upload it to a ECR repository you will have to tag it first
```
docker tag voice-backend:latest 967661707579.dkr.ecr.us-east-1.amazonaws.com/voice-summary:latest
```

And finally it will be ready to be uploaded to ECR
```
docker push 967661707579.dkr.ecr.us-east-1.amazonaws.com/voice-summary:latest
```