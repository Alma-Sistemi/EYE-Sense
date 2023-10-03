# mmdetAPI

This service is used to integrate many mmdetection models to our Platform. As of now only a faster-RCNN which is trained on DOTA is utilized but it is easy to use any other model supported by the mmdetection framework.

To use this service you need to install OBBDetection. This is an intricate task and requires many careful steps. Refer to [this page](https://github.com/jbwang1997/OBBDetection/blob/master/docs/install.md) in order to properly install it

For reference : I set it up in WSL2 with the following configurations
pytorch=1.9.0+cu111. I had to install cudatoolkit 11.1 specifically inside the conda environment I created.

This Service right now uses a pre-trained FRCNN model to detect cars,trucks,airplanes and ships in very high resolution (VHR) imagery. 

Example output:
![Imgur](https://i.imgur.com/CCL9ygU.jpg)

To run this service and use it via frontend1.0 run the following:
```
uvicorn api:app --reload --port 8003
```


