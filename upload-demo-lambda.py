import boto3
import io
import zipfile
import mimetypes

def lambda_handler(event, context):
    s3 = boto3.resource('s3')

    demo_bucket = s3.Bucket('demo.sga.guru')
    for obj in demo_bucket.objects.all():
        print(obj.key)
    # demo_bucket.download_file('index.html', '/tmp/index.html')
    
    build_bucket = s3.Bucket('build.demo.sga.guru')
    #build_bucket.download_file('buildDemo.zip', '/tmp/buildDemo.zip')
    
    demo_zip = io.BytesIO()
    build_bucket.download_fileobj('buildDemo.zip', demo_zip)
    
    # with zipfile.ZipFile(demo_zip) as myzip:
    #     for nm in myzip.namelist():
    #         print(nm)
    with zipfile.ZipFile(demo_zip) as myzip:
        for nm in myzip.namelist():
            obj = myzip.open(nm)
            demo_bucket.upload_fileobj(obj, nm, ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
            #demo_bucket.Object(nm).Acl().put(ACL='public-read')
    
    return 'Hello from Lambda'