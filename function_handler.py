import json
import boto3

def handler(event, context):
    #eventJson = json.loads(event)
    result = None
    eventJson = json.loads(json.dumps(event))
    print(eventJson)
    tags = [
        {'Key': 'Owner', 'Value': eventJson["userIdentity"]["principalId"]},
        {'Key': 'OwnerARN', 'Value': eventJson["userIdentity"]["arn"]},
        {'Key': 'awsRegion', 'Value': eventJson["awsRegion"]}
        ]
    # tag s3 buckets
    if (eventJson["eventSource"] == 's3.amazonaws.com' and
        eventJson["eventName"] == 'CreateBucket'):
        print("s3")
        # Run tag_s3 function
        result = tag_s3(eventJson["requestParameters"]["bucketName"], tags)
    # tag ec2 instances
    elif eventJson["eventSource"] == "ec2.amazonaws.com":
        print("ec2")
        # Run tag_ec2 function
        result = tag_ec2(eventJson["eventName"], eventJson["responseElements"],tags)
    # tag CreateTrail trails
    elif (eventJson["eventSource"] == "cloudtrail.amazonaws.com" and
        eventJson["eventName"] == 'CreateTrail'):
        print("cloudtrail")
        # Run tag_trail function
        result = tag_trail(eventJson["responseElements"],tags)
    # tag iam Roles and Policies
    elif eventJson["eventSource"] == "iam.amazonaws.com":
        print("iam")
        # Run tag_iam function
        tag_iam(eventJson["eventName"],eventJson["responseElements"],tags)
    
    # print output
    print(result)

# Tag All EC2 Resources
def tag_ec2(eventName, responseElements, tags):
    ec2 = boto3.resource('ec2')
    
    ids = []

    if eventName == "RunInstances":
        #loop through instances"
        for item in responseElements["instancesSet"]["items"]:
            ids.append(item['instanceId'])
        base = ec2.instances.filter(InstanceIds=ids)
        #loop through connected resources"
        for instance in base:
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
        ids.append(responseElements['networkaclid'])
    elif eventName == 'CreateVpc':
        ids.append(responseElements['vpcid'])
    if ids:
        return ec2.create_tags(
                    Resources=ids,
                    Tags=tags
                )
    return "No IDs"

# Tag S3 Bucket
def tag_s3(bucketName, tags):
    s3 = boto3.client('s3')

    return s3.put_bucket_tagging(
        Bucket=bucketName,
        Tagging={
            'TagSet': tags
            }
    )

# Tag CloudTrail trail
def tag_trail(responseElements, tags):
    cloudtrail = boto3.client('cloudtrail')

    print(responseElements)
    return cloudtrail.add_tags(
        ResourceId = responseElements['trailid'],
        TagsList = tags
    )

# Tag IAM Roles and Policies
def tag_iam(eventName, responseElements, tags):
    iam = boto3.client('iam')
    
    print(responseElements)
    if eventName == 'PutRolePolicy':
        
        return iam.tag_role(
            RoleName = responseElements['trailid'],
            TagsList = tags
        )