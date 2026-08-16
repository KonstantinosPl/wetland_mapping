import numpy as np

np.seterr(divide='ignore')

# 1. Normalized Difference Vegetation Index
def NDVI(red, nir):
    ndvi = np.divide((nir - red), (nir + red))
    return ndvi

# 2. Normalized Difference Water Index.
def NDWI(green, nir):
    ndwi = np.divide((green - nir), (green + nir))
    return ndwi


# 3. Modified Soil Adjusted Vegetation Index. 
def MSAVI(red, nir):
    numerator = (2 * nir + 1) - np.sqrt(np.power((2 * nir + 1), 2) - 8 * (nir - red))
    msavi = np.divide(numerator, 2)
    return msavi

# 4. Vegetation Condition Index
# Ref: https://ieeexplore.ieee.org/document/8518022
def VCI(red, nir):
    ndvi     = NDVI(red, nir)
    ndvi_min = np.nanmin(ndvi)
    ndvi_max = np.nanmax(ndvi)
    vci      = ( ndvi - ndvi_min ) / ( ndvi_max - ndvi_min )
    return vci

#5. Modified Chlorophyll Absorption in Reflectance Index
def MCARI(green, red, redge):
    mcari =  np.multiply((redge-red) - np.multiply(0.2, (redge-green)), np.divide(redge, red))
    return mcari

# Red-Edge Triangulated Vegetation Index
def RTVI(green, redge, nir):
    rtvi = 100 * (nir - redge) - 10 * (nir-green) 
    return rtvi

# NDVI (red Edge)
def DATT4(green, red, redge):
    datt4 = np.divide(red, (green*redge))
    return datt4

# NDVI (red Edge)
def NDVIre(redge, nir):
    ndvire = np.divide((nir - redge),(nir + redge))
    return ndvire

# Simple Ratio
def SR(redge, nir):
    sr = np.divide(nir,redge)
    return sr

# Soil Adjusted Vegetation Index
def SAVI(red, nir):
    L = 0.5
    savi = np.multiply((1+L),(nir-red)) / (nir+red+L)
    return savi

# Corrected Transformed Ratio Vegetation Index
def CTVI(red, nir):
    ndvi = NDVI(red, nir)
    abs_ndvi_shift = np.abs(ndvi + 0.5)
    ctvi = ((ndvi + 0.5) / abs_ndvi_shift) * np.sqrt(abs_ndvi_shift)
    return ctvi

# Infrared percentage vegetation index. L8-UAV
def IPVI(red, nir):
    ndvi = NDVI(red, nir)
    ipvi =  np.multiply(0.5, (ndvi + 1) )
    return ipvi

# Green Normalized Difference Vegetation Index.
def GNDVI(green, nir):
    gndvi = np.divide((nir - green), (nir + green))
    return gndvi

# Modified Green Red Vegetation Index.
def MGRVI(green, red):
    mgrvi = np.divide((np.power(green, 2) - np.power(red, 2)), (np.power(green, 2) + np.power(red, 2)))
    return mgrvi
