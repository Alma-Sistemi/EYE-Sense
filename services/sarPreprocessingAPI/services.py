import functools 
from utils import getAOI,getThreshold,savePlot,basemaps
import json
import folium
from folium import plugins                
from folium.plugins import MiniMap, Draw, Search
import os
import numpy as np
import skimage.filters  # threshold calculation
import geopandas
from sentinelsat.sentinel import SentinelAPI, read_geojson, geojson_to_wkt
from snappy import ProductIO
import snappy
#from time import time
from datetime import datetime                  # dates, times and intervalls
import time

# For testing
sourceBands = 'Amplitude_VH,Intensity_VH,Amplitude_VV,Intensity_VV'



def _applySubset(path,sourceBands,directory=None):
    if not os.path.exists("./storage"):
        os.makedirs("storage")
    directory = "./storage"

    
    # get path to AOI
    aoiDirectory = 'C:/Users/kosta/git/CV-Platform/frontend1.0/storage/saved_aois'
    #aoiDirectory = './aoi'
    file = getAOI(aoiDirectory)
    file = '/mnt/c/Users/kosta/git/CV-Platform/frontend1.0/storage/saved_aois/temp.geojson'
    if file == None :
        return None
    with open(file, 'r') as f:
        data_json = json.load(f)
    print(data_json)
    footprint = geojson_to_wkt(data_json)
    
    file_path = path
    S1_source = snappy.ProductIO.readProduct(file_path)
    
    

    # read geographic coordinates from Sentinel-1 image meta data
    meta_data = S1_source.getMetadataRoot().getElement('Abstracted_Metadata')
    # refines center of map according to Sentinel-1 image
    S1_center = (meta_data.getAttributeDouble('centre_lat'), meta_data.getAttributeDouble('centre_lon'))
    # defines polygon illustrating Sentinel-1 image
    polygon_geom = {
      "type": "FeatureCollection",
      "features":
                [{"type": "Feature",
                "properties": {},
                "geometry": {"type": "Polygon", "coordinates": [[[meta_data.getAttributeDouble('first_near_long'), meta_data.getAttributeDouble('first_near_lat')],
                                                                [meta_data.getAttributeDouble('last_near_long'), meta_data.getAttributeDouble('last_near_lat')],
                                                                [meta_data.getAttributeDouble('last_far_long'), meta_data.getAttributeDouble('last_far_lat')],
                                                                [meta_data.getAttributeDouble('first_far_long'), meta_data.getAttributeDouble('first_far_lat')],
                                                                [meta_data.getAttributeDouble('first_near_long'), meta_data.getAttributeDouble('first_near_lat')]]]}}]}


    with open(file, 'r') as f:
        data_json = json.load(f)
    footprint = geojson_to_wkt(data_json)

    
    
    # creates map for visualization
    f = folium.Figure(height=500)
    m = folium.Map(location = S1_center, zoom_start = 7.5, control_scale=True).add_to(f)
    # add S1 tile to map
    folium.GeoJson(polygon_geom, name='Sentinel-1 tile').add_to(m)
    # add AOI to map
    folium.GeoJson(file, name='AOI', style_function = lambda x: {'color':'green'}).add_to(m)
    # add custom basemap
    basemaps['Google Satellite Hybrid'].add_to(m)
    # add a layer control panel to the map
    m.add_child(folium.LayerControl())
    
    # Save map as html
    #m.save(outfile= "tile-aoi.html")

    print('Apply Subset File:          ', end='', flush=True)
    start_time = time.time()
    # Subset operator - SNAP
    parameters = snappy.HashMap()
    parameters.put('copyMetadata', True)
    geom = snappy.WKTReader().read(footprint)
    parameters.put('geoRegion', geom)
    parameters.put('sourceBands', sourceBands)
    S1_crop = snappy.GPF.createProduct('Subset', parameters, S1_source)
    print('--- %.2f  seconds ---' % (time.time() - start_time), flush=True)
    
    # status update
    return S1_crop

def _apply_orbit_file(inputFile):
    print('Apply Orbit File:          ', end='', flush=True)
    start_time = time.time()
    parameters = snappy.HashMap()
    # continue with calculation in case no orbit file is available yet
    parameters.put('continueOnFail', True)
    S1_Orb = snappy.GPF.createProduct('Apply-Orbit-File', parameters, inputFile)
    print('--- %.2f  seconds ---' % (time.time() - start_time), flush=True)
    return S1_Orb

def _apply_LandSeaMask(inputFile,landMask=True):
    print('Land-Sea-Mask   ', end='', flush=True)
    start_time = time.time()
    parameters = snappy.HashMap()
    parameters.put('useSRTM', True)
    parameters.put('landMask', landMask)

    #parameters.put('shorelineExtension', '10')
    #parameters.put('sourceBands', 'Intensity_VV')
    S1_LSM = snappy.GPF.createProduct('Land-Sea-Mask', parameters, inputFile)
    for i in range(S1_LSM.getNumBands()):
        S1_LSM.getBandAt(i).setNoDataValueUsed(True)
        S1_LSM.getBandAt(i).setNoDataValue(np.nan)
        
    print('--- %.2f  seconds ---' % (time.time() - start_time), flush=True)
    return S1_LSM



