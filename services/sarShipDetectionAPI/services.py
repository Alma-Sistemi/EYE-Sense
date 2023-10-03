from typing import List
import os
import random
import fastapi
import time
import glob
from sahi.model import Yolov5DetectionModel
from sahi.utils.cv import read_image
from sahi.utils.file import download_from_url
from sahi.predict import get_prediction, get_sliced_prediction, predict
import cv2
import numpy as np
from sahi.utils.cv import read_image_as_pil, visualize_object_predictions
from sahi.utils.file import Path



def get_filenames(directory_name:str) -> List[str]:
    # Function to get every filename is a given directory

    return os.listdir(directory_name)



def get_SSDD_model_weights(directory_name:str) -> str:
    # Used to retrieve the model weights from local storage

    files = get_filenames(directory_name)
    for f in files:
        if ".pt" in f and "SSDD" in f:
            return f"{directory_name}/{f}"
    return "error"



def is_Image(filename:str) -> bool:
    # Used to check if the given string is an actual image

    valid_extensions=(".zip",".png",".jpg",".jpeg",".tif",".tiff")
    return filename.endswith(valid_extensions)

async def trigger_image_cap():
    # Check if there is enough space in temporary storage. 
    # If there are more >THRESHOLD files then all of them are deleted
    THRESHOLD = 5
    
    files = glob.glob("./temporary_storage/*")
    if len(files)>THRESHOLD:
        for f in files:
            os.remove(f)

def upload_image(directory_name:str,image:fastapi.UploadFile):
    # Store an image in local file storage (in ./temporary_storage)
    # Uploaded images are given a distinct name based on time of upload 
    # output of the function is the directory the uploaded image is stored at
    if is_Image(image.filename+".png"):
        timestr = time.strftime("%Y%m%d-%H%M%S")
        image_name = timestr +"_"+ image.filename.replace(" ","-") +".png"
        image_name =  timestr +"_"+ image.filename.replace(" ","-")
        
        path = f"{directory_name}/{image_name}"
        with open(path, "wb+") as image_file_upload:
            image_file_upload.write(image.file.read())
        return path
    return None


def mask_borders(linearImage:str,dbImage:str):
    '''
    The model has some issues with white backgrounds,therefore we need to convert those white 
    pixels to black. We use the linearImage as an auxiliary image to help us turn the white background of
    dbImage to black pixels in order to decrease some mispredictions
    '''

    filename1_linear = linearImage
    filename2_db = dbImage
    img = cv2.imread(filename1_linear)
    img1 = cv2.imread(filename2_db)
    
    image_copy = img1.copy()

    black_pixels_mask1 = np.all(img == [0, 0, 0] ,axis=-1)

    image_copy[black_pixels_mask1] = [0, 0,0]
    #image_copy[non_black_pixels_mask] = [0, 0, 0]
    
    outdir = dbImage.replace(".png","")+"_masked.png"
    print(outdir)
    cv2.imwrite(outdir, image_copy) 
    return outdir


def rerotate_image(filename:str):
    # Currently it is not used. It is an auxiliary function to rotate images with a white background
    
    filename="./"+filename
    img = cv2.imread(filename)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    th, threshed = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)


    ## (2) Morph-op to remove noise
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11,11))
    morphed = cv2.morphologyEx(threshed, cv2.MORPH_CLOSE, kernel)

    ## (3) Find the max-area contour
    cnts = cv2.findContours(morphed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    cnt = sorted(cnts, key=cv2.contourArea)[-1]


    ## This will extract the rotated rect from the contour
    rot_rect = cv2.minAreaRect(cnt)

    # Extract useful data
    cx,cy = (rot_rect[0][0], rot_rect[0][1]) # rect center
    sx,sy = (rot_rect[1][0], rot_rect[1][1]) # rect size
    angle = rot_rect[2] # rect angle


    # Set model points : The original shape
    model_pts = np.array([[0,sy],[0,0],[sx,0],[sx,sy]]).astype('int')
    # Set detected points : Points on the image
    current_pts = cv2.boxPoints(rot_rect).astype('int')

    # sort the points to ensure match between model points and current points
    ind_model = np.lexsort((model_pts[:,1],model_pts[:,0]))
    ind_current = np.lexsort((current_pts[:,1],current_pts[:,0]))

    model_pts = np.array([model_pts[i] for i in ind_model])
    current_pts = np.array([current_pts[i] for i in ind_current])


    # Estimate the transform betwee points
    #M = cv2.estimateRigidTransform(current_pts,model_pts,True)
    [H,inliers] = cv2.estimateAffine2D(current_pts,model_pts)
    #print(type(M),type(x))
    # Wrap the image
    wrap_gray = cv2.warpAffine(gray, H, (int(sx),int(sy)))


    # for display
    #return wrap_gray
    outdir = "./results/002.png"
    cv2.imwrite(outdir, wrap_gray) 
    return outdir


def export_visuals(result, export_dir: str, text_size: float = None, rect_th: int = None,file_name="prediction_visual"):
        # Used to create the output image with detection bounding boxes
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
        
        Path(export_dir).mkdir(parents=True, exist_ok=True)
        visualize_object_predictions(
            image=np.ascontiguousarray(result.image),
            object_prediction_list=result.object_prediction_list,
            rect_th=rect_th,
            text_size=text_size,
            text_th=None,
            color=None,
            output_dir=export_dir,
            file_name=file_name,
            export_format="png",
)


def detect(linear_image:str,db_image:str, name=""):
    
    weights = get_SSDD_model_weights("./resources")

    # Load model weights
    detection_model = Yolov5DetectionModel(
        model_path = weights,
        confidence_threshold = 0.82,
        device = "cuda:0"
    )
    im = mask_borders(linear_image,db_image)
    try:    
        # Perform sliced prediction
        result = get_sliced_prediction(
            im,
            detection_model,
            slice_height = 200,
            slice_width = 200,
            overlap_height_ratio = 0.25,
            overlap_width_ratio = 0.25
        )
        
        print(im.split("/")[-1].replace(".png",""))
        
        if name:
            file_name=name 
        else:
            file_name = im.split("/")[-1].replace(".png","")
        
        export_visuals(result,export_dir="predictions/",text_size=0,rect_th=1,file_name=file_name)
        #result.export_visuals(export_dir="predictions/",text_size=0,rect_th=1)
        return "predictions/"+file_name+".png"
    except Exception as ex:
        print(str(ex))
        return None 
