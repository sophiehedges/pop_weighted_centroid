import pandas as pd
import os

print("Starting population-weighted centroid calculation for selected districts...")

# === Step 1: Set working directory ===
os.chdir("/Users/sophshedges/Documents/centroid")

# === Step 2: Load datasets ===
print("Loading Kantar districts...")
kantar = pd.read_csv("kantar_districts.csv")
kantar_districts = kantar["area_code"].unique().tolist()
print(f"Loaded {len(kantar_districts)} districts.")

print("Loading ONSPD data...")
onspd = pd.read_csv("ONSPD_FEB_2024_UK.csv", low_memory=False)
onspd = onspd[["pcd", "lat", "long", "oa21"]].copy()

# Extract postcode district from full postcode (e.g., "B11 1AA" → "B11")
onspd["district"] = onspd["pcd"].str.extract(r"^([A-Z]{1,2}\d{1,2})")
onspd["district"] = onspd["district"].str.strip()

# Filter ONSPD to only districts in Kantar list
onspd = onspd[onspd["district"].isin(kantar_districts)]
print(f"Filtered to {len(onspd)} postcode records in Kantar districts.")

print("Loading OA population estimates...")
oa_pop = pd.read_csv("oa_population.csv", usecols=["OA_2021_Code", "Total"])
oa_pop.columns = ["oa21", "population"]

# === Step 3: Merge and clean ===
print("Merging datasets...")
df = onspd.merge(oa_pop, on="oa21", how="inner")
df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
df["long"] = pd.to_numeric(df["long"], errors="coerce")
df["population"] = pd.to_numeric(df["population"], errors="coerce")
df = df.dropna(subset=["lat", "long", "population"])
print(f"Merged dataset has {len(df)} valid rows.")

# === Step 4: Compute population-weighted centroids ===
print("Calculating population-weighted centroids...")
centroids = (
    df.groupby("district")
    .apply(lambda g: pd.Series({
        "lat_centroid": (g["lat"] * g["population"]).sum() / g["population"].sum(),
        "lon_centroid": (g["long"] * g["population"]).sum() / g["population"].sum()
    }))
    .reset_index()
)
print(f"Calculated centroids for {len(centroids)} districts.")

# === Step 5: Merge centroids back into Kantar list ===
print("Adding centroids to original Kantar district list...")
kantar = kantar.merge(centroids, left_on="area_code", right_on="district", how="left")
kantar = kantar.drop(columns="district")

# === Step 6: Save output ===
output_file = "kantar_districts_with_centroids.csv"
kantar.to_csv(output_file, index=False)
print(f"Saved updated district centroids to '{output_file}'.")
