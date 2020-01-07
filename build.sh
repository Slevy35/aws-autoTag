# zip code
cd src; zip -r ../build/aws-autotag.zip *; cd ..

# upload to s3 bucket
aws s3 cp build/aws-autotag.zip s3://autocleanuplogs/