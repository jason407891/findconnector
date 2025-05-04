import boto3
from mysql.connector import pooling
import os
from dotenv import load_dotenv #載入環境

load_dotenv()

aws_access_key_id =os.getenv("aws_access_key_id")
aws_secret_access_key = os.getenv("aws_secret_access_key")

#上傳圖片到S3
def insert_file_s3(time,userid,pn,file):
    s3 = boto3.client('s3',region_name='ap-southeast-2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    filename=str(time)+"_"+str(userid)+"_"+str(pn)+".png"
    s3.upload_fileobj(
        Fileobj=file,
        Bucket="findconnector",
        Key=filename, # 取檔名
        ExtraArgs={'ACL': 'public-read'}  # 設定公開讀取
    )
    file_url="https://findconnector.s3.ap-southeast-2.amazonaws.com/"+filename
    return file_url