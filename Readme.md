Refere to this for starting: 
https://docs.aws.amazon.com/lambda/latest/dg/images-create.html

## Deploy 

Start by building the image
```
docker build -t voice-summary .   
```

Run locally
```
docker run -p 9000:8080 voice-summary 
```

Test locally with
```
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'
```


You will not need to upload this image to ECR to run it in lambda

If not already created, create a ECR repo
```
aws ecr create-repository --repository-name voice-summary-ecr-repository --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE
```

Then get credentials
```
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 967661707579.dkr.ecr.us-east-1.amazonaws.com
```

Before uploading the image to ECR you will need to tag the image
```
docker tag voice-summary:latest 967661707579.dkr.ecr.us-east-1.amazonaws.com/voice-summary-ecr-repository:latest
```

Now, push the image
```
docker push 967661707579.dkr.ecr.us-east-1.amazonaws.com/voice-summary-ecr-repository:latest
```