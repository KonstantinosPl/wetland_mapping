import os

import geopandas as gpd
import rasterio as ras

from rasterio.mask import mask
from shapely.geometry import mapping

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

from sklearn.preprocessing import StandardScaler

def plot_correlation_heatmap(input_path_data, output_dir, region_name=None, src_img=None):
    output_folder = os.path.join(output_dir, region_name, src_img, "heatmaps")
    os.makedirs(output_folder, exist_ok=True)

    data = pd.read_parquet(input_path_data)
    features = data.columns[2:]

    sample_size = min(1000000, len(data))

    sample_data = data.sample(n=sample_size, random_state=42)

    corr = sample_data[features].corr()

    fig, ax = plt.subplots(figsize=(12, 10))

    im = ax.imshow(corr, cmap="RdYlGn")

    ax.set_xticks(range(len(features)))
    ax.set_xticklabels(
        [feature.upper() for feature in features],
        rotation=90,
        fontsize=11
    )

    ax.set_yticks(range(len(features)))
    ax.set_yticklabels(
        [feature.upper() for feature in features],
        fontsize=11
    )

    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("Pearson Correlation", fontsize=12)
    cbar.ax.tick_params(labelsize=11)

    for i in range(len(features)):
        for j in range(len(features)):
            ax.text(
                j,
                i,
                f"{corr.iloc[i, j]:.2f}",
                ha="center",
                va="center",
                fontsize=10
            )

    plt.tight_layout()

    output_path = os.path.join(output_folder, f"corr_heatmap_input_{region_name}.svg")
    plt.savefig(output_path, format="svg", bbox_inches="tight")

    plt.close(fig)

    return


def plot_hist_index(tif_paths, output_dir, boundaries_path=None, region_name=None, src_img=None):
    """
    Reads index TIFs and strictly masks them using the original GeoJSON polygon
    so ONLY pixels inside the Zone of Interest are plotted.

    Creates one histogram per TIF.
    """
    output_folder = os.path.join(output_dir, region_name, src_img)
    os.makedirs(output_folder, exist_ok=True)

    if boundaries_path is not None:
        aoi = gpd.read_file(boundaries_path)   

    colormaps = {
        "NDVI": "RdYlGn",
        "NDWI": "Blues",
        "MSAVI": "YlGn",
        "VCI": "RdYlGn",
        "MCARI": "YlGn",
        "RTVI": "YlGn",
        "DATT4": "YlGn",
        "NDVIRE": "RdYlGn",
        "SR": "YlGn",
        "SAVI": "RdYlGn",
        "CTVI": "RdYlGn",
        "IPVI": "YlGn",
        "GNDVI": "RdYlGn",
        "MGRVI": "RdYlGn"
    }

    for index_name, file_path in tif_paths.items():

        if not os.path.exists(file_path):
            print(f"{index_name}: File Not Found")
            continue

        with ras.open(file_path) as src:

            if boundaries_path is not None:

                if aoi.crs != src.crs:
                    aoi_projected = aoi.to_crs(src.crs)
                else:
                    aoi_projected = aoi

                geoms = [mapping(geom) for geom in aoi_projected.geometry]

                out_image, _ = mask(
                    src,
                    geoms,
                    crop=True,
                    filled=False
                )

                inside_pixels = out_image[0].compressed()
                clean_data = inside_pixels[np.isfinite(inside_pixels)]

            else:
                data = src.read(1, masked=True)

                inside_pixels = data.compressed()
                clean_data = inside_pixels[np.isfinite(inside_pixels)]

        fig, ax = plt.subplots(figsize=(8, 6))

        _, bins, patches = ax.hist(
            clean_data,
            bins=100,
            density=False,
            edgecolor='black',
            linewidth=0.6
        )

        # Get colormap according to index
        cmap_name = colormaps.get(index_name.upper(), "viridis")
        cmap = plt.get_cmap(cmap_name)

        norm = Normalize(vmin=clean_data.min(), vmax=clean_data.max())

        # Color each histogram bar according to its index value
        bin_centers = (bins[:-1] + bins[1:]) / 2

        for bin_center, patch in zip(bin_centers, patches):
            patch.set_facecolor(
                cmap(norm(bin_center))
            )

        ax.set_yscale('linear')
        ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
        ax.set_title(f'{index_name} Histogram - {region_name}', fontsize=14, fontweight='bold')
        ax.set_xlabel(f'{index_name} Value', fontsize=12)
        ax.set_ylabel('Pixel Count', fontsize=12)
        ax.grid(axis='y', alpha=0.7)

        plt.tight_layout()

        output_path = os.path.join(output_folder, f"{index_name.lower()}_histogram.svg")

        plt.savefig(output_path, format="svg", bbox_inches="tight")
        plt.close(fig)

    return


def plot_clusters(clustered_file):
    df = pd.read_parquet(clustered_file, columns=["x", "y", "cluster"])

    x_unique = np.sort(df["x"].unique())
    y_unique = np.sort(df["y"].unique())[::-1]

    x_index = {x: i for i, x in enumerate(x_unique)}
    y_index = {y: i for i, y in enumerate(y_unique)}

    cluster_map = np.full((len(y_unique), len(x_unique)), np.nan)

    cols = df["x"].map(x_index).to_numpy()
    rows = df["y"].map(y_index).to_numpy()

    cluster_map[rows, cols] = df["cluster"].to_numpy()

    plt.figure(figsize=(10, 10))

    plt.imshow(
        cluster_map,
        extent=[
            x_unique.min(),
            x_unique.max(),
            y_unique.min(),
            y_unique.max()
        ],
        interpolation="nearest"
    )

    plt.colorbar(label="Cluster")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.title("K-means clusters")

    plt.tight_layout()
    plt.show()

    return

def plot_cluster_heatmap(clustered_file, output_dir, region_name, src_img=None):
    output_folder = os.path.join(output_dir, region_name, src_img, "heatmaps")

    os.makedirs(output_folder, exist_ok=True)

    df = pd.read_parquet(clustered_file)

    sample_size = min(1000000, len(df))
    sample_data = df.sample(n=sample_size, random_state=42)

    features = df.columns[2:-1]

    scaler = StandardScaler()
    sample_data[features] = scaler.fit_transform(sample_data[features])

    cluster_profiles = (sample_data.groupby("cluster")[features].mean())

    fig, ax = plt.subplots(figsize=(12, 6))
    im = ax.imshow(
        cluster_profiles,
        aspect="auto",
        cmap="RdYlGn",
        vmin=-2,
        vmax=2
    )

    ax.set_xticks(range(len(features)))
    ax.set_xticklabels([feature.upper() for feature in features], rotation=45, ha="right")
    ax.set_yticks(range(len(cluster_profiles)))
    ax.set_yticklabels(cluster_profiles.index)
    ax.set_ylabel("Cluster", fontsize=13)
    ax.tick_params(axis="x", labelsize=12)
    ax.tick_params(axis="y", labelsize=12)
    ax.set_title(f"Mean Standardized Remote Sensing Indices by Cluster - {region_name}", fontsize=14)

    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("Mean Standardized Value", fontsize=14)
    cbar.ax.tick_params(labelsize=12)

    plt.tight_layout()

    output_path = os.path.join(output_folder, f"cluster_profiles_heatmap_{region_name}.svg")
 
    plt.savefig(output_path, format="svg", bbox_inches="tight")
    plt.close(fig)

    return cluster_profiles

def plot_cluster_boxplots(clustered_file, output_dir, indices, region_name=None, src_img=None):
    output_folder = os.path.join(output_dir, region_name, src_img, "boxplots")
    os.makedirs(output_folder, exist_ok=True)

    df = pd.read_parquet(clustered_file)

    sample_size = min(1000000, len(df))
    sample_data = df.sample(n=sample_size, random_state=42)

    for index_name in indices:
        clusters = sorted(sample_data["cluster"].unique())

        data = [
            sample_data.loc[
                sample_data["cluster"] == cluster,
                index_name
            ].dropna()
            for cluster in clusters
        ]

        fig, ax = plt.subplots(figsize=(12, 8))

        ax.boxplot(data, positions=clusters, showfliers=False, medianprops={"color": "black", "linewidth": 1.5})

        ax.set_xticks(clusters)
        ax.set_xticklabels(clusters)

        ax.set_xlabel("Cluster", fontsize=12)
        ax.set_ylabel(index_name.upper(), fontsize=12)
        ax.tick_params(axis="x", labelsize=11)
        ax.tick_params(axis="y", labelsize=11)
        ax.set_title(f"{index_name.upper()} Distribution by Cluster - {region_name}", fontsize=14)
        ax.grid(axis="y", alpha=0.3)

        plt.tight_layout()

        output_path = os.path.join(output_folder, f"{index_name}_cluster_boxplot_{region_name}.svg")

        plt.savefig(output_path, format="svg", bbox_inches="tight")
        plt.close(fig)

    return

def plot_cluster_distribution(clustered_file, output_dir, region_name=None, src_img=None):
    output_folder = os.path.join(output_dir, region_name, src_img, "distribution")

    os.makedirs(output_folder, exist_ok=True)

    df = pd.read_parquet(clustered_file, columns=["cluster"])

    cluster_distribution = (
        df["cluster"]
        .value_counts()
        .sort_index()
        .reset_index()
    )

    cluster_distribution.columns = ["cluster", "pixel_count"]

    cluster_distribution["percentage"] = (
        cluster_distribution["pixel_count"]
        / cluster_distribution["pixel_count"].sum()
        * 100
    )

    fig, ax = plt.subplots(figsize=(8, 6))

    bars = ax.bar(
        cluster_distribution["cluster"],
        cluster_distribution["percentage"],
        color="0.65",
        edgecolor="black",
        linewidth=0.8
    )

    ax.set_xlabel("Cluster", fontsize=12)
    ax.set_ylabel("Pixels (%)", fontsize=12)
    ax.set_title(f"Cluster Distribution - {region_name}", fontsize=14)
    ax.set_xticks(cluster_distribution.index)
    ax.tick_params(axis="both", labelsize=11)
    ax.grid(axis="y", alpha=0.2, linewidth=0.6)
    ax.set_axisbelow(True)

    for bar, value in zip(bars, cluster_distribution["percentage"]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value:.1f}%",
            ha="center",
            va="bottom",
            fontsize=11
        )

    plt.tight_layout()
    
    output_path = os.path.join(output_folder, f"cluster_distribution_{region_name}.svg")

    cluster_distribution.to_csv(os.path.join(output_folder, f"cluster_distribution_{region_name}.csv"), index=False)

    plt.savefig(output_path, format="svg", bbox_inches="tight")
    plt.close(fig)

    return 
