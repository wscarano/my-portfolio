import boto3
import io
import zipfile
import mimetypes

def lambda_handler(event, context):
    s3 = boto3.resource('s3')
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:743837219496:deployDemoTopic')

    location = {
        "bucketName": 'build.demo.sga.guru',
        "objectKey": 'buildDemo.zip'
    }
    print('location: ', location)

    try:
        job = event.get("CodePipeline.job")
        
        if job: 
            for artifact in job["data"]["inputArtifacts"]:
                if artifact["name"] == "MyAppBuild":
                    location = artifact["location"]["s3Location"]
                    
        print("Building demo from " + str(location))
        
        demo_bucket = s3.Bucket('demo.sga.guru')
        for obj in demo_bucket.objects.all():
            print(obj.key)
        # demo_bucket.download_file('index.html', '/tmp/index.html')
        
        build_bucket = s3.Bucket(location["bucketName"])
        
        
        #build_bucket.download_file('buildDemo.zip', '/tmp/buildDemo.zip')
        
        demo_zip = io.BytesIO()
        build_bucket.download_fileobj(location["objectKey"], demo_zip)
        
        # with zipfile.ZipFile(demo_zip) as myzip:
        #     for nm in myzip.namelist():
        #         print(nm)
        with zipfile.ZipFile(demo_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                demo_bucket.upload_fileobj(obj, nm, ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                #demo_bucket.Object(nm).Acl().put(ACL='public-read')
        
        topic.publish(Subject="Demo code deployed", Message="Deployed to bucket demo.sga.guru")
        print("Function Completed - Bucket Updated")
        if job:
            codepipeline = boto3.client('codepipeline')
            codepipeline.put_job_success_result(jobId=job["id"])
        
    except Exception as e:
        print("\n upload-demo-lambda error: ",str(e))
        # print("Function Failed")
        # topic.publish(Subject="Demo code deployment Failed", Message="Failed deployment to bucket demo.sga.guru")
        raise
    
    return 'demo Completed'