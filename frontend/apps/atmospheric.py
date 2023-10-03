import streamlit as st
import ee
from datetime import date, timedelta
import datetime
import folium
import leafmap
import os
import json
import calendar
from apps.utils import download_button,general_utils,atmosphericQuality_utils
import pandas as pd
import plotly.tools as tls
import time

# Add EE drawing method to folium.
leafmap.foliumap.Map.add_ee_layer = general_utils.add_ee_layer


@st.cache_data
def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')


# Function for date selection box
def get_date_selection(label):
    this_year = datetime.date.today().year
    this_month = datetime.date.today().month
    year = st.selectbox(label + ' Year', range(this_year, this_year - 8, -1))
    month_abbr = calendar.month_abbr[1:]
    month_str = st.radio(label + ' Month', month_abbr, index=this_month - 1, horizontal=True)
    month = month_abbr.index(month_str) + 1
    return year, month



def app():
    st.markdown("""
    
    <h1 style="text-align:center">Atmospheric Quality</h1>
    """, unsafe_allow_html=True)

    st.markdown(
    """
    <p style="text-align:center; font-size:20px;">Upload or Export a geojson for an area of interest (keep the size of the area reasonable) and see the nightlight
    activity for that particular area in the selected timeframe<p>
    """
    ,unsafe_allow_html=True)

    row1_col1, row1_col2 = st.columns([4, 1])

    with row1_col2:
        with st.form("my_form"):
            start_year, start_month = get_date_selection('Starting')
            end_year, end_month = get_date_selection('Ending')
            data = st.file_uploader("Upload a vector dataset", type=["geojson", "kml", "zip", "tab"])
            function = st.selectbox(label='Analysis', options=['Map Visualization', 'Raw data & Plot'])
            frequency = st.selectbox(label='Frequency', options=['Daily', 'Weekly', 'Monthly'])
            metrics = st.multiselect('Choose Atmospheric Indices', ['L3_SO2', 'L3_CO', 'L3_NO2', 'L3_HCHO', 'L3_AER_AI', 'L3_O3'])

            submitted = st.form_submit_button("Submit")
            
            
            if submitted:
                #general_utils.initCredentials()
                if data: #Check if .geojson file was given
                    file_path = general_utils.save_uploaded_file(data, data.name)
                    layer_name = os.path.splitext(data.name)[0]
                    # Save the uploaded file
                    with open(file_path,'r') as f:
                        geom = json.load(f)
                        eegeom = general_utils.getGeometry(geom)
                    #location = eegeom.centroid().coordinates().getInfo()[::-1]
                
                    # Visualization
                    if function == 'Map Visualization':
                        #Visualize only first metric
                        m = atmosphericQuality_utils.mapVisualization(eegeom,start_year,start_month,end_year,end_month,frequency,metrics[0])
                    
                        with row1_col1:
                            m.add_child(folium.LayerControl())
                            m.to_streamlit(height=700)
                    else:
                        dataframe = atmosphericQuality_utils.getDataFrame(eegeom,start_year,start_month,end_year,end_month,frequency,metrics)
                        #dataframe = pd.read_csv('temporary.csv')
                        dataframe.to_csv('temporary.csv')
                        plot = atmosphericQuality_utils.createPlot(dataframe,frequency)
                        first_column = dataframe.pop('date')
                        #print(first_column)
                        dataframe.insert(0,'date',first_column)
                        dataframe = dataframe.reset_index(drop=True)
                        #dataFrame = dataFrame.set_index('date')
                        csv = convert_df(dataframe)
                        #download_button_str = download_button.download_button(csv,"file.csv","Press To Download")
                        #st.markdown(download_button_str, unsafe_allow_html=True)
                        
                        with row1_col1:
                            st.plotly_chart(plot)
                            st.dataframe(dataframe)
                            download_button_str = download_button.download_button(csv,"file.csv","Press To Download")
                            st.markdown(download_button_str, unsafe_allow_html=True)

            else:
                with row1_col1:
                    attr = ("&copy; <a href=https://www.esri.com/>Esri</a> &copy; <a href=https://services.arcgisonline.com/ArcGIS/rest/services>ArcGIS</a>")
                    tiles = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                    m = leafmap.foliumap.Map(zoom_start=2,draw_export=True,tiles=tiles,attr=attr)
                    m.to_streamlit(height=700)
    
