import ee
import streamlit as st
import json


@st.cache_resource()
def setup():
    print("Currently Running the Setup Function")
    serviceAccount = "earthenginealma@earth-engine-project-368208.iam.gserviceaccount.com"
    credentials = ee.ServiceAccountCredentials(serviceAccount,'earth-engine-key.json')
    ee.Initialize(credentials)
    print("Credentials Initialized")
# Call setup when this module is imported
setup()