import os
import numpy as np
import gdal
from matplotlib import pyplot as plt
from rasterstats import zonal_stats
import geopandas as gpd
import pandas as pd
import datetime

# Directories
base_dir = 'C:/Users/40kmp/Desktop/Python projects/NDVI/'
LC_folder = 'LC08_L1TP_179021_20160715_20170323_01_T1/'
LC_dir = base_dir + 'Landsat8/' + LC_folder
file_list = os.listdir(LC_dir)

# Converting tif file into numpy array
def singleTifToArray(inRas):
    ds = gdal.Open(inRas, gdal.GA_ReadOnly)
    cols = ds.RasterXSize
    rows = ds.RasterYSize
    array = ds.ReadAsArray(0, 0, cols, rows).astype(float)
    return array

# Open the red band (band 4)
red = singleTifToArray(LC_dir + 'LC08_L1TP_179021_20160715_20170323_01_T1_B4.TIF')

name = file_list[0][0:42]  # creating default name so only band number needs to be added
print(name)

# Plotting red band
red = singleTifToArray(LC_dir + name + str(4) +'.TIF')
plt.figure()
im = plt.imshow(red)
plt.title('Red band')
plt.colorbar(im)


# In the previous plotting negative values take place. Most likely they are an artefact made by
# atmospheric correction. Since negative values for surface reflectance are meaningless we will
# replace them with NaNs
red = singleTifToArray(LC_dir + name + str(4) +'.tif')
red[red <0] = np.nan
plt.figure()
im = plt.imshow(red)
plt.title('Red band')
plt.colorbar(im)


# Changing function so negative values are excluded
def singleTifToArray_LC(inRas):
    ds = gdal.Open(inRas, gdal.GA_ReadOnly)
    cols = ds.RasterXSize
    rows = ds.RasterYSize
    array = ds.ReadAsArray(0, 0, cols, rows).astype(float)
    array[array<0] = np.nan #excludes negative values
    return array


# Plotting individual bands
red = singleTifToArray_LC(LC_dir + name + str(4) +'.tif')
nir = singleTifToArray_LC(LC_dir + name + str(5) +'.tif')

plt.figure(figsize=(10, 7))
im = plt.imshow(red,cmap='cool')
plt.title('Red band')
cb = plt.colorbar(im)
cb.set_label('Surface reflectance')
plt.savefig(base_dir + 'plots/red_band.png' , dpi=300, bbox_inches='tight')
plt.show()

plt.figure(figsize=(10, 7))
im = plt.imshow(nir,cmap='cool')
plt.title('Near Infrared band')
cb = plt.colorbar(im)
cb.set_label('Surface reflectance') 
plt.savefig(base_dir + 'plots/nir_band.png', dpi=300, bbox_inches='tight')
plt.show()


def NDVI(nir, red):
    ndvi = (nir - red) / (nir + red)
    return ndvi
ndvi = NDVI(nir, red)

plt.figure(figsize=(10, 7))
im = plt.imshow(ndvi, cmap='RdYlGn')
cb = plt.colorbar(im)
cb.set_label('NDVI')
plt.savefig(base_dir + 'plots/ndvi.png' , dpi=300, bbox_inches='tight')
plt.show()




# Automatic NDVI counting
LC_folders = ['LC08_L1TP_179021_20150526_20170408_01_T1/',
 'LC08_L1TP_179021_20160715_20170323_01_T1/',
 'LC08_L1TP_179021_20180907_20180912_01_T1/',
 'LC08_L1TP_179021_20190606_20190619_01_T1/',
 'LC08_L1TP_179021_20190910_20190917_01_T1/']

n = len(LC_folders) # number of iterations
for i in range(n):
    LC_dir = base_dir + 'Landsat8/' + LC_folders[i]
    file_list = os.listdir(LC_dir)
    name = file_list[0][0:42] 
    print(name)
    red = singleTifToArray_LC(LC_dir + name + str(4) +'.tif')
    nir = singleTifToArray_LC(LC_dir + name + str(5) +'.tif')
    ndvi = NDVI(nir, red)
    plt.figure()
    im = plt.imshow(ndvi, cmap='RdYlGn',vmin=-1,vmax=1)
    cb = plt.colorbar(im)
    cb.set_label('NDVI')
    year, month, day = name[17:21] , name[21:23] , name[23:25] # Adding date-title, info taken from the file name
    print(year, month, day)
    date = datetime.datetime(int(year) , int(month) , int(day))
    plt.title(date)
    plt.savefig(base_dir + 'plots/ndvi_'+year+month+day+'.png', dpi=300, bbox_inches='tight') 
    
    
# Exporting to TIFF 
def To_Tif(output, arr, gt, cs):
    driver = gdal.GetDriverByName('GTiff')
    driver.Register()
    outRaster = driver.Create(output, arr.shape[1], arr.shape[0], 1, gdal.GDT_Float64)
    outRaster.SetGeoTransform(gt)
    outRaster.SetProjection(cs)
    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(arr,0,0)
    outband.SetNoDataValue(np.nan)
    outband.FlushCache()
    del outband, outRaster, driver
 
n = len(LC_folders)
for i in range(n):
    LC_dir = base_dir + 'Landsat8/' + LC_folders[i]
    file_list = os.listdir(LC_dir)
    name = file_list[0][0:42] # root name

    red = singleTifToArray_LC(LC_dir + name + str(4) +'.tif')
    nir = singleTifToArray_LC(LC_dir + name + str(5) +'.tif')
    ndvi = NDVI(nir, red)
    ds = gdal.Open(LC_dir + name + str(4) +'.tif', gdal.GA_ReadOnly)
    gt , cs = ds.GetGeoTransform() , ds.GetProjection()
    To_Tif(base_dir + 'NDVIs/'+ name[0:34] +'_NDVI.tif', ndvi, gt, cs)
 
    
    
# Mean NDVI time-series
ndvi_dir = base_dir + 'NDVIs/'
ndvi_list = os.listdir(ndvi_dir)
print(ndvi_list)
ndvi_means , dates = [] , []

# Loop through NDVI tifs
n = len(LC_folders)
for i in range(n):
    ndvi = singleTifToArray(ndvi_dir + ndvi_list[i])
    
    mean_i = np.nanmean(ndvi) 
    ndvi_means.append(mean_i) 
        
    year, month, day = ndvi_list[i][17:21] ,ndvi_list[i][21:23], ndvi_list[i][23:25]
    date = datetime.datetime(int(year) , int(month) , int(day))
    dates.append(date) 
    
plt.figure(figsize=(10,5))
plt.plot(dates , ndvi_means, label='Mean NDVI')
plt.xlabel('Time')
plt.ylabel('NDVI') 
plt.legend() 
    



# NDVI for specific locations

def utm_to_matrix(x, y , gt):       # converting coordinates to matrix
    X = int(round((x - gt[0])/gt[1]))
    Y = int(round((y - gt[3])/gt[5]))
    return X, Y

eastings = [413954.68, 421658.27, 408873.42]
northings = [6179192.14, 6172958.79, 6174694.21]
labels = ['Zaryadye' , 'Volzhskiy bulvar' , 'Vorobyevi Gori']

#Zaryadye is a park in center of Moscow, founded in 2017
#Volzhskiy bulvar is a boulevard next to where I live
#Vorobyevi Gori - hills covered with trees

df = pd.DataFrame(index=dates, columns=labels)

# Loop through NDVI tifs
n = len(ndvi_list)
m = len(eastings)
for i in range(n):
    ndvi = singleTifToArray(ndvi_dir + ndvi_list[i]) # open ndvi tif

    year, month = ndvi_list[i][17:21] ,ndvi_list[i][21:23]
    day = ndvi_list[i][23:25]
    date = datetime.datetime(int(year) , int(month) , int(day))
 
    ds = gdal.Open(ndvi_dir + ndvi_list[i], gdal.GA_ReadOnly)
    gt = ds.GetGeoTransform()

    for j in range(m):
        x, y = utm_to_matrix(eastings[j], northings[j], gt) 
        df[labels[j]][date] = ndvi[y,x] # stores NDVI values in dataframe
        
plt.style.use('dark_background')
fig, axs = plt.subplots(1,figsize=(10,5))
axs.plot(dates, ndvi_means, label='Mean NDVI', linewidth=3)
df.plot(ax=axs)
plt.xlabel('Time')
plt.ylabel('NDVI')
axs.legend()
plt.savefig(base_dir + 'plots/trend_moscow.png' , dpi=300, bbox_inches='tight')
