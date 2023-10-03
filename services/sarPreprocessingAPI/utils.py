import glob
import geopandas
import os 
import folium
import shutil
from osgeo import ogr, gdal, osr              # data conversion
from zipfile import ZipFile
from folium import plugins                    # visualization
from folium.plugins import MiniMap, Draw, Search
import numpy as np
import skimage.filters  # threshold calculation
import matplotlib.pyplot as plt      
import os
import zipfile
import io
from fastapi import FastAPI, Response



def zipfiles(filenames):
    zip_filename = "archive.zip"

    s = io.BytesIO()
    zf = zipfile.ZipFile(s, "w")

    for fpath in filenames:
        # Calculate path for file in zip
        fdir, fname = os.path.split(fpath)

        # Add file, at correct path
        zf.write(fpath, fname)

    # Must close zip for all contents to be written
    zf.close()

    # Grab ZIP file from in-memory, make response with correct MIME-type
    resp = Response(s.getvalue(), media_type="application/x-zip-compressed", headers={
        'Content-Disposition': f'attachment;filename={zip_filename}'
    })

    return resp




basemaps = {
    'Google Satellite Hybrid': folium.TileLayer(
        tiles = 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        attr = 'Google',
        name = 'Google Satellite',
        overlay = True,
        control = True,
        show = False
    ),
    'Google Satellite': folium.TileLayer(
        tiles = 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        attr = 'Google',
        name = 'Google Satellite',
        overlay = True,
        control = True,
        show = False
    )
}

def readJSONFromAOI(path):
    # check for GeoJSON file in 'AOI' subfolder
    if len(glob.glob('%s/*.geojson' % path)) == 1:
        file = glob.glob('%s/*.geojson' % path)[0]
    elif len(glob.glob('%s/*.json' % path)) == 1:
        file = glob.glob('%s/*.json' % path)[0]

    # convert SHP to GeoJSON if no JSON is given
    elif len(glob.glob('%s/*.shp' % path)) == 1:
        file_name = os.path.splitext(glob.glob('%s/*.shp' % path)[0])[0].split('/')[-1]
        shp_file = geopandas.read_file(glob.glob('%s/*.shp' % path)[0])
        shp_file.to_file('%s/%s.json' % (path, file_name), driver='GeoJSON')
        file = glob.glob('%s/*.json' % path)[0]

    # convert KML to GeoJSON if no JSON or SHP is given
    elif len(glob.glob('%s/*.kml' % path)) == 1:
        file_name = os.path.splitext(glob.glob('%s/*.kml' % path)[0])[0].split('/')[-1]
        kml_file = gdal.OpenEx(glob.glob('%s/*.kml' % path)[0])
        ds = gdal.VectorTranslate('%s/%s.json' % (path, file_name), kml_file, format='GeoJSON')
        del ds
        file = glob.glob('%s/*.json' % path)[0]

    # convert KMZ to JSON if no JSON, SHP, or KML is given
    elif len(glob.glob('%s/*.kmz' % path)) == 1:
        # open KMZ file and extract data
        with ZipFile(glob.glob('%s/*.kmz' % path)[0], 'r') as kmz:
            folder = os.path.splitext(glob.glob('%s/*.kmz' % path)[0])[0]
            kmz.extractall(folder)
        # convert KML to GeoJSON if extracted folder contains one KML file
        if len(glob.glob('%s/*.kml' % folder)) == 1:
            kml_file = gdal.OpenEx(glob.glob('%s/*.kml' % folder)[0])
            ds = gdal.VectorTranslate('%s/%s.json' % (path, folder.split('/')[-1]), kml_file, format='GeoJSON')
            del ds
            file = glob.glob('%s/*.json' % path)[0]
            # remove unzipped KMZ directory and data
            shutil.rmtree(folder)
    # allow to upload AOI file or manually draw AOI if no file was found
    else:
        raise FileNotFoundError

    
    return file

def getAOI(path):
    try:
        file = readJSONFromAOI(path)
    except:
        '''
        print('No AOI file was found. Please draw and download the area of interest by clicking the Export-button')
        print('inside the map or directly upload a locally stored AOI file using the dialogue below the map.\n')
        # create map
        f = folium.Figure(height=500)
        m = folium.Map(location=[0, 0], zoom_start=2.5, control_scale=True).add_to(f)
        # add custom basemap
        basemaps['Google Satellite Hybrid'].add_to(m)
        # add a layer control panel to the map
        m.add_child(folium.LayerControl())
        # add minimap
        m.add_child(MiniMap(tile_layer=basemaps['Google Satellite'], position='bottomright'))
        # add draw control
        draw = Draw(export=True, filename='AOI_manual_%s.geojson' % str(date.today()), draw_options={'polyline': False, 'circle': False, 'marker': False, 'circlemarker': False})
        draw.add_to(m)
        # display map
        updater = display(f, display_id='m')
        print('\n')
        print("After exporting please upload the image to"+path+"   folder and then re-run the cell")
        # open upload section
        os.chdir('/content')
        uploaded = google.colab.files.upload()
        for fn in uploaded.keys():
            # copy uploaded file to GDrive folder
            aoi_path = os.path.join(directory, 'AOI')
            if not os.path.isdir(aoi_path):
                os.mkdir(aoi_path)
            shutil.copy2('/content/%s' % fn, aoi_path)
            # remove original file
            os.remove('/content/%s' % fn)
            file_path = '%s/%s' % (aoi_path, fn)
        '''
        file = None
        #file = readJSONFromAOI(aoi_path)
    
    return file


# calculate and return threshold of 'Band'-type input
# SNAP API: https://step.esa.int/docs/v6.0/apidoc/engine/
def getThreshold(S1_band):
    # read band
    w = S1_band.getRasterWidth()
    h = S1_band.getRasterHeight()
    band_data = np.zeros(w * h, np.float32)
    S1_band.readPixels(0, 0, w, h, band_data)
    band_data.shape = h * w
    # calculate threshold using Otsu method
    threshold_otsu = skimage.filters.threshold_otsu(band_data)
    # calculate threshold using minimum method
    threshold_minimum = skimage.filters.threshold_minimum(band_data)
    # get number of pixels for both thresholds
    numPixOtsu = len(band_data[abs(band_data - threshold_otsu) < 0.1])
    numPixMinimum = len(band_data[abs(band_data - threshold_minimum) < 0.1])

    # if number of pixels at minimum threshold is less than 0.1% of number of pixels at Otsu threshold
    if abs(numPixMinimum/numPixOtsu) < 0.001:
        # adjust band data according
        if threshold_otsu < threshold_minimum:
            band_data = band_data[band_data < threshold_minimum]
            threshold_minimum = skimage.filters.threshold_minimum(band_data)
        else:
            band_data = band_data[band_data > threshold_minimum]
            threshold_minimum = skimage.filters.threshold_minimum(band_data)
        numPixMinimum = len(band_data[abs(band_data - threshold_minimum) < 0.1])
    # check for final threshold
    if abs(numPixMinimum/numPixOtsu) < 0.001:
        threshold = threshold_otsu
    else:
        threshold = threshold_minimum

    return threshold

def savePlot(band,thresholds,outfile='output.png', binary=False):
    # color stretch
    vmin, vmax = 0, 1
    # read pixel values
    w = band.getRasterWidth()
    h = band.getRasterHeight()
    band_data = np.zeros(w * h, np.float32)
    print("slow")
    band.readPixels(0, 0, w, h, band_data)
    print("slow1")
    band_data.shape = h, w
    # color stretch
    if binary:
        cmap = plt.get_cmap('binary')
    else:
        vmin = np.percentile(band_data, 2.5)
        vmax = np.percentile(band_data, 97.5)
        cmap = plt.get_cmap('gray')
    #plt.savefig(outfile,band_data,transparent=True)
    print("In here")
    plt.imsave(outfile,band_data,cmap=cmap,vmin=vmin,vmax=vmax)