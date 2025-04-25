# Load required libraries
library(sf)
library(ggplot2)
library(readr)
library(dplyr)

# Set working directory
setwd("/Users/sophshedges/Documents/centroid")

# Load your centroid data
centroids <- read_csv("kantar_districts_with_centroids.csv")

# Convert to sf object using lon/lat
centroids_sf <- st_as_sf(centroids, coords = c("lon_centroid", "lat_centroid"), crs = 4326)

# Load Birmingham boundary
bham_map <- st_read("/Users/sophshedges/OneDrive - London School of Hygiene and Tropical Medicine/birmingham_maps/geo_data/birmingham_boundaries.geojson")

# Ensure both layers have the same CRS
centroids_sf <- st_transform(centroids_sf, st_crs(bham_map))

# Find centroids inside Birmingham boundaries
inside <- st_within(centroids_sf, bham_map, sparse = FALSE)

# Filter to only those within the Birmingham map
centroids_inside <- centroids_sf[apply(inside, 1, any), ]

# Count how many are inside
cat("Number of centroids inside Birmingham boundary:", nrow(centroids_inside), "\n")

# Plot only the ones inside
ggplot() +
  geom_sf(data = bham_map, fill = "white", color = "grey50") +
  geom_sf(data = centroids_inside, color = "red", size = 2) +
  theme_minimal() +
  labs(title = "Population-Weighted Centroids Inside Birmingham",
       x = "Longitude", y = "Latitude")
# Save the plot
ggsave("centroids_inside_birmingham.png", width = 10, height = 8)
# Save the filtered centroids to a new geojson file
st_write(centroids_inside_birmingham, "centroids_inside_birmingham.geojson", delete_dsn = TRUE)
