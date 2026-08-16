import os

import rasterio as ras

import pandas as pd
import numpy as np

def raster2points(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

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

    output_path = os.path.join(output_dir, "rs_indices_points.parquet")
    all_indices.to_parquet(output_path, index=False)

    return all_indices

def table2raster(input_clustered_file, reference_tif, output_dir):
    output_folder = os.path.join(output_dir, "clustering")

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