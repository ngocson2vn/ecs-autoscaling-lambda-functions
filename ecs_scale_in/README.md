## Lambda functions scale in ECS clusters Staging and Production
### Description
#### Lambda functions:
```
functions:
  drain_ec2instance:
    handler: scale_handler.drain_ec2instance
    events:
      - schedule: rate(15 minutes)
  terminate_drained_ec2instances:
    handler: scale_handler.terminate_drained_ec2instances
    events:
      - schedule: rate(15 minutes)
```
#### `drain_ec2instance`
This function checks `SCALE_IN_THRESHOLD` periodically. If the threshold crossed, it will change state of the oldest instance in AutoScalingGroup to DRAINING state. Later on, the lambda function `terminate_drained_ec2instances` will check and remove drained instances from the AutoScalingGroup.

### Setup
```
# Install nvm
curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.33.2/install.sh | bash
nvm install node
nvm use node

#Install serverless package
npm install -g serverless
```

### Deploy:
```
pip install -t vendored/ -r requirements.txt
serverless deploy --stage staging
serverless deploy --stage production
```

### Set environment variables for lambda functions
```
STAGE=Staging or Production
SCALE_IN_THRESHOLD=60
DATAPOINT_PERIOD=10
DATAPOINT_COUNT=3
```
