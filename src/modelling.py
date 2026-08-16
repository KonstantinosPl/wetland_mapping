import os

import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.metrics import silhouette_score

def clustering(input_file, output_dir, src_img=None):
    output_path = os.path.join(output_dir, src_img, "clustering")

    os.makedirs(output_path, exist_ok=True)

    df = pd.read_parquet(input_file)
    
    sample_size = min(1000000, len(df))
    sample_data = df.sample(n=sample_size, random_state=42)

    features = df.columns[2:]

    scaler = StandardScaler()
    x_sample_scaled = scaler.fit_transform(sample_data[features])

    results = []

    for i in range(4, 12):
        kmeans = KMeans(n_clusters=i, random_state=42, n_init=10)

        clusters = kmeans.fit_predict(x_sample_scaled)

        silhouette_val = silhouette_score(
            x_sample_scaled,
            clusters,
            sample_size=10000,
            random_state=42
        )

        results.append({"clusters": i, "silhouette_score": silhouette_val})

    results = pd.DataFrame(results)

    best_k = int(
        results.loc[
            results["silhouette_score"].idxmax(),
            "clusters"
        ]
    )
    results["best"] = results["clusters"] == best_k

    print(f"Best number of clusters: {best_k}")

    x_scaled = scaler.transform(df[features])

    kmeans = MiniBatchKMeans(
        n_clusters=best_k,
        random_state=42,
        batch_size=10000,
        n_init=10
    )

    df["cluster"] = kmeans.fit_predict(x_scaled)

    results.to_csv(os.path.join(output_path, "sil_scores.csv"), index=False)
    df.to_parquet(os.path.join(output_path, "clustered_df.parquet"), index=False)

    return