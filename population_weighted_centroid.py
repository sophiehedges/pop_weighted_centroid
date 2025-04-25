# Population Weighted Centroid
# What date files are needed?
# 1. ONSPD (ONS Postcode Directory) - https://www.ons.gov.uk/methodology/geography/geographicalproducts/postcodeproducts
# 2. OA Population Estimates - https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/datasets/oa2011populationestimates

import pandas as pd
import os

# === Step 1: Load data ===

# Set the working directory to the location of this script
os.chdir("/Users/sophshedges/Documents/centroid")

# Load full ONSPD data
onspd = pd.read_csv("ONSPD_FEB_2024_UK.csv", low_memory=False)

# Use just what's needed
onspd = onspd[["pcd", "pcds", "lat", "long", "oa21"]].copy()
onspd["pcd"] = onspd["pcd"].str.strip()  # ensure no extra spaces

# Load OA population estimates
oa_pop = pd.read_csv("oa_population.csv", usecols=["OA_2021_Code", "Total"])
oa_pop.columns = ["oa21", "population"]

# Ensure column names match
oa_pop.columns = ["oa21", "population"]

# Merge ONSPD with OA populations
df = onspd.merge(oa_pop, on="oa21", how="inner")

# Clean types
df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
df["long"] = pd.to_numeric(df["long"], errors="coerce")
df["population"] = pd.to_numeric(df["population"], errors="coerce")
df = df.dropna(subset=["lat", "long", "population"])

# === Step 2: Compute centroids ===

centroids = (
    df.groupby("pcd")
    .apply(lambda g: pd.Series({
        "lat_centroid": (g["lat"] * g["population"]).sum() / g["population"].sum(),
        "lon_centroid": (g["long"] * g["population"]).sum() / g["population"].sum()
    }))
    .reset_index()
)

# === Step 3: Save output ===
centroids.to_csv("postcode_district_centroids.csv", index=False)
print("✅ Saved postcode centroids to 'postcode_district_centroids.csv'")
