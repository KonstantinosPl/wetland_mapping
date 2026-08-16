RASTER_PATHS = {
    "Parika": {
        "drone_img": {
            "red": r"..\data\raster\Parika\band_red.tif",
            "green": r"..\data\raster\Parika\band_green.tif",
            "nir": r"..\data\raster\Parika\band_nir.tif",
            "red_edge": r"..\data\raster\Parika\band_red_edge.tif"
        },
        "S2": {
            "red": r"..\data\raster\Parika\sentinel-2\red_band_sentinel_2.tif",
            "green": r"..\data\raster\Parika\sentinel-2\green_band_sentinel_2.tif",
            "nir": r"..\data\raster\Parika\sentinel-2\NIR_band_sentinel_2.tif",
            "red_edge": r"..\data\raster\Parika\sentinel-2\red_edge_band_sentinel_2_resampled.tif"
        }
    },

    "Ilmatsalu": {
        "drone_img": {
            "red": r"..\data\raster\Ilmatsalu\drone_imagery\band_red.tif",
            "green": r"..\data\raster\Ilmatsalu\drone_imagery\band_green.tif",
            "nir": r"..\data\raster\Ilmatsalu\drone_imagery\band_nir.tif",
            "red_edge": r"..\data\raster\Ilmatsalu\drone_imagery\band_redge.tif"
        },
        "S2": {
            "red": r"..\data\raster\Ilmatsalu\sentinel-2\red_band_sentinel_2.tif",
            "green": r"..\data\raster\Ilmatsalu\sentinel-2\green_band_sentinel_2.tif",
            "nir": r"..\data\raster\Ilmatsalu\sentinel-2\NIR_band_sentinel_2.tif",
            "red_edge": r"..\data\raster\Ilmatsalu\sentinel-2\red_edge_band_sentinel_2_resampled.tif"
        }
    }
}

REGION_NAME_PARIKA = "Parika"
REGION_NAME_ILMATSALU = "Ilmatsalu"

DIR_PARIKA = r"..\results\Parika"
DIR_ILMATSALU = r"..\results\Ilmatsalu"

DIR_PARIKA_INDICES_DRONE = r"..\results\Parika\drone_img\indices"
DIR_ILMATSALU_INDICES_DRONE = r"..\results\Ilmatsalu\drone_img\indices"

DIR_PARIKA_INDICES_S2 = r"..\results\Parika\S2\indices"
DIR_ILMATSALU_INDICES_S2 = r"..\results\Ilmatsalu\S2\indices"

OUTPUT_DIR_PLOTS = r"../results/plots"
OUTPUT_DIR_PLOTS_S2 = r"../results/plots/S2"


INDEX_NAMES = [
    "ndvi",
    "ndwi",
    "msavi",
    "vci",
    "mcari",
    "rtvi",
    "datt4",
    "ndvire",
    "sr",
    "savi",
    "ctvi",
    "ipvi",
    "gndvi",
    "mgrvi"
]