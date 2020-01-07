# zip code
cd src; zip -r ../aws-autotag.zip *; cd ..

# upload to s3 bucket
aws s3 cp aws-autotag.zip s3://autocleanuplogs/