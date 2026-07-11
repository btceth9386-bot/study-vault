

# Creating a test environment
<a name="getting-started-with-aws-devops-agent-creating-a-test-environment"></a>

This guide provides hands-on tests to validate AWS DevOps Agent’s incident response functionality using sample architecture. Use this supplement if you want to test DevOps Agent before connecting your production systems.

## Prerequisites
<a name="prerequisites"></a>
+ AWS account with administrative access
+ AWS DevOps Agent Space created with and configured using the Auto create DevOps Agent role flow
+ For the EC2 test: an existing VPC with at least one subnet in the region where you'll deploy.

## Cost and safety overview
<a name="cost-and-safety-overview"></a>

### Cost protection
<a name="cost-protection"></a>
+ **EC2 test**: FREE (AWS Free Tier) or \~$0.02 for 2 hours
+ **Lambda test**: FREE (1M requests/month free tier)
+ **CloudWatch**: FREE (10 alarms, basic metrics included)
+ **Expected estimated total cost**: $0.00 - $0.05 for complete testing

### Safety features in these tests
<a name="safety-features-in-these-tests"></a>
+ **Auto-termination**: Built-in automatic shutdown
+ **Free Tier eligible**: Uses smallest instance types
+ **Limited scope**: Minimal, isolated test resources
+ **Easy cleanup**: Simple console steps to remove everything
+ **No production impact**: Completely separate test environment

## Set up your AWS account for testing
<a name="set-up-your-aws-account-for-testing"></a>

**Important**  
** Infrastructure resources need to be deployed in the AWS account where you created your DevOps Agent Space’s primary cloud account. The specific region does not matter.

