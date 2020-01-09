# aws-autotag

This function allow you to automatically tag aws resources

**Suported resources**

- EC2 Instances
- EC2 Image
- EBS Volume
- EBS Snapshote
- InternetGateway
- SecurityGroup
- VPC
- S3 Bucket
- CloudTrail trail
- IAM Role
- Lambda Function

---

## How to deploy

### Clone

- Clone this repo to your local machine
- Change directory to the project folder

### Preper the function

- Zip the source code 

```sh

cd src; zip -r ../aws-autotag.zip *; cd ..

```

### Setup

- Create a temporary S3 Bucket
- Upload the zip file to the Bucket

### Deploy

- Create CloudFormation Stack
- Upload the template JSON file
- Insert the Bucket name that you created under Parameters
- Deploy!