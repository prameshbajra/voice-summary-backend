Refere to this for starting: 
https://docs.aws.amazon.com/lambda/latest/dg/images-create.html

## Deploy 

> PREFER NOT RUNNING COMMANDS FROM THIS README.

> Note: If you want to deploy the the image from here you will have to make some path changes on the dockerfile. Or just run it, you will see error and you will figure it out :D

Before starting make sure you are in `container-images` directory in your terminal.

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
aws ecr create-repository --repository-name voice-summary-ecr-repository --region ap-south-1 --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE
```

Then get credentials
```
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 967661707579.dkr.ecr.ap-south-1.amazonaws.com
```

Before uploading the image to ECR you will need to tag the image
```
docker tag voice-summary:latest 967661707579.dkr.ecr.ap-south-1.amazonaws.com/voice-summary-ecr-repository:latest
```

Now, push the image
```
docker push 967661707579.dkr.ecr.ap-south-1.amazonaws.com/voice-summary-ecr-repository:latest
```


