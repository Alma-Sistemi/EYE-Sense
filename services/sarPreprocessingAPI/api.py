#import fastapi
from fastapi import FastAPI,UploadFile,File,BackgroundTasks
import fastapi
import fastapi.responses as responses
from fastapi.responses import RedirectResponse
import os,pathlib,aiofiles
from utils import getAOI,zipfiles
import services

app = FastAPI()

@app.get("/")
def home():
    return {"Status":"OK"}




@app.get("/preprocessing_aoi")
def snap_preprocess(path1:str=""):
    #path,sourceBands
    filename = '../frontend1.0/saved_aois/'
    
    #Sourcebands
    sourceBands = 'Amplitude_VH,Intensity_VH,Amplitude_VV,Intensity_VV'
    
    #path = '../frontend1.0/storage/sar_storage/S1A_IW_GRDH_1SDV_20220408T154140_20220408T154205_042684_0517CC_2B6A.zip'
    path = "/mnt/c/Users/kosta/git/CV-Platform/frontend1.0/storage/sar_storage/S1B_IW_GRDH_1SDV_20210130T154913_20210130T154938_025386_030606_D0FC.zip"
    head, tail = os.path.split(path)
    name = tail[17:25]
    print(path,name)
    # For demo

    services.preprocessingChain(path,sourceBands,name)
    return "OK"
    file1 = './storage/'+name+'-linear-sea-Sigma0_VV.png'
    file2 = './storage/'+name+'-linear-sea-Sigma0_VH.png'
    file3 = './storage/'+name+'-new-sea-Sigma0_VV_db.png'
    file4 = './storage/'+name+'-new-sea-Sigma0_VH_db.png'
    
    img = [file1,file2,file3,file4]
    return zipfiles(img)
    #return responses.FileResponse(file1)
    #return {"f":file1,"f1":file2}
    

