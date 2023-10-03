import os
import geopandas as gpd
import streamlit as st


import streamlit as st

import ee
from datetime import date, timedelta
import datetime
import folium
import leafmap
import os
import json
import calendar
from apps.utils import download_button,general_utils,shipdetection_utils
#from utils import download_button,general_utils,shipdetection_utils
import pandas as pd
import plotly.tools as tls
import time

from datetime import date
import sys 
from sentinelsat.sentinel import SentinelAPI, read_geojson, geojson_to_wkt


@st.cache_data
def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')




def trigger(email):
    st.warning('Downloading and Preprocessing has officially begun. We will send an email to '+email+' with the results', icon="✅")

def app():
    sub = False
    st.markdown(
        """
            <h2 style='text-align:center'>
                Ship Detection
            </h2>
        """,unsafe_allow_html=True)
    
    
    step1_description = st.empty()
    with step1_description.container():
        st.markdown(
        """
        <h4 style='text-align:center'>
        Upload or Export a geojson for an area of interest (keep the size of the area reasonable) and find the available sentinel-1 tiles
        for that particular area in the selected timeframe
        </h4>
        """
        ,unsafe_allow_html=True)
    row1_col1, row1_col2 = st.columns([3, 1])
    submitted = False

    print("sub is now ",sub)
    
    
    with row1_col1:
        placeholder1= st.empty() 
        with placeholder1.container():  
            attr = ("&copy; <a href=https://www.esri.com/>Esri</a> &copy; <a href=https://services.arcgisonline.com/ArcGIS/rest/services>ArcGIS</a>")
            tiles = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
            m = leafmap.foliumap.Map(zoom_start=2,draw_export=True,attr=attr,tiles=tiles)
            m.to_streamlit(height=700)   
    
    with row1_col2:
        placeholder = st.empty() 
        with placeholder.container():  
            with st.form("my_form",clear_on_submit=True):
                username = st.text_input('Sentinel API username', '')
                password = st.text_input("Sentinel API password", type="password")
                with st.expander(label='Starting month'):
                    this_year = datetime.date.today().year
                    this_month = datetime.date.today().month
                    start_year = st.selectbox('startYear', range(this_year, this_year - 8, -1),label_visibility="hidden")
                    month_abbr = calendar.month_abbr[1:]
                    start_month_str = st.radio('startMonth', month_abbr, index=this_month - 1, horizontal=True,label_visibility="hidden")
                    start_month = month_abbr.index(start_month_str) + 1
                with st.expander(label='Ending month'):
                    this_year = datetime.date.today().year
                    this_month = datetime.date.today().month
                    end_year = st.selectbox('endYear', range(this_year, this_year - 8, -1),label_visibility="hidden")
                    month_abbr = calendar.month_abbr[1:]
                    end_month_str = st.radio('endMonth', month_abbr, index=this_month - 1, horizontal=True,label_visibility="hidden")
                    end_month = month_abbr.index(end_month_str) + 1
                #starting_date = st.date_input(label="Starting Date", value=None, min_value=None, max_value=None, key=None, help=None, on_change=None)
                #ending_date = st.date_input(label="Ending Date", value=None, min_value=None, max_value=None, key=None, help=None, on_change=None, args=None, kwargs=None)
                data = st.file_uploader(
                    "Upload a vector dataset", type=["geojson", "kml", "zip", "tab"]
                )
                #functionality = st.selectbox(label='Analysis',options=['Map Visualization','Raw data & Plot'])
                #newButton = st.form_submit_button(label="Testbutton")
                submit = st.form_submit_button("Submit")
                submitted = submit
                if submit:
                   
                    placeholder.empty()
                    placeholder1.empty()
                    step1_description.empty()
                    #with step1_description:
                        #st.warning('Downloading and Preprocessing has officially begun. We will send an email to kostantinosst23@gmail.com with the results', icon="✅")
    print('Form 1 submit is= ',submit)
    
    if submitted:
        print("submit is now", submit)
        products_df, m = shipdetection_utils.main()
        placeholder.empty()
        placeholder1.empty()
        step1_description.empty()
        with row1_col1:
            step2 = st.empty()
            with step2.container():
                m.to_streamlit(height=500)
                st.dataframe(products_df)
        with row1_col2:
            newForm = st.form("my_preprocessing_form",clear_on_submit=False)
            with newForm:
                email = st.text_input('Email for results', '')
                resultFormat = st.multiselect('Choose the format of results',['coco.txt file','.zip file with bounding boxes in images'],default = ['coco.txt file'])
                preprocessing_Chain = st.multiselect('Choose Preprocessing Chain',
                                                        ['Land-Sea-Mask','Radiometric calibration','Speckle filtering', 'Terrain Correction'],
                                                        help='Keep all the Preprocessing steps for optimal preprocessing',
                                                        default= ['Land-Sea-Mask','Radiometric calibration','Speckle filtering', 'Terrain Correction'])
                
                tiles_to_download = st.multiselect('Tiles to download',options = products_df, help='Details for every tile can be seen on the Table right below the map')
                #but = st.form_submit_button("Submit",on_)
                if st.form_submit_button("Submit"):
                    st.warning('Downloading and Preprocessing has officially begun. We will send an email to '+email+' with the results', icon="✅")
                    print("GOT IN HERE FINALLY")
                    sub=True
                else:
                    pass
                
            
           
            