def _apply_calibration(inputFile):
    print('Radiometric Calibration:   ', end='', flush=True)
    start_time = time.time()
    parameters = snappy.HashMap()
    parameters.put('outputSigmaBand', True)
    parameters.put('selectedPolarisations','VH,VV')
    S1_Cal = snappy.GPF.createProduct('Calibration', parameters, inputFile)
    print('--- %.2f  seconds ---' % (time.time() - start_time), flush=True)
    return S1_Cal


def _apply_AdaptiveThresholding(inputFile):
    #Default Adaptive Thresholing for Ship Detection
    print('Adaptive Thresholding:        ', end='', flush=True)
    start_time = time.time()
    parameters = snappy.HashMap()
    parameters.put("targetWindowSizeInMeter",30)
    parameters.put("guardWindowSizeInMeter",500.0)
    parameters.put("backgroundWindowSizeInMeter",800.0)
    parameters.put("pfa",12.5)
    S1_AT = snappy.GPF.createProduct("AdaptiveThresholding",parameters,inputFile)
    print('--- %.2f  seconds ---' % (time.time() - start_time), flush=True)
    return S1_AT

def _apply_ObjectDiscrimination(inputFile):
    print('Object Discrimination:        ', end='', flush=True)
    start_time = time.time()
    parameters = snappy.HashMap()
    parameters.put("minTargetSizeInMeter",30.0)
    parameters.put("maxTargetSizeInMeter",600.0)
    S1_OD = snappy.GPF.createProduct("Object-Discrimination",parameters,inputFile)
    print('--- %.2f  seconds ---' % (time.time() - start_time), flush=True)
    return S1_OD

def _apply_TerrainCorrection(inputFile,border=False):
    print('Terrain Correction:        ', end='', flush=True)
    start_time = time.time()
    parameters = snappy.HashMap()
    parameters.put('demName', 'SRTM 1Sec HGT')
    parameters.put('demResamplingMethod', 'BILINEAR_INTERPOLATION')
    parameters.put('imgResamplingMethod', 'NEAREST_NEIGHBOUR')
    parameters.put('pixelSpacingInMeter', 10.0)
    parameters.put('nodataValueAtSea', True)
    parameters.put('saveSelectedSourceBand', True)
    #global S1_TC
    S1_TC = snappy.GPF.createProduct('Terrain-Correction', parameters, inputFile)
    if border:
        for i in range(S1_TC.getNumBands()):
            S1_TC.getBandAt(i).setNoDataValueUsed(True)
            S1_TC.getBandAt(i).setNoDataValue(255)
    print('--- %.2f  seconds ---' % (time.time() - start_time), flush=True)
    return S1_TC


def _apply_SpeckleFiltering(inputFile,border=False):
    # Speckle-Filter operator
    print('Speckle Filtering:         ', end='', flush=True)
    start_time = time.time()
    parameters = snappy.HashMap()
    parameters.put('filter', 'Lee')
    parameters.put('filterSizeX', 5)
    parameters.put('filterSizeY', 5)
    S1_Spk = snappy.GPF.createProduct('Speckle-Filter', parameters, inputFile)
    if border:
        for i in range(S1_Spk.getNumBands()):
            S1_Spk.getBandAt(i).setNoDataValueUsed(True)
            S1_Spk.getBandAt(i).setNoDataValue(255)
    print('--- %.2f  seconds ---' % (time.time() - start_time), flush=True)
    #S1_crop = applySubset(path,sourceBands)
    return S1_Spk

def _apply_LinearToFromdB(inputFile):
    print('Linear to dB:         ', end='', flush=True)
    start_time = time.time()
    db_conversion = snappy.GPF.createProduct('LinearToFromdB', snappy.HashMap(), inputFile)
    print('--- %.2f  seconds ---' % (time.time() - start_time), flush=True)
    return db_conversion
#print(applySubset(path,sourceBands))





def _saveResults(S1_TC,S1_Spk_db=None,id="",out_dir='./'):
    # inputFile should be result S1 - Terrain Correction
    expressions = ['' for i in range(S1_TC.getNumBands())]
    # empty array for threshold(s)
    #global thresholds
    thresholds = np.zeros(S1_TC.getNumBands())
    
    
    # loop through bands
    print('Plot:                      ', end='', flush=True)
    start_time = time.time()
    for i in range(S1_TC.getNumBands()):
        name = id+S1_TC.getBandNames()[i]
        savePlot(S1_TC.getBandAt(i),thresholds[i],outfile='./storage/'+name+'.png')
    print('--- %.2f seconds ---' % (time.time() - start_time), flush=True)


def preprocessingChain(path,sourceBands,name):
    tmp = _applySubset(path,sourceBands)
    tmp = _apply_orbit_file(tmp)
    tmp = _apply_LandSeaMask(tmp,landMask=True)
    tmp = _apply_calibration(tmp)
    tmp = _apply_SpeckleFiltering(tmp)
    spk_db = _apply_LinearToFromdB(tmp)
    tmp= _apply_TerrainCorrection(tmp) 
    _saveResults(tmp,id=name+"-linear-sea-")
    # Save the first mask before converting to db
    tc_db = _apply_LinearToFromdB(tmp)
    _saveResults(tc_db,S1_Spk_db=spk_db,id=name+"-new-sea-")