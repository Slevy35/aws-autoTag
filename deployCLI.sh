# zip code
cd src; zip -r ../aws-autotag.zip *; cd ..

# create role
roleArn=$(aws iam create-role \
--role-name AllowTagging \
--path /service-role/ \
--assume-role-policy-document file://role-trust.json \
--description "Allow only tagging for aws-autotag function")

# put role policy
aws iam put-role-policy \
--role-name AllowTagging \
--policy-name AllowOnlyTagging \
--policy-document file://role-policy.json

# create lambda function
aws lambda create-function \
--function-name "aws-autotag" \
--description "Auto tag AWS resources" \
--runtime "python3.8" \
--role $(echo $roleArn|jq -r '.Role.Arn') \
--handler "main.handler" \
--zip-file "fileb://aws-autotag.zip"