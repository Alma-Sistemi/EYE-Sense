import streamlit as st
import ee
from datetime import date, timedelta
import datetime
import folium
import leafmap
import os
import json
import calendar
from apps.utils import download_button,general_utils,waterQuality_utils
import pandas as pd
import plotly.tools as tls
import time

# Add EE drawing method to folium.
leafmap.foliumap.Map.add_ee_layer = general_utils.add_ee_layer


@st.cache_data
def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')

def get_current_year_and_month():
    today = date.today()
    return today.year, today.month

def get_month_selection(label, default_month):
    month_abbr = calendar.month_abbr[1:]
    month_str = st.radio(label, month_abbr, index=default_month - 1, horizontal=True, label_visibility="hidden")
    return month_abbr.index(month_str) + 1

def app():
    st.title("Water Quality")

    st.markdown(
    """
    Upload or Export a geojson for an area of interest (keep the size of the area reasonable) and retrieve Water Quality data 
    for that particular area in the selected timeframe
    """
    )

    row1_col1, row1_col2 = st.columns([4, 1])

    with row1_col2:
        with st.form("my_form"):
            current_year, current_month = get_current_year_and_month()
            years_range = range(current_year, current_year - 8, -1)

            with st.expander(label='Starting month'):
                start_year = st.selectbox('startYear', years_range, label_visibility="hidden")
                start_month = get_month_selection('startMonth', current_month)

            with st.expander(label='Ending month'):
                end_year = st.selectbox('endYear', years_range, label_visibility="hidden")
                end_month = get_month_selection('endMonth', current_month)

            data = st.file_uploader("Upload a vector dataset", type=["geojson", "kml", "zip", "tab"])
            metrics = st.multiselect('Choose Water Quality Indices', ['Chlorophyl-A', 'Turbidity', 'Suspended Matter', 'Color Dissolved Organic Matter'])
            submitted = st.form_submit_button("Submit")


            if submitted:
                if data: #Check if .geojson file was given
                    file_path = general_utils.save_uploaded_file(data, data.name)
                    layer_name = os.path.splitext(data.name)[0]
                    # Save the uploaded file
                    with open(file_path,'r') as f:
                        geom = json.load(f)
                        eegeom = general_utils.getGeometry(geom)
                    frequency = 'Daily'
                    dataframe = waterQuality_utils.getDataFrame(eegeom,start_year,start_month,end_year,end_month,metrics)
                    dataframe.to_csv('temporary.csv')
                    plot = waterQuality_utils.createPlot(dataframe,frequency)
                    first_column = dataframe.pop('date')
                    dataframe.insert(0,'date',first_column)
                    dataframe = dataframe.reset_index(drop=True)
                    csv = convert_df(dataframe)
                    
                    with row1_col1:
                        st.plotly_chart(plot)
                        st.dataframe(dataframe)
                        download_button_str = download_button.download_button(csv,"file.csv","Press To Download")
                        st.markdown(download_button_str, unsafe_allow_html=True)

            else:
                with row1_col1:
                    attr = ("&copy; <a href=https://www.esri.com/>Esri</a> &copy; <a href=https://services.arcgisonline.com/ArcGIS/rest/services>ArcGIS</a>")
                    tiles = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                    m = leafmap.foliumap.Map(zoom_start=2,draw_export=True,attr=attr,tiles=tiles)
                    m.to_streamlit(height=700)
    