1. Log into AWS Console: [https://console.aws.amazon.com](https://console.aws.amazon.com)

1. Ensure you're working in the same AWS account where your DevOps Agent Space is located

1. You can use any region for your testing resources

**Note**  
The 1:1 mapping between your DevOps Agent’s primary account and the test environment resources you are creating simplifies the test setup. You can easily extend your DevOps Agent Space to include secondary accounts and enable cross-account investigations.

## Choose your test
<a name="choose-your-test"></a>

You can run either test independently or both together:

### Test option A: EC2 CPU capacity test
<a name="test-option-a-ec2-cpu-capacity-test"></a>

**Purpose**: Validate AWS DevOps Agent’s ability to detect and investigate EC2 performance issues

**Estimated time**: 5 minutes setup \+ 10 minutes automatic execution

**Difficulty**: Fully automated (no manual steps required)

### Test option B: Lambda error rate test
<a name="test-option-b-lambda-error-rate-test"></a>

**Purpose**: Validate AWS DevOps Agent’s ability to detect and investigate Lambda function errors

**Estimated time**: 10 minutes setup \+ 2 minutes to trigger

**Difficulty**: Very easy

## Test option A: EC2 CPU capacity test
<a name="test-option-a-ec2-cpu-capacity-test"></a>

### Step 1: Deploy CloudFormation stack for EC2 test
<a name="step-1-deploy-cloudformation-stack-for-ec2-test"></a>

We'll use CloudFormation to create our test resources, which allows AWS DevOps Agent to properly track and investigate them.

1. **Navigate to CloudFormation**:

   1. In AWS Console, search for "CloudFormation" and choose **CloudFormation**

   1. Choose **Create stack** > **With new resources (standard)**

1. **Upload template**:

   1. Create a new local file called`AWS-DevOpsAgent-ec2-test.yaml`

   1. Copy and paste this CloudFormation template into the file:

      1. 

         ```
         AWSTemplateFormatVersion: '2010-09-09'
         Description: 'AWS DevOps Agent EC2 CPU Test Stack'
         Parameters:
           VpcId:
             Type: AWS::EC2::VPC::Id
             Description: ID of an existing VPC where the test instance will be launched.
           SubnetId:
             Type: AWS::EC2::Subnet::Id
             Description: ID of an existing subnet within the selected VPC. Choose a subnet that routes to an internet gateway if you plan to connect via SSH.
           MyIP:
             Type: String
             Description: Your current IP address for SSH access (find at https://whatismyipaddress.com)
             Default: '0.0.0.0/0'
         Resources:
           # Security Group for SSH access
           TestSecurityGroup:
             Type: AWS::EC2::SecurityGroup
             Properties:
               GroupDescription: AWS DevOps Agent beta testing security group
               VpcId: !Ref VpcId
               SecurityGroupIngress:
                 - IpProtocol: tcp
                   FromPort: 22
                   ToPort: 22
                   CidrIp: !Ref MyIP
                   Description: SSH access from your IP
               Tags:
                 - Key: Name
                   Value: AWS-DevOpsAgent-Test-SG
                 - Key: Purpose
                   Value: AWS-DevOpsAgent-Testing
           # Key Pair for SSH access
           TestKeyPair:
             Type: AWS::EC2::KeyPair
             Properties:
               KeyName: AWS-DevOpsAgent-test-key
               KeyType: rsa
               Tags:
                 - Key: Name
                   Value: AWS-DevOpsAgent-Test-Key
                 - Key: Purpose
                   Value: AWS-DevOpsAgent-Testing
           # IAM Role for Session Manager access
           SSMInstanceRole:
             Type: AWS::IAM::Role
             Properties:
               AssumeRolePolicyDocument:
                 Version: '2012-10-17'
                 Statement:
                   - Effect: Allow
                     Principal:
                       Service: ec2.amazonaws.com
                     Action: sts:AssumeRole
               ManagedPolicyArns:
                 - arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore
               Tags:
                 - Key: Name
                   Value: AWS-DevOpsAgent-Test-SSMRole
                 - Key: Purpose
                   Value: AWS-DevOpsAgent-Testing
           # Instance profile wrapping the SSM role
           SSMInstanceProfile:
             Type: AWS::IAM::InstanceProfile
             Properties:
               Roles:
                 - !Ref SSMInstanceRole
           # EC2 Instance for CPU testing
           TestInstance:
             Type: AWS::EC2::Instance
             Properties:
               InstanceType: t3.micro
               ImageId: '{{resolve:ssm:/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-6.1-x86_64}}'
               KeyName: !Ref TestKeyPair
               SubnetId: !Ref SubnetId
               SecurityGroupIds:
                 - !GetAtt TestSecurityGroup.GroupId
               IamInstanceProfile: !Ref SSMInstanceProfile
               InstanceInitiatedShutdownBehavior: terminate
               UserData:
                 Fn::Base64: !Sub |
                   #!/bin/bash
                   yum update -y
                   yum install -y htop
                   
                   # Create the CPU stress test script
                   cat > /home/ec2-user/cpu-stress-test.sh << 'EOF'
                   #!/bin/bash
                   echo "Starting AWS DevOpsAgent CPU Stress Test"
                   echo "Time: $(date)"
                   echo "Instance: $(curl -s http://169.254.169.254/latest/meta-data/instance-id)"
                   echo ""
                   
                   # Get number of CPU cores
                   CORES=$(nproc)
                   echo "CPU Cores: $CORES"
                   echo ""
                   
                   echo "Starting stress test (5 minutes)..."
                   echo "This will generate >70% CPU usage to trigger CloudWatch alarm"
                   echo ""
                   
                   # Create CPU load using yes command
                   echo "Starting CPU load processes..."
                   for i in $(seq 1 $CORES); do
                       (yes > /dev/null) &
                       CPU_PID=$!
                       echo "Started CPU load process $i (PID: $CPU_PID)"
                       echo $CPU_PID >> /tmp/cpu_test_pids
                   done
                   
                   # Auto-cleanup after 5 minutes
                   (sleep 300 && echo "Stopping CPU load processes..." && kill $(cat /tmp/cpu_test_pids 2>/dev/null) 2>/dev/null && rm -f /tmp/cpu_test_pids) &
                   
                   echo ""
                   echo "CPU load processes started for 5 minutes"
                   echo "Check CloudWatch for alarm trigger in 3-5 minutes"
                   EOF
                   
                   chmod +x /home/ec2-user/cpu-stress-test.sh
                   chown ec2-user:ec2-user /home/ec2-user/cpu-stress-test.sh
                   
                   # Create auto-shutdown script (safety mechanism)
                   cat > /home/ec2-user/auto-shutdown.sh << 'SHUTDOWN_EOF'
                   #!/bin/bash
                   echo "Auto-shutdown scheduled for 2 hours from now: $(date)"
                   sleep 7200
                   echo "Auto-shutdown executing at: $(date)"
                   sudo shutdown -h now
                   SHUTDOWN_EOF
                   
                   chmod +x /home/ec2-user/auto-shutdown.sh
                   nohup /home/ec2-user/auto-shutdown.sh > /home/ec2-user/auto-shutdown.log 2>&1 &
                   
                   echo "AWS DevOpsAgent test setup completed at $(date)" > /home/ec2-user/setup-complete.txt
               Tags:
                 - Key: Name
                   Value: AWS-DevOpsAgent-Test-Instance
                 - Key: Purpose
                   Value: AWS-DevOpsAgent-Testing
           # CloudWatch Alarm for CPU utilization
           CPUAlarm:
             Type: AWS::CloudWatch::Alarm
             Properties:
               AlarmName: AWS-DevOpsAgent-EC2-CPU-Test
               AlarmDescription: AWS-DevOpsAgent beta test - EC2 CPU utilization alarm
               MetricName: CPUUtilization
               Namespace: AWS/EC2
               Statistic: Average
               Period: 60
               EvaluationPeriods: 1
               Threshold: 70
               ComparisonOperator: GreaterThanThreshold
               Dimensions:
                 - Name: InstanceId
                   Value: !Ref TestInstance
               TreatMissingData: notBreaching
         Outputs:
           InstanceId:
             Description: EC2 Instance ID for testing
             Value: !Ref TestInstance
           
           SecurityGroupId:
             Description: Security Group ID
             Value: !GetAtt TestSecurityGroup.GroupId
             
           AlarmName:
             Description: CloudWatch Alarm Name
             Value: !Ref CPUAlarm
             
           SSHCommand:
             Description: SSH command to connect to instance
             Value: !Sub 'ssh -i "AWS-DevOpsAgent-test-key.pem" ec2-user@${TestInstance.PublicDnsName}'
         ```

   1. In the CloudFormation console, select **Upload a template file**

   1. Choose **Choose file**

   1. Select the `AWS-DevOpsAgent-ec2-test.yaml` file

   1. Choose **Next**

1. **Configure stack**:

   1. **Stack name**:`AWS-DevOpsAgent-EC2-Test`

   1. **Parameters**:

      1. **VpcId**: Select an existing VPC from the dropdown.

      1. **SubnetId**: Select a subnet within the VPC you chose. For SSH access, the subnet must route to an internet gateway, and the instance must have a public IPv4 address associated. Otherwise, the `SSHCommand` output will be empty and SSH connections won't succeed.

      1. **MyIP**: Leave as default `0.0.0.0/0` (you can secure this later if needed)

   1. Choose **Next**

1. **Configure stack options**:

   1. Leave defaults, choose **Next**

1. **Review and create**:

   1. Check **I acknowledge that AWS CloudFormation might create IAM resources**

   1. Choose **Submit**

1. **Wait for completion**:

   1. Stack creation takes 3-5 minutes

   1. Status will change from`CREATE_IN_PROGRESS`to`CREATE_COMPLETE`

   1. **Important**: Your EC2 instance is now part of a CloudFormation stack that AWS DevOpsAgent can track\!

#### Optional: Secure SSH access (only if you plan to connect to the instance)
<a name="optional-secure-ssh-access-only-if-you-plan-to-connect-to-the-instance"></a>

Skip this step if you just want to run the automated test

1. **Locate the security group**:

   1. In AWS Console, go to **CloudFormation** and select the `AWS-DevOpsAgent-EC2-Test` stack

   1. Open the **Outputs** tab and copy the value of `SecurityGroupId` (starts with `sg-`)

   1. Go to **EC2** → **Security Groups** and paste the ID into the search bar to open the security group

1. **Update SSH rule**:

   1. Select the security group → **Inbound rules** tab → **Edit inbound rules**

   1. Find the SSH rule (port 22)

   1. Change source from`0.0.0.0/0`to your IP:`[YOUR_IP]/32`

   1. Get your IP from [https://whatismyipaddress.com](https://whatismyipaddress.com/)

   1. Choose **Save rules**

### Step 2: Wait for automatic test execution
<a name="step-2-wait-for-automatic-test-execution"></a>

1. **Automatic test execution**:
   + The CPU stress test will **automatically start 5 minutes** after instance launch
   + No manual intervention required - just wait, the test runs completely in the background

1. **Monitor the test**:
   + Instance boots and prepares the test automatically
   + The script will run for 5 minutes and generate >70% CPU usage
   + CloudWatch alarm should trigger within 8-10 minutes total (5 min delay \+ 3-5 min for alarm)

1. **Optional: Manual re-run** (for additional testing):
   + Connect to your instance: EC2 console →`AWS-DevOpsAgent-Test-Instance`→ **Connect** → **Session Manager**
   + Run the stress test again:`./cpu-stress-test.sh`
   + Perfect for testing AWS DevOpsAgent's response multiple times

## Test option B: Lambda error rate test
<a name="test-option-b-lambda-error-rate-test"></a>

### Step 1: Deploy CloudFormation stack for Lambda test
<a name="step-1-deploy-cloudformation-stack-for-lambda-test"></a>

1. **Navigate to CloudFormation**:

   1. In AWS Console, go to **CloudFormation**

   1. Choose **Create stack** → **With new resources (standard)**

1. **Upload template**:

   1. Create a new local file called`AWS-DevOpsAgent-lambda-test.yaml`

   1. Copy and paste this CloudFormation template into the file:

      1. 

         ```
         AWSTemplateFormatVersion: '2010-09-09'
         Description: 'AWS DevOpsAgent Lambda Error Test Stack'
         Resources:
           # IAM Role for Lambda function
           LambdaExecutionRole:
             Type: AWS::IAM::Role
             Properties:
               RoleName: AWS-DevOpsAgentLambdaTestRole
               AssumeRolePolicyDocument:
                 Version: '2012-10-17'
                 Statement:
                   - Effect: Allow
                     Principal:
                       Service: lambda.amazonaws.com
                     Action: sts:AssumeRole
               ManagedPolicyArns:
                 - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
               Tags:
                 - Key: Name
                   Value: AWS-DevOpsAgent-Lambda-Test-Role
                 - Key: Purpose
                   Value: AWS-DevOpsAgent-Testing
           # Lambda function that generates errors
           TestLambdaFunction:
             Type: AWS::Lambda::Function
             Properties:
               FunctionName: AWS-DevOpsAgent-test-lambda
               Runtime: python3.12
               Handler: index.lambda_handler
               Role: !GetAtt LambdaExecutionRole.Arn
               Code:
                 ZipFile: |
                   import json
                   import random
                   import time
                   from datetime import datetime
                   def lambda_handler(event, context):
                       print(f"AWS DevOpsAgent Test Lambda - {datetime.now()}")
                       print(f"Event: {json.dumps(event)}")
                       
                       # Intentionally generate errors for testing
                       error_scenarios = [
                           "Simulated database connection timeout",
                           "Test API rate limit exceeded", 
                           "Intentional validation error for AWS DevOpsAgent testing"
                       ]
                       
                       # Always throw an error for testing purposes
                       error_message = random.choice(error_scenarios)
                       print(f"Generating test error: {error_message}")
                       
                       # This will create a Lambda error that CloudWatch will detect
                       raise Exception(f"AWS DevOpsAgent Test Error: {error_message}")
               Description: AWS DevOpsAgent beta test function - intentionally generates errors
               Timeout: 30
               Tags:
                 - Key: Name
                   Value: AWS-DevOpsAgent-Test-Lambda
                 - Key: Purpose
                   Value: AWS-DevOpsAgent-Testing
           # CloudWatch Alarm for Lambda errors
           LambdaErrorAlarm:
             Type: AWS::CloudWatch::Alarm
             Properties:
               AlarmName: AWS-DevOpsAgent-Lambda-Error-Test
               AlarmDescription: AWS-DevOpsAgent beta test - Lambda error rate alarm
               MetricName: Errors
               Namespace: AWS/Lambda
               Statistic: Sum
               Period: 60
               EvaluationPeriods: 1
               Threshold: 0
               ComparisonOperator: GreaterThanThreshold
               Dimensions:
                 - Name: FunctionName
                   Value: !Ref TestLambdaFunction
               TreatMissingData: notBreaching
         Outputs:
           LambdaFunctionName:
             Description: Lambda Function Name for testing
             Value: !Ref TestLambdaFunction
             
           LambdaFunctionArn:
             Description: Lambda Function ARN
             Value: !GetAtt TestLambdaFunction.Arn
             
           AlarmName:
             Description: CloudWatch Alarm Name
             Value: !Ref LambdaErrorAlarm
             
           TestCommand:
             Description: AWS CLI command to test the function
             Value: !Sub 'aws lambda invoke --function-name ${TestLambdaFunction} --payload "{\"test\":\"AWS DevOpsAgent validation\"}" response.json'
         ```

   1. In the CloudFormation console, select **Upload a template file**

   1. Choose **Choose file**

   1. Select the `AWS-DevOpsAgent-lambda-test.yaml` file

   1. Choose **Next**

1. **Configure stack**:

   1. **Stack name**:`AWS-DevOpsAgent-Lambda-Test`

   1. Choose **Next**

1. **Configure stack options**:

   1. Leave defaults, choose **Next**

1. **Review and create**:

   1. Check **I acknowledge that AWS CloudFormation might create IAM resources**

   1. Choose **Submit**

1. **Wait for completion**:

   1. Stack creation takes 2-3 minutes

   1. Status will change to`CREATE_COMPLETE`

### Step 2: Trigger Lambda errors
<a name="step-2-trigger-lambda-errors"></a>

1. **Navigate to Lambda console**:

   1. Go to **AWS Lambda** console

   1. Find your function`AWS-DevOpsAgent-test-lambda`

1. **Test the function**:

   1. Choose **Test** tab

   1. Choose **Create new event**

   1. **Event name**:`AWS-DevOpsAgent-test-event`

   1. Use this JSON payload:

      1. 

         ```
         {
         "test": "AWS DevOpsAgent validation",
         "timestamp": "2024-01-01T00:00:00Z"
         }
         ```

   1. Choose **Save**

1. **Generate errors**:

   1. Choose **Test** button 3 times (wait 10 seconds between each)

   1. Each test will generate an intentional error

   1. **CloudWatch alarm** should trigger within 2-3 minutes

   1. **AWS DevOpsAgent** should now be able to detect the alarm with an **Investigation** in the **Operator app** which you will set up next.

## Validate AWS DevOps Agent detection
<a name="validate-aws-devops-agent-detection"></a>

### Step 1: Sanity check CloudWatch alarms (optional)
<a name="step-1-sanity-check-cloudwatch-alarms-optional"></a>

This step is for ensuring that the above tests are now in an alarm state.

**For EC2 Test:**
+ In CloudWatch console, go to **Alarms**
+ **Wait 3-5 minutes** after starting the stress test
+ Your alarm should show **In alarm** state
+ **If still "OK"**: Wait another 2-3 minutes (CloudWatch metrics can be delayed)

**For Lambda Test:**
+ Check`AWS-DevOpsAgent-Lambda-Error-Test`alarm
+ Should show **In alarm** within 2-3 minutes of running tests

### Step 2: Start a AWS DevOps Agent Investigation
<a name="step-2-start-a-aws-devops-agent-investigation"></a>

1. Open your **AWS DevOps Agent AgentSpace**

1. Choose **Admin access**. This will open the DevOps Agent Space web app in a new window

1. Choose the **Start Investigation** button on the right side of the screen

1. Complete the following form:

   1. **Investigation details:** Describe the investigation you'd like to run. Include any details you can about the investigation goals, areas to explore, or relevant information.

   1. **Investigation starting point**: Describe the information you'd like to start the investigation from. You can mention an alarm, metric, log snippet, or anything else to give DevOps Agent a starting point to work from. In this case, provide a summary of the alarms you just created.

   1. **Date and time of incident** (ISO 8601 preferred): YYYY-MM-DDTHH:MMZ

   1. **Name your investigation:** example: `Oncall_investigation_1:2025-10-27`

   1. **AWS Account ID** for the incident

   1. **Region ** where the incident occurred

   1. **Priority** - AWS DevOpsAgent allows for two concurrent investigations. The Priority allows for you to define the order of execution of your investigations.

1. Choose Investigate to launch the investigation.

1. Choose your Investigation listed in the dashboard. You will be taken to the Investigation Details screen where you can view the granular steps that DevOps Agent is taking.

### Expected Results
<a name="expected-results"></a>

#### EC2 test results:
<a name="ec2-test-results"></a>
+ Detects EC2 CPU alarm
+ Identifies root cause: "CPU stress testing workload"
+ Shows timeline: Stress test → CPU spike → Alarm
+ Provides recommendations for monitoring and scaling

**Lambda test results:**
+ Detects Lambda error rate spike
+ Identifies root cause: "Intentional test exceptions"
+ Shows timeline: Function invocations → Errors → Alarm
+ Provides recommendations for error handling and monitoring

## Cleanup instructions
<a name="cleanup-instructions"></a>

### Cleanup test A (EC2 test)
<a name="cleanup-test-a-ec2-test"></a>

#### Automatic cleanup
<a name="automatic-cleanup"></a>
+ Instance will auto-terminate after 2 hours (built into CloudFormation template)

#### Manual cleanup (immediate)
<a name="manual-cleanup-immediate"></a>

1. **Delete CloudFormation Stack**:

   1. Go to CloudFormation console

   1. Select`AWS-DevOpsAgent-EC2-Test`stack

   1. Choose **Delete**

   1. Confirm deletion

   1. **This will automatically delete all resources**: EC2 instance, security group, key pair, and CloudWatch alarm

### Cleanup test B (Lambda test)
<a name="cleanup-test-b-lambda-test"></a>

1. **Delete CloudFormation Stack**:

   1. Go to CloudFormation console

   1. Select`AWS-DevOpsAgent-Lambda-Test`stack

   1. Choose **Delete**

   1. Confirm deletion

   1. **This will automatically delete all resources**: Lambda function, IAM role, and CloudWatch alarm

## Troubleshooting
<a name="troubleshooting"></a>

### Common issues
<a name="common-issues"></a>

#### "Can't connect to EC2 instance"
<a name="cant-connect-to-ec2-instance"></a>
+ **Check Security Group**: Ensure SSH (port 22) is open to your IP
+ **Check Key Permissions**: Run`chmod 400 AWS-DevOpsAgent-test-key.pem`
+ **Verify Public IP**: Instance must have public IP assigned
+ **Wait for Instance**: Ensure instance is in "Running" state

#### "Alarm not triggering"
<a name="alarm-not-triggering"></a>
+ **Wait for Metrics**: CloudWatch metrics can take 2-5 minutes to appear
+ **Check CPU Load**: SSH to instance and run`top`to verify CPU >70%
+ **Verify Stress Test**: Run`ps aux | grep yes`to see if load processes are running
+ **Extended Wait**: Sometimes takes up to 7-8 minutes for first alarm trigger

## Test validation
<a name="test-validation"></a>

Your AWS DevOp Agent testing is successful when:

### Technical validation
<a name="technical-validation"></a>
+ **Investigation Accuracy**: The results of the EC2 test should correctly indicate that the alarm was triggered due to CPU load. The result of the Lambda test should indicate that this was an intentional failure.
+ **Timeline Accuracy**: Correct sequence of events shown
+ **Recommendation Quality**: Actionable suggestions provided