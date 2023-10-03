import os
import json
import calendar
import pandas as pd
import ee 
from datetime import date, timedelta
import datetime
import plotly.tools as tls
import plotly.express as px
import plotly.graph_objects as go
import leafmap

# imports 
from datetime import date
import sys 
from sentinelsat.sentinel import SentinelAPI, read_geojson, geojson_to_wkt
import folium

# INIT DATA

def main():
    credentials = {"username": "razkey23", "password": ".dinos123a", "sp_to": "2023-01-31", "sp_from": "2023-01-01", "polarization": "VH,VV"}
    data_json = {"type":"FeatureCollection","features":[{"type":"Feature","properties":{},"geometry":{"type":"Polygon","coordinates":[[[25.105991,35.337674],[25.136633,35.343065],[25.149422,35.333613],[25.122728,35.323809],[25.107365,35.32654],[25.105991,35.337674]]]}}]}

    Username = credentials['username']
    Password = credentials['password']
    SensingPeriod_Start = '2021-01-01'
    SensingPeriod_Stop = '2021-02-01'
    polarization = "VH,VV"

    api = SentinelAPI(Username, Password, 'https://scihub.copernicus.eu/dhus')
    try:
        # GeoJSON format if KMZ is given
        center = [data_json['features'][0]['geometry']['coordinates'][0][0][0][1],
                    data_json['features'][0]['geometry']['coordinates'][0][0][0][0]]
    except:
            # GeoJSON format if JSON or SHP is given
        center = [data_json['features'][0]['geometry']['coordinates'][0][0][1],
                    data_json['features'][0]['geometry']['coordinates'][0][0][0]]
            

    f = folium.Figure(height=500)
    m1 = leafmap.foliumap.Map(location=center,zoom_start=6,control_scale=True)
    m = folium.Map(location=center, zoom_start=6, control_scale=True).add_to(f)
    # add AOI to map
    
    folium.GeoJson(data_json, name='AOI', style_function = lambda x: {'color':'green'}).add_to(m)
    m1.add_geojson(data_json, style_function = lambda x: {'color':'green'})

    footprint = geojson_to_wkt(data_json)
    products_df,m= queri(footprint,m,m1,SensingPeriod_Start,SensingPeriod_Stop,api)
    return products_df,m

def queri(footprint,m,m1,SensingPeriod_Start,SensingPeriod_Stop,api):
    period = (date(int(SensingPeriod_Start.split('-')[0]), int(SensingPeriod_Start.split('-')[1]), int(SensingPeriod_Start.split('-')[2])),
              date(int(SensingPeriod_Stop.split('-')[0]), int(SensingPeriod_Stop.split('-')[1]), int(SensingPeriod_Stop.split('-')[2])))
    try:
        products = api.query(footprint, date=period, platformname='Sentinel-1', producttype='GRD')
        print('Successfully connected to Copernicus Open Access Hub.\n', flush=True)
    except:
        sys.exit('\nLogin data not valid. Please change username and/or password.')
    products_json = api.to_geojson(products)
    products_df = api.to_dataframe(products)
    indices = []
    for i in range (1, len(products_df.index)+1):
        indices.append('Tile %d' % i)
        products_json.features[i-1].properties['index'] = ' Tile %d' % i
    products_df.insert(0, 'index', indices, True) 
    
    s1_tiles = folium.GeoJson(
        products_json,
        name='S1 tiles',
        show=True,
        style_function=lambda feature: {'fillColor': 'royalblue', 'fillOpacity' : 0.2},
        highlight_function=lambda x: {'fillOpacity' : 0.4},
        tooltip=folium.features.GeoJsonTooltip(
            fields=['index', 'beginposition'],
            aliases=['Index:','Date:'],
        ),
    ).add_to(m)
    s1_tiles = folium.GeoJson(
        products_json,
        name='S1 tiles',
        show=True,
        style_function=lambda feature: {'fillColor': 'royalblue', 'fillOpacity' : 0.2},
        highlight_function=lambda x: {'fillOpacity' : 0.4},
        tooltip=folium.features.GeoJsonTooltip(
            fields=['index', 'beginposition'],
            aliases=['Index:','Date:'],
        ),
    ).add_to(m1)
    m1.add_child(folium.LayerControl())
    m.add_child(folium.LayerControl())
    return products_df,m1
    #print(products_df)




