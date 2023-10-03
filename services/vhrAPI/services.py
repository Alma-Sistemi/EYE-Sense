from typing import List
import os
import random
import fastapi
import time
import glob
from mmdet.apis import init_detector, show_result_pyplot
from mmdet.apis import inference_detector_huge_image
import numpy as np
import inspect
import cv2
import BboxToolkit as bt
import mmcv

def get_filenames(directory_name:str) -> List[str]:
    return os.listdir(directory_name)


def is_Image(filename:str) -> bool:
    print(filename)
    valid_extensions=(".zip",".png",".jpg",".jpeg",".tif",".tiff")
    return filename.endswith(valid_extensions)


async def trigger_image_cap():
    files = glob.glob("./storage/*")
    if len(files)>5:
        for f in files:
            os.remove(f)

def upload_image(directory_name:str,image:fastapi.UploadFile):
    if is_Image(image.filename+".png"):
        timestr = time.strftime("%Y%m%d-%H%M%S")
        image_name = timestr + image.filename.replace(" ","-") 
        path = f"{directory_name}/{image_name}"
        with open(path, "wb+") as image_file_upload:
            image_file_upload.write(image.file.read())
        return path
    return None


def detect(image:str,classes=set()):
    config = './OBBDetection/configs/obb/oriented_rcnn/faster_rcnn_orpn_r101_fpn_1x_ms_rr_dota10.py'
    checkpoint = './resources/model/faster_rcnn_orpn_r101_fpn_1x_mssplit_rr_dota10_epoch12.pth'
    split = './OBBDetection/BboxToolkit/tools/split_configs/dota1_0/ss_test.json'
    #try:
    model = init_detector(config,checkpoint,device='cuda:0')
    nms_cfg = dict(type='BT_nms', iou_thr=0.2)
    result = inference_detector_huge_image(model,image,split,nms_cfg) 
    # trucks = 0 , plane =4 , ship = 5 , car = 9
    newRes = [result[x] if x in classes else np.empty([0, 6]) for x in range(len(result))]
    for i,x in enumerate(result):
        print(i)
        print(len(newRes[i]))
        #print(x)

    #print(newRes)
    newD = {i:0 for i in range(len(newRes))}
    for i,x in enumerate(newRes):
        for detectedObj in x:  
            if detectedObj[-1]>0.80:
                newD[i]+=1

    img = mmcv.imread(image)
    img = img.copy()
    bbox_result = newRes
    bboxes = np.vstack(bbox_result)
    labels = [
        np.full(bbox.shape[0], i, dtype=np.int32)
        for i, bbox in enumerate(bbox_result)
    ]


    labels = np.concatenate(labels)
    score_thr = 0.3
    bboxes, scores = bboxes[:, :-1], bboxes[:, -1]
    bboxes = bboxes[scores > score_thr]
    labels = labels[scores > score_thr]
    scores = scores[scores > score_thr]
    print("****")
    print(len(bboxes))
    img = bt.imshow_bboxes(
        img, bboxes, labels, scores,
        class_names=model.CLASSES,
        #colors=colors,
        #thickness=thickness,
        #font_size=font_size,
        #win_name=win_name,
        show=False,
        out_file='./predictions/resultsPort3.jpg')

    image = cv2.imread('./predictions/resultsPort3.jpg')
    position = (10,50)

    text = f"Ships Detected: {newD[5]}" 
    #newText = f"Planes Detected: {newD[4]}"
    font_color = (0,128,0,255)
    cv2.putText(
        image, #numpy array on which text is written
        text, #text
        position, #position at which writing has to start
        cv2.FONT_HERSHEY_SIMPLEX, #font family
        1, #font size
        font_color, #font color
        3) #font stroke

    '''
    cv2.putText(
        image, #numpy array on which text is written
        newText, #text
        (position[0],position[1]+50), #position at which writing has to start
        cv2.FONT_HERSHEY_SIMPLEX, #font family
        1, #font size
        font_color, #font color
        3) #font stroke
    '''
    cv2.imwrite('./predictions/output.jpg', image)
    #model.show_result(image,newRes,score_thr=0.75,out_file='./predictions/output.jpg')
    #source_code = inspect.getsource(model.show_result)
    #print(source_code)

    return "predictions/output.jpg"