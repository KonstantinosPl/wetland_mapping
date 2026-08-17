import os
from pathlib import Path

import rasterio as ras

import pandas as pd
import numpy as np

def raster2points(input_dir, output_dir, src_img=None):
    output_folder = os.path.join(output_dir, src_img, "points")

    os.makedirs(output_folder, exist_ok=True)

    all_indices = None

    for file in os.listdir(input_dir):

        tif_path = os.path.join(input_dir, file)
        index_name = os.path.splitext(file)[0]

        with ras.open(tif_path) as src:
            band = src.read(1)
            rows, cols = np.indices(band.shape)

            xs, ys = ras.transform.xy(
                src.transform,
                rows,
                cols,
                offset="center"
            )

            df = pd.DataFrame({
                "x": np.array(xs).ravel(),
                "y": np.array(ys).ravel(),
                index_name: band.ravel()
            })

            if src.nodata is not None:
                df = df[df[index_name] != src.nodata]

            df = df.dropna(subset=[index_name]).reset_index(drop=True)

            if all_indices is None:
                all_indices = df
            else:
                all_indices = all_indices.merge(df, on=["x", "y"], how="inner")

    output_path = os.path.join(output_folder, "rs_indices_points.parquet")
    all_indices.to_parquet(output_path, index=False)

    return all_indices

def table2raster(input_clustered_file, reference_tif, output_dir, src_img):
    output_folder = os.path.join(output_dir, src_img, "clustering")

    os.makedirs(output_folder, exist_ok=True)

    df = pd.read_parquet(input_clustered_file, columns=["x", "y", "cluster"])

    with ras.open(reference_tif) as src:
        profile = src.profile.copy()

        cluster_raster = np.full((src.height, src.width), -1, dtype="int16")

        rows, cols = ras.transform.rowcol(
            src.transform,
            df["x"].to_numpy(),
            df["y"].to_numpy()
        )

        cluster_raster[rows, cols] = df["cluster"].to_numpy()

        profile.update(dtype="int16", count=1, nodata=-9999)

    output_path = os.path.join(output_folder, "clustered_output.tif")

    with ras.open(output_path, "w", **profile) as dst:
        dst.write(cluster_raster, 1)

    return cluster_raster



def stack_bands(folder, output_file, order=None):
    """
    Stack raster bands according to a predefined order.

    Parameters
    ----------
    folder : str | Path
        Folder containing the .tif files.
    output_file : str | Path
        Output stacked raster.
    order : list
        Desired order of bands.
        Example:
        ["green", "red", "red_edge", "nir"]
    """

    if order is None:
        order = ["green", "red", "red_edge", "nir"]

    folder = Path(folder)

    # Retrieve all tif files
    tif_files = list(folder.glob("*.tif"))

    # Associate each band name with its file
    band_files = {}
    for tif in tif_files:
        name = tif.stem.lower()

        for band_name in order:
            if band_name in name:
                band_files[band_name] = tif
                break

    # Check that all requested bands exist
    missing = [b for b in order if b not in band_files]
    if missing:
        raise ValueError(f"Missing bands: {missing}")

    # Reorder according to 'order'
    ordered_files = [band_files[b] for b in order]

    stacked_bands = []

    for i, band_file in enumerate(ordered_files, start=1):
        print(f"{i}. Stacking {band_file.name}")

        with ras.open(band_file) as src:
            stacked_bands.append(src.read(1).astype(np.float32))

    # Shape: (rows, cols, bands)
    stacked_array = np.stack(stacked_bands, axis=2)

    # Use first raster as template
    with ras.open(ordered_files[0]) as src:
        metadata = src.meta.copy()

    metadata.update(
        count=stacked_array.shape[2],
        dtype=np.float32,
        nodata=-10000,
        compress="lzw"
    )

    # Write output
    with ras.open(output_file, "w", **metadata) as dst:

        # rasterio expects (bands, rows, cols)
        dst.write(np.moveaxis(stacked_array, 2, 0))

        # Assign band names
        for idx, band_name in enumerate(order, start=1):
            dst.set_band_description(idx, band_name)

    print(f"\nStack saved to: {output_file}")