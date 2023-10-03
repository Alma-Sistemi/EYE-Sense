import streamlit as st
import ee
from datetime import date, timedelta
import datetime
import os
import json
import calendar
from apps.utils import download_button,general_utils,atmosphericQuality_utils
import pandas as pd
import time
import requests
# Add EE drawing method to folium.



def app():
    st.title("Object Detection on Very High Resolution Imagery")

    object_selection = st.multiselect("Select objects:", ["Cars", "Ships", "Planes", "Containers"])

    if object_selection:
        st.write(f"You selected: {', '.join(object_selection)}")
    else:
        st.write("No objects selected.")

    # Image uploader
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

    # Check if an image is uploaded
    image_to_display = None
    if uploaded_file is not None:
        image_to_display = uploaded_file
    else:
        # Use the sample image if no image is uploaded
        sample_image_path = os.path.join("apps", "resources", "home", "output.jpg")
        image_to_display = sample_image_path

    if st.button("Run Inference") and uploaded_file:
        # Prepare the data for the POST request
        image_bytes = uploaded_file.getvalue()
        
        files = {
            "image": ("image.jpg", image_bytes, "image/jpeg"),
        }
        params = {
            "cars": "true" if "Cars" in object_selection else "false",
            "planes": "true" if "Planes" in object_selection else "false",
            "trucks": "true" if "Containers" in object_selection else "false",
            "ships": "true" if "Ships" in object_selection else "false"
        }

        # Send the POST request
        response = requests.post("http://localhost:8000/object_detection_planes", files=files, params=params)

        # Handle the response
        if response.status_code == 200:
            st.write("Inference successful!")
            image_to_display = response.content
        else:
            st.write(f"Error during inference: {response.text}")

    # Display the image (either uploaded, sample, or inference result)
    st.image(image_to_display, caption="Displayed Image.", use_column_width=True)