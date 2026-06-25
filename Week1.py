import pandas as pd
import glob
import re

# ============================================================
# Week 1 – Monthly Dataset Aggregation
# Concatenate all monthly MLS files from Jan 2024 to May 2026
# Filter to Residential only, save as combined CSVs
# ============================================================

# ------ SOLD: Select files (prefer _filled version) ------

all_sold_files = sorted(glob.glob("Dataset/CRMLSSold_Data/CRMLSSold*.csv"))

month_files = {}
for f in all_sold_files:
    match = re.search(r"CRMLSSold(\d{6})", f)
    if match:
        ym = match.group(1)
        if ym not in month_files or "_filled" in f:
            month_files[ym] = f

sold_files = [month_files[ym] for ym in sorted(month_files)]
print(f"Selected {len(sold_files)} sold files")

# ------ SOLD: Load and concatenate ------

sold_parts = []
for f in sold_files:
    df = pd.read_csv(f)
    print(f"  {f}: {len(df):,} rows")
    sold_parts.append(df)

sold = pd.concat(sold_parts, ignore_index=True)
print(f"\nSold before filter: {len(sold):,} rows")

# ------ LISTING: Select files ------

listing_files = sorted(glob.glob("Dataset/CRMLSListing_Data/CRMLSListing*.csv"))
print(f"\nSelected {len(listing_files)} listing files")

# ------ LISTING: Load and concatenate ------

listing_parts = []
for f in listing_files:
    df = pd.read_csv(f)
    print(f"  {f}: {len(df):,} rows")
    listing_parts.append(df)

listing = pd.concat(listing_parts, ignore_index=True)
print(f"\nListing before filter: {len(listing):,} rows")

# ------ Filter to Residential only ------

sold_residential = sold[sold["PropertyType"] == "Residential"].copy()
listing_residential = listing[listing["PropertyType"] == "Residential"].copy()

print(f"\nSold before filter:    {len(sold):,} rows")
print(f"Sold after filter:     {len(sold_residential):,} rows")
print(f"\nListing before filter: {len(listing):,} rows")
print(f"Listing after filter:  {len(listing_residential):,} rows")

# ------ Save to CSV ------

sold_residential.to_csv("sold_combined_residential.csv", index=False)
listing_residential.to_csv("listing_combined_residential.csv", index=False)

print("\n Saved: sold_combined_residential.csv")
print(" Saved: listing_combined_residential.csv")
