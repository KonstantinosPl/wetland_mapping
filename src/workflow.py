import os 

import pandas as pd

import rasterio as ras

from src.vegetation_indices import *

def calculate_rs_indices(red_band, green_band, nir_band, red_edge_band, index_names):
    index_functions = {
        "ndvi": lambda: NDVI(red_band, nir_band),
        "ndwi": lambda: NDWI(green_band, nir_band),
        "msavi": lambda: MSAVI(red_band, nir_band),
        "vci": lambda: VCI(red_band, nir_band),
        "mcari": lambda: MCARI(green_band, red_band, red_edge_band),
        "rtvi": lambda: RTVI(green_band, red_edge_band, nir_band),
        "datt4": lambda: DATT4(green_band, red_band, red_edge_band),
        "ndvire": lambda: NDVIre(red_edge_band, nir_band),
        "sr": lambda: SR(red_edge_band, nir_band),
        "savi": lambda: SAVI(red_band, nir_band),
        "ctvi": lambda: CTVI(red_band, nir_band),
        "ipvi": lambda: IPVI(red_band, nir_band),
        "gndvi": lambda: GNDVI(green_band, nir_band),
        "mgrvi": lambda: MGRVI(green_band, red_band)
    }
    
    indices = {}

    for index_name in index_names:
        indices[index_name] = index_functions[index_name]()

    return indices

def workflow(red_path, green_path, nir_path, red_edge_path, output_dir, index_names):
    output_folder = os.path.join(output_dir, "indices")

    os.makedirs(output_folder, exist_ok=True)

    red_raster = ras.open(red_path)
    green_raster = ras.open(green_path)
    nir_raster = ras.open(nir_path)
    red_edge_raster = ras.open(red_edge_path)

    red_band = red_raster.read(1).astype("float32")     
    green_band = green_raster.read(1).astype("float32")
    nir_band = nir_raster.read(1).astype("float32")
    red_edge_band = red_edge_raster.read(1).astype("float32")

    nodata_mask = (
        (red_band == red_raster.nodata) |
        (green_band == green_raster.nodata) |
        (nir_band == nir_raster.nodata) |
        (red_edge_band == red_edge_raster.nodata)
    )

    profile = red_raster.profile.copy()
    profile.update(dtype="float32", count=1)

    indices = calculate_rs_indices(red_band, green_band, nir_band, red_edge_band, index_names)

    for index_name, index_data in indices.items():
        index_data[nodata_mask] = np.nan
        
        output_path = os.path.join(output_folder, f"{index_name}.tif")

        with ras.open(output_path, "w", **profile) as dst:
            dst.write(index_data.astype("float32"), 1)

    return indices


