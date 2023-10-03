from fastapi import FastAPI,UploadFile,File,BackgroundTasks
import fastapi
import fastapi.responses as responses
import services
import os,pathlib,aiofiles

# Model used is the one with highest accuracy in DOTA-dataset
config = './OBBDetection/configs/obb/oriented_rcnn/faster_rcnn_orpn_r101_fpn_1x_ms_rr_dota10.py'
checkpoint = './resources/model/faster_rcnn_orpn_r101_fpn_1x_mssplit_rr_dota10_epoch12.pth'
split = './OBBDetection/BboxToolkit/tools/split_configs/dota1_0/ss_test.json'

app = FastAPI()

@app.get("/")
def home():
    return {"Status":"OK"}


@app.post("/object_detection_planes")
async def detect_objects(image : UploadFile = File(...),cars: bool = False,planes: bool = False,trucks: bool = False, ships: bool = False):
    print(cars,planes,ships,trucks)
    # Check if there is space to save the uploaded image 
    await services.trigger_image_cap()
    if not os.path.exists("./storage"):
        os.makedirs("storage")
    file_path = services.upload_image("storage",image)
    if file_path is None:
        return fastapi.HTTPException(status_code=409,detail="incorrect file type")
    # trucks = 0 , planes =4 , ships = 5 , cars = 9
    classes = []
    if cars : classes.append(9)
    if planes : classes.append(4)
    if trucks :classes.append(0) 
    if ships : classes.append(5) 
    classes = set(classes)
    
    # Infer service for detection
    detectionRes= services.detect(file_path,classes)
    #detectionRes = "./predictions/output.jpg"
    if detectionRes == None:
        return fastapi.HTTPException(status_code=404,detail="Problem with detection")
    else :
        return responses.FileResponse(detectionRes)