import json
import boto3

def handler(event, context):

    result = None
    eventDetails = json.loads(json.dumps(event))["detail"]
    print(eventDetails)
    tags = [
        {'Key': 'Owner', 'Value': eventDetails["userIdentity"]["principalId"]},
        {'Key': 'OwnerARN', 'Value': eventDetails["userIdentity"]["arn"]},
        {'Key': 'Region', 'Value': eventDetails["awsRegion"]}
    ]
        
    # Check if eventSource is s3
    if (eventDetails["eventSource"] == 's3.amazonaws.com' and
        eventDetails["eventName"] == 'CreateBucket'):
        
        # Run tag_s3 function
        result = tag_s3(eventDetails["requestParameters"]["bucketName"], tags)
    # Check if eventSource is ec2
    elif eventDetails["eventSource"] == "ec2.amazonaws.com":
        
        # Run tag_ec2 function
        result = tag_ec2(eventDetails["eventName"], eventDetails["responseElements"],tags)
    # Check if eventSource is CreateTrail
    elif (eventDetails["eventSource"] == "cloudtrail.amazonaws.com" and
        eventDetails["eventName"] == 'CreateTrail'):
        print("cloudtrail")
        # Run tag_trail function
        result = tag_trail(eventDetails["responseElements"],tags)
    # Check if eventSource is iam
    elif eventDetails["eventSource"] == "iam.amazonaws.com":
        print("iam")
        # Run tag_iam function
        result = tag_iam(eventDetails["eventName"],eventDetails["responseElements"],tags)
    # Check if eventSource is lambda
    elif eventDetails["eventSource"] == "lambda.amazonaws.com":
        print("lambda")
        # Run tag_lambda function
        result = tag_lambda(eventDetails["eventName"],eventDetails["responseElements"],tags)
    
    # print output
    print(result)

# Tag All EC2 Resources
def tag_ec2(eventName, responseElements, tags):
    ec2Client = boto3.client('ec2')
    
    ids = []

    if eventName == "RunInstances":
        #loop through instances"
        for item in responseElements["instancesSet"]["items"]:
            ids.append(item['instanceId'])
        #base = ec2Client.instances.filter(InstanceIds=ids)
        instances = ec2Client.describe_instances(
            InstanceIds=[ids]
        )
        #loop through connected resources"
        for instance in instances:
            for vol in instance.volumes.all():
                ids.append(vol.id)
            for eni in instance.network_interfaces:
                ids.append(eni.id)
    elif eventName == 'CreateVolume':
        ids.append(responseElements['volumeId'])
    elif eventName == 'CreateImage':
        ids.append(responseElements['imageId'])
    elif eventName == 'CreateSnapshot':
        ids.append(responseElements['snapshotId'])
    elif eventName == 'CreateInternetGateway':
        ids.append(responseElements['internetGateway']['internetGatewayId'])
    elif eventName == 'CreateSecurityGroup':
        ids.append(responseElements['groupId'])
    elif eventName == 'CreateNetworkAcl':
        ids.append(responseElements['networkAcl']['networkAclId'])
    elif eventName == 'CreateVpc':
        ids.append(responseElements['vpc']['vpcId'])
    if ids:
        return ec2Client.create_tags(
                    Resources=ids,
                    Tags=tags
                )
    return "No IDs"

# Tag S3 Bucket
def tag_s3(bucketName, tags):
    s3Client = boto3.client('s3')

    return s3Client.put_bucket_tagging(
        Bucket=bucketName,
        Tagging={
            'TagSet': tags
            }
    )

# Tag CloudTrail trail
def tag_trail(responseElements, tags):
    cloudtrailClient = boto3.client('cloudtrail')

    print(responseElements)
    return cloudtrailClient.add_tags(
        ResourceId = responseElements['trailid'],
        TagsList = tags
    )

# Tag IAM Roles and Policies
def tag_iam(eventName, responseElements, tags):
    iamClient = boto3.client('iam')
    
    print(responseElements)
    if eventName == 'CreateRole':
        print("CreateRole")
        
        return iamClient.tag_role(
            RoleName = responseElements['role']['roleName'],
            Tags = tags
        )

# Tag Lambda resources
def tag_lambda(eventName, responseElements, tags):
    lambdaClient = boto3.client('lambda')
    
    print(responseElements)
    if eventName == 'CreateFunction20150331':
        print("CreateFunction20150331")
        
        return lambdaClient.tag_resource(
            RoleName = responseElements['functionArn'],
            Tags = tags
        )