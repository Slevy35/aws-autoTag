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
        # Run tag_s3 function
        result = tag_s3(eventJson["requestParameters"]["bucketName"], tags)
    # tag ec2 instances
    elif eventJson["eventSource"] == "ec2.amazonaws.com":
        # Run tag_ec2 function
        result = tag_ec2(eventJson["eventName"], eventJson["responseElements"],tags)
        if eventJson["eventName"] == "CreateVpc":
            result = "Vpc"
    # print output
    print(result)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

# Tag All EC2 Resources
def tag_ec2(eventName, responseElements, tags):
    ec2 = boto3.resource('ec2')
    
    ids = []

    if eventName == "RunInstances":
        for item in responseElements["instancesSet"]["items"]:
            ids.append(item['instanceId'])
        base = ec2.instances.filter(InstanceIds=ids)
        #loop through the instances",
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
    if ids:
        return ec2.create_tags(
                    Resources=ids,
                    Tags=tags
                )
    return "No IDs"

# Tag All S3 Buckets
def tag_s3(bucketName, tags):
    s3 = boto3.client('s3')

    return s3.put_bucket_tagging(
        Bucket=bucketName,
        Tagging={
            'TagSet': tags
            }
    )