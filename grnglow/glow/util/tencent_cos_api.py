# encoding: utf-8
#!/usr/bin/env python
'''
@author: rabbit

@contact: 739462304@qq.com

@time: 2018/6/25 15:01

@desc:

'''

from qcloud_cos import CosConfig

from qcloud_cos import CosS3Client

import sys,logging

fileURL=r'https://image-1256353254.cos.ap-shanghai.myqcloud.com/%s'

logging.basicConfig(level=logging.INFO,stream=sys.stdout)


secret_id='AKIDALRRL8BDVcXM6pPjvuiKQBnEUdbQgY3T'

secret_key='ISRFvY8h5IJ8rRp12tZ3SiojS0MWUHya'

region='ap-shanghai'

token=''

config=CosConfig(Secret_id=secret_id,Secret_key=secret_key,Region=region,Token=token)


client=CosS3Client(config)


#region  sample upload files ,suitable for small files ,maximum to more than 5GB


#file flow
def uploadByfilestream(file_name,rename,contenttype='image/jpeg'):
    if rename=='':
        rename=file_name
    with open(file_name,'rb') as fp:
        response=client.put_object(Bucket='image-1256353254',Body=fp,Key=rename,StorageClass='STANDARD',ContentType=contenttype)
        print(response['ETag'])
    return response['ETag']




#byte flow
def uploadByByteStream(bytedata):

    a=bytedata.encode('utf-8')

    response=client.put_object(Bucket='image-1256353254',Body=a,Key='bytetest.txt')

    print(response['ETag'])

    return response['ETag']



#local path upload
def uploadBylocalpath(file_name,rename):
    response=client.put_object_from_local_file(Bucket='image-1256353254',LocalFilePath=file_name,Key=rename)
    print(response['ETag'])
    return response['ETag']

#endregion



#region  senior

def uploadByblock(file_name,rename,partsize=10,MaxThread=10):

    response=client.upload_file(Bucket='image-1256353254',LocalFilePath=file_name,Key=rename,PartSize=partsize,MAXThread=MaxThread)

    r=response['ETag']

    url= fileURL % rename

    return url




#endregion


def download_file(key_filename,rename,Bucket='image-1256353254'):

    response=client.get_object(Bucket=Bucket,Key=key_filename)

    response['Body'].get_stream_to_file(rename)



def downloadByRange(key_filename,rename,range='0-10',Bucket='image-1256353254'):

    response=client.get_object(Bucket=Bucket,Key=key_filename,Range='bytes=%s'%range)

    fp=response['Body'].get_raw_stream()

    print(fp.read())

    with open(rename,'wb') as f:
        f.write(fp.read())





















