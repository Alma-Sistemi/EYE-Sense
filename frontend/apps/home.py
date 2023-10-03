import streamlit as st
import leafmap
import ee
from apps.utils import general_utils
import pandas as pd
import plotly.tools as tls
import plotly.express as px
import plotly.graph_objects as go
import os
import json 

def minMaxScaling(column):
    return (column-column.min())/(column.max()-column.min())


def app():
    #general_utils.initCredentials()
    #st.title("Home")
    st.markdown("""
        <style>
        .small-font {
            font-size:15px !important;
        }
        .centered {
            display: flex;
            flex-direction: column;
            justify-content: center;
            height: 100%;
        }
        </style>
        """, unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center'>Extract information-rich indicators from Earth Observation missions</h1>",unsafe_allow_html=True)
    

    st.markdown('''
    <h3 style='text-align: center'>
        Use-case  - Area of Interest
    </h3>
    
    ''',unsafe_allow_html=True)
    grid = general_utils.make_grid(4,[1,2.5])
    with grid[0][0]:
        for _ in range(10):
            st.write("")
        st.markdown('''
                <div class="centered">
                    <p class="small-font">
                    In this case study we focus on the Area of Heraklion. We derive time-series information for three different domains
                        <ol>
                            <li>Maritime Activity via Detecting Ships in a given timeframe</li>
                            <li>Atmospheric Quality changes across time</li>
                            <li>Water Quality changes across time</li>
                        </ol>
                    </p>
                </div>
                 ''',unsafe_allow_html=True)
    with grid[0][1]:
        for _ in range(5):
            st.write("")
        with open('apps/resources/home/herPort.geojson', 'r') as f:
            data = json.load(f)
            eegeom = general_utils.getGeometry(data)
            location = eegeom.centroid().coordinates().getInfo()[::-1]
            m = leafmap.foliumap.Map(location=location,zoom_start=12,draw_export=True)
            m.add_geojson(data,layer_name='Area Of Interest')
            m.to_streamlit(height=300)
    
    
    
    
    # First row of the grid will contain information regarding the ship detection (sample time-series plot)
    with grid[1][0]:
        for _ in range(15):
            st.write("")
        
        #st.subheader("Ship Detection")
        st.markdown('''
                <div style='display: flex; flex-direction: column; justify-content: center; height: 100%;'>
                    <p class="small-font">
                    The workflow involves acquiring Sentinel-1 radar satellite images, preprocessing them through cropping,
                    calibration, speckle filtering, and terrain correction, and then using them as input for a trained YOLOv5 model to detect ships. 
                    The algorithm is trained on a dataset of annotated Sentinel-1 images. Time-series data for a specific area of interest can be 
                    obtained by applying the workflow to multiple Sentinel-1 images.
                    </p>
                </div>
                 ''',unsafe_allow_html=True)
    
    with grid[1][1]:
        st.subheader("")
        st.subheader("")
     
#grid[0][0].write()
        # Create the plot
        st.markdown('''
            <h5 style='text-align: center'>
            Number of Ships detected in Heraklion Port from 2017 up until mid 2022
            </h5>
            '''
        ,unsafe_allow_html=True)
        fig = go.Figure()
        df = pd.read_csv('apps/resources/home/shipdetection_HerPort.csv') 
        col = df.columns
        #gee-streamlit/apps/resources/home/shipdetection_HerPort.csv
        newDf = df.groupby(pd.PeriodIndex(df['Date'],freq='d'))["Ships"].mean()
        
        fig.add_trace(go.Scatter(
            x=newDf.index.strftime('%Y-%m-%d'),
            y=newDf,
            name="Number of Ships Detected",
            marker=dict(
                size=12,
            )
        ))
            
            
        st.plotly_chart(fig,use_container_width=True)
        st.subheader("")
        st.subheader("")
        
    with grid[2][0]:
        for _ in range(15):
            st.write("")
    #st.subheader("Ship Detection")
        st.markdown('''
            <p class="small-font">
            This workflow uses Google Earth Engine platform to access and process Sentinel-5p satellite data to generate time-series data for atmospheric indicators. 
            The user selects the area of interest and the desired atmospheric indicator(s) from six options, along with the frequency of analysis. 
            The platform uses a mean reducer to derive a single value for the selected indicators, 
            and generates a .csv file with time-series data for the specified frequency.
                </p>
                ''',unsafe_allow_html=True)
            
    with grid[2][1]:
        st.markdown('''
            <h5 style='text-align: center'>
            Mean Values of Atmospheric Indicators for Heraklion Area from 2018 up until Oct 2022
            </h5>
            '''
            ,unsafe_allow_html=True)
        df = pd.read_csv('apps/resources/home/HerakleionCoastal_Atmospheric_Full.csv') 

        cols = df.columns
        fig = go.Figure()
        for col in cols:
            if 'median' not in col: continue
            df[col+"_scaled"] = minMaxScaling(df[col])
            newDf = df.groupby(pd.PeriodIndex(df['date'],freq='d'))[col+"_scaled"].mean()
            fig.add_trace(go.Scatter(
                x=newDf.index.strftime('%Y-%m-%d'),
                y=newDf,
                name=col,
                marker=dict(
                    size=12,
                )
            ))
        st.plotly_chart(fig,use_container_width=True)
        st.subheader("")
        st.subheader("")

    with grid[3][0]:
        for _ in range(15):
            st.write("")
        #st.subheader("Ship Detection")
        st.markdown('''
                <p class="small-font">
                The Water Quality Analysis workflow uses multi-spectral satellite images from the Sentinel-2 mission to generate indicators for Chlorophyll-A, Cyanobacteria, \
                Turbidity, Dissolved Organic Carbon, and Color Dissolved Organic Matter. 
                The user provides the area of interest and time interval, and the appropriate formula is used to calculate the indicator values. 
                The mean reducer is then used to derive a single value for each indicator, which generates a time-series for the specified frequency.
                 </p>
                 ''',unsafe_allow_html=True)
    
    with grid[3][1]:
        st.markdown('''
            <h5 style='text-align: center'>
            Mean Values of Water Quality Indicators for Heraklion Area from 2018 up until Oct 2022
            </h5>
            '''
            ,unsafe_allow_html=True)
        files = ['apps/resources/home/Turbidity.csv','apps/resources/home/cholorophylA-L1C.csv']
        fig = go.Figure()
        dataframes = [pd.read_csv(file) for file in files]

        for df in dataframes:
            cols = df.columns
            for col in cols:
                if 'p50' not in col: continue
                df[col+"_scaled"] = minMaxScaling(df[col])
                newDf = df.groupby(pd.PeriodIndex(df['date'],freq='d'))[col+"_scaled"].mean()
                fig.add_trace(go.Scatter(
                    x=newDf.index.strftime('%Y-%m-%d'),
                    y=newDf,
                    name=col.replace("_p50",""),
                    marker=dict(
                        size=12,
                    )
                ))
        st.plotly_chart(fig,use_container_width=True)

    