#import fastapi
from fastapi import FastAPI,UploadFile,File,BackgroundTasks
import fastapi
import fastapi.responses as responses
from fastapi.responses import RedirectResponse
import os,pathlib,aiofiles
from utils import getAOI,zipfiles
import services
import os 
import time
sourceBands = 'Amplitude_VH,Intensity_VH,Amplitude_VV,Intensity_VV'

images=os.listdir('/mnt/c/Users/kosta/git/CV-Platform/frontend1.0/storage/sar_storage_new/')
#images=os.listdir('/mnt/c/Users/kosta/Documents/Computer-Vision/Sentinel-1-Imagery/')
already_parsed = os.listdir('./storage/')
parsed={"20180129","20180305","20180529"}
for date in already_parsed:
    parsed.add(date[0:8])
print(len(parsed))
for img in images:
    path = '/mnt/c/Users/kosta/git/CV-Platform/frontend1.0/storage/sar_storage_new/'+img
    #path = '/mnt/c/Users/kosta/Documents/Computer-Vision/Sentinel-1-Imagery/'+img
    #print(path)
    head, tail = os.path.split(path)
    name = tail[17:25]
    print(name)
    if name in parsed:
        continue
    try:
        x=1
        services.preprocessingChain(path,sourceBands,name)
        time.sleep(300)
    except Exception as ex:
        with open('./error.txt','w') as f:
            f.write(path+" "+str(ex)+"\n")
        continue

'''
    head, tail = os.path.split(path)
    name = tail[17:25]
    print(path,name)
    # For demo

    services.preprocessingChain(path,sourceBands,name)
'''
