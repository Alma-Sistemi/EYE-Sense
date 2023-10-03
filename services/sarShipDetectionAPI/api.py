#import fastapi
from fastapi import FastAPI,UploadFile,File,BackgroundTasks
import fastapi
import fastapi.responses as responses
import services
import os,pathlib,aiofiles

app = FastAPI()


'''
Endpoint to check if everything is running properly
'''
@app.get("/")
def home():
    return {"Status":"OK"}





@app.post("/object_detection_demo")
async def detect_objects1(image: UploadFile = File(...)):
    
    await services.trigger_image_cap()
    
    if not os.path.exists("./temp"):
        print("GOT IN HERE")
        os.makedirs("temp")
    file_path_linear = services.upload_image("temp",image)
    if file_path_linear is None:
        return fastapi.HTTPException(status_code=409,detail="incorrect file type")
    #else:
    
    detectionRes = './predictions_demo/prediction_visual.png'

    # For Demo
    #detectionRes= services.detect(file_path_linear,file_path_db)
    
    if detectionRes == None:
        return fastapi.HTTPException(status_code=404,detail="Problem with detection")
    else :
        return responses.FileResponse(detectionRes)





'''
Input : 1 Linear Image , and one db Image (These two are the result of preprocessing)
Output : db_Image overlaid with the predictions 
Todo: (return maybe an array and use .js to create an Image in frontend?)
'''
@app.post("/ObjectDetection")
async def detect_objects(image_linear : UploadFile = File(...),image_db: UploadFile = File(...) ):
    
    await services.trigger_image_cap() #Check if there is enough storage to store the uploaded images
    
    # Create a folder for temporary storage
    if not os.path.exists("./temporary_storage"):
        os.makedirs("temporary_storage")
    

    file_path_linear = services.upload_image("temporary_storage",image_linear)
    if file_path_linear is None:
        return fastapi.HTTPException(status_code=409,detail="incorrect file type")
    #else:
    file_path_db = services.upload_image("temporary_storage",image_db)
    if file_path_db is None:
        return fastapi.HTTPException(status_code=409,detail="incorrect file type")

    #detectionRes = './results/prediction_visual.png'
    print(file_path_linear)
    # For Demo
    detectionRes= services.detect(file_path_linear,file_path_db)
    
    if detectionRes == None:
        return fastapi.HTTPException(status_code=404,detail="Problem with detection")
    else :
        return responses.FileResponse(detectionRes)


    