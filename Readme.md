# How to get started?

Make sure you have these things first:
1. Docker running
2. AWS CLI configured properly.


After which you can simply,

Run `chmod +x deploy.sh` before you start.
Then run `./deploy.sh`. Done !!


## Things to note

- Sometimes you might get `ROLLBACK_COMPLETE` error which will not allow you to deploy any further. In that case you will have to delete the stack and redeploy it. Weird, I know. It is what it is. You can delete the stack using this command : `sam delete --stack-name voice-summary-stack` or this would also work `aws cloudformation delete-stack --stack-name voice-summary-stack`. Then you can check if the stack is deleted by this command : `aws cloudformation describe-stacks --stack-name voice-summary-stack`.