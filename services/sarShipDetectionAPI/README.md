# DetectionAPI - (SAR/Ship Detection)
A service (via FastAPI) with the following feature:
* Input : A cropped (or not) Sentinel-1 Image in .png/.jpg/.tif format (Could be VH, or VV polarization)
* Output : An Image after performing Ship-Detection leveraging YOLO and a Slicing Aid Hyper Inference technique.

To use this service you only need to create a conda environment 
```bash
cd detectionAPI
conda create -n detection python=3.7
conda activate detection
pip install -r requirements.txt
```

After creating the environment and activating it you run the following commands in a terminal
```bash
cd detectionAPI
uvicorn api:app --reload --port 8002 
``` 
Then you move to the localhost port uvicorn server is running on and you can use this service either via 
1. cURL
2. POSTMAN
3. localhost:8002/docs (provided by fastAPI)

**NOTE**: To work with the other services, detectionAPI needs to run on port 8002.

Sample Output if this service
![Imgur](https://i.imgur.com/sk01knC.jpg)