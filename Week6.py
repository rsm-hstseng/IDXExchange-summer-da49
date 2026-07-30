# District Mapping
# Read GeoJSON

import geopandas as gpd
import pandas as pd

sold_clean = pd.read_csv(
    "/Users/mollytseng/Desktop/IDX_Exchange/IDXExchange-summer-da49/sold_clean_analysis_ready.csv"
)
districts = gpd.read_file(
    "/Users/mollytseng/Desktop/IDX_Exchange/DistrictAreas2526_-284845464123469011.geojson"
)
print(districts.shape)
print(districts.columns)
print(districts.head())

# unified datatype
unified_districts = districts[districts["DistrictType"] == "Unified"].copy()
print(f"unified_shape : {unified_districts.shape}")
unified_districts[["DistrictName", "DistrictType"]]

# covert Coordinate Reference systems from 3857 to 4326
print(unified_districts.crs)
unified_districts = unified_districts.to_crs("EPSG:4326")
print(unified_districts.crs)

# Convert property coordinates into geographic points
sold_geo = gpd.GeoDataFrame(
    sold_clean.copy(),
    geometry=gpd.points_from_xy(sold_clean["Longitude"], sold_clean["Latitude"]),
    crs="EPSG:4326",
)

print("Property CRS:", sold_geo.crs)
print("Property dataset shape:", sold_geo.shape)
print(sold_geo[["Latitude", "Longitude", "geometry"]].head())

# Prepare district lookup table
district_lookup = unified_districts[
    ["DistrictName", "DistrictType", "CountyName", "geometry"]
].copy()
print("\nDistrict lookup shape:", district_lookup.shape)
print(district_lookup[["DistrictName", "DistrictType", "CountyName"]].head())

# Perform spatial join
sold_joined = gpd.sjoin(sold_geo, district_lookup, how="left", predicate="intersects")
# Check for duplicate matches
duplicate_join_count = sold_joined.index.duplicated().sum()
print("Duplicated property indexes:", duplicate_join_count)

# create final enriched dataset
sold_enriched = sold_joined.drop(
    columns=["index_right", "geometry"], errors="ignore"
).copy()

# Validate row counts and matching results
before_rows = len(sold_clean)
after_rows = len(sold_enriched)
matched_count = sold_enriched["DistrictName"].notna().sum()
unmatched_count = sold_enriched["DistrictName"].isna().sum()
match_rate = matched_count / after_rows * 100

print("\nValidation results")
print("------------------")
print(f"Before spatial join: {before_rows:,}")
print(f"After spatial join:  {after_rows:,}")
print(f"Matched districts:   {matched_count:,}")
print(f"Unmatched districts: {unmatched_count:,}")
print(f"Match rate:           {match_rate:.2f}%")
print(f"Duplicated indexes:   {duplicate_join_count:,}")

# Separate reasons for unmatched records
missing_coordinates = (
    sold_enriched["Latitude"].isna() | sold_enriched["Longitude"].isna()
)

zero_coordinates = (sold_enriched["Latitude"] == 0) | (sold_enriched["Longitude"] == 0)

unmatched_with_coordinates = (
    sold_enriched["DistrictName"].isna()
    & sold_enriched["Latitude"].notna()
    & sold_enriched["Longitude"].notna()
    & (sold_enriched["Latitude"] != 0)
    & (sold_enriched["Longitude"] != 0)
)

print("\nUnmatched record review")
print("-----------------------")
print("Missing latitude or longitude:", f"{missing_coordinates.sum():,}")
print("Zero latitude or longitude:", f"{zero_coordinates.sum():,}")
print(
    "Valid-looking coordinates but no Unified District match:",
    f"{unmatched_with_coordinates.sum():,}",
)

output_file = (
    "/Users/mollytseng/Desktop/IDX_Exchange/"
    "sold_combined_residential_school_district.csv"
)

sold_enriched.to_csv(output_file, index=False)
print("\nEnriched dataset saved successfully:")
print(output_file)

# =========================================================================================================
# Feature engineering and Market Metrics
sold_clean = pd.read_csv(
    "/Users/mollytseng/Desktop/IDX_Exchange/sold_combined_residential_school_district.csv"
)
listing_clean = pd.read_csv(
    "/Users/mollytseng/Desktop/IDX_Exchange/IDXExchange-summer-da49/listing_clean_analysis_ready.csv"
)

# data shape
print(sold_clean.shape)
print(listing_clean.shape)
# transfer sold datetime columns
date_cols = ["ListingContractDate", "PurchaseContractDate", "CloseDate"]
for col in date_cols:
    sold_clean[col] = pd.to_datetime(sold_clean[col], errors="coerce")
sold_clean = sold_clean.drop(
    columns=["ListingDate_dt", "CloseDate_dt"], errors="ignore"
)

# transfer listing dtype
listing_date_cols = [
    "ListingContractDate",
    "PurchaseContractDate",
    "CloseDate",
    "ContractStatusChangeDate",
]

for col in listing_date_cols:
    listing_clean[col] = pd.to_datetime(listing_clean[col], errors="coerce")
listing_clean.info()

# check originallistprice
sold_clean.loc[
    sold_clean["OriginalListPrice"] <= 0,
    ["OriginalListPrice", "ClosePrice", "City", "MlsStatus"],
]
sold_clean = sold_clean[sold_clean["OriginalListPrice"] > 0].copy()
# validate value
validation_summary = pd.DataFrame(
    {
        "Check": [
            "ClosePrice <= 0",
            "OriginalListPrice <= 0",
            "LivingArea <= 0",
            "DaysOnMarket < 0",
        ],
        "Count": [
            (sold_clean["ClosePrice"] <= 0).sum(),
            (sold_clean["OriginalListPrice"] <= 0).sum(),
            (sold_clean["LivingArea"] <= 0).sum(),
            (sold_clean["DaysOnMarket"] < 0).sum(),
        ],
    }
)

print(validation_summary)

# sold_clean data
import numpy as np

# price ratio
sold_clean["PriceRatio"] = sold_clean["ClosePrice"] / sold_clean["ListPrice"]
print(sold_clean["PriceRatio"].describe())

# Price Per Sq Ft
sold_clean["PricePerSqFt"] = sold_clean["ClosePrice"] / sold_clean["LivingArea"]
print(sold_clean["PricePerSqFt"].describe())

# Days On Market
print(sold_clean["DaysOnMarket"].describe())

# Year / Month / YrMo
# Year
sold_clean["Year"] = sold_clean["CloseDate"].dt.year
# Month (1-12)
sold_clean["Month"] = sold_clean["CloseDate"].dt.month
sold_clean[["CloseDate", "Year", "Month", "year_month"]].head(10)

# CloseToOriginalList
sold_clean["CloseToOriginalListRatio"] = (
    sold_clean["ClosePrice"] / sold_clean["OriginalListPrice"]
)
print(sold_clean["CloseToOriginalListRatio"].describe())

# Listing to Contract Days
sold_clean["ListingToContractDays"] = (
    sold_clean["PurchaseContractDate"] - sold_clean["ListingContractDate"]
).dt.days
print(
    sold_clean[
        ["ListingContractDate", "PurchaseContractDate", "ListingToContractDays"]
    ].head()
)
print(sold_clean["ListingToContractDays"].describe())

# Contract to Close Days
sold_clean["ContractToCloseDays"] = (
    sold_clean["CloseDate"] - sold_clean["PurchaseContractDate"]
).dt.days
print(sold_clean[["PurchaseContractDate", "CloseDate", "ContractToCloseDays"]].head())
print(sold_clean["ContractToCloseDays"].describe())

# Segment
# PropertyType/PropertySubType
property_summary = (
    sold_clean.groupby(["PropertyType", "PropertySubType"])
    .agg(
        TransactionCount=("ClosePrice", "count"),
        MedianClosePrice=("ClosePrice", "median"),
        MedianPricePerSqFt=("PricePerSqFt", "median"),
        MedianDaysOnMarket=("DaysOnMarket", "median"),
        MedianPriceRatio=("PriceRatio", "median"),
        MedianListingToContractDays=("ListingToContractDays", "median"),
        MedianContractToCloseDays=("ContractToCloseDays", "median"),
    )
    .sort_values(by="TransactionCount", ascending=False)
    .reset_index()
)
property_summary.head(20)
# CountyOrParish / MLSAreaMajor
county_mls_summary = (
    sold_clean.groupby(["CountyOrParish", "MLSAreaMajor"])
    .agg(
        TransactionCount=("ClosePrice", "count"),
        MedianClosePrice=("ClosePrice", "median"),
        MedianPricePerSqFt=("PricePerSqFt", "median"),
        MedianDaysOnMarket=("DaysOnMarket", "median"),
        MedianPriceRatio=("PriceRatio", "median"),
        MedianListingToContractDays=("ListingToContractDays", "median"),
        MedianContractToCloseDays=("ContractToCloseDays", "median"),
    )
    .sort_values(by=["CountyOrParish", "TransactionCount"], ascending=[True, False])
    .reset_index()
)

county_mls_summary.head(20)

### Listing
# price Ratio
listing_clean["PriceRatio"] = listing_clean["ClosePrice"] / listing_clean["ListPrice"]
print(listing_clean["PriceRatio"].describe())
# price per Sq Ft
listing_clean["PricePerSqFt"] = (
    listing_clean["ClosePrice"] / listing_clean["LivingArea"]
)
print(listing_clean["PricePerSqFt"].describe())
# Days on Market
print(listing_clean["DaysOnMarket"].describe())
# Year / Month / YearMonth
listing_clean["Year"] = listing_clean["ListingContractDate"].dt.year
listing_clean["Month"] = listing_clean["ListingContractDate"].dt.month
listing_clean["YearMonth"] = (
    listing_clean["ListingContractDate"].dt.to_period("M").astype(str)
)
print(listing_clean[["ListingContractDate", "Year", "Month", "YearMonth"]].head())
# remove 0 value
listing_clean = listing_clean.loc[listing_clean["OriginalListPrice"] > 0].copy()
# validate
validation_summary = pd.DataFrame(
    {
        "Check": [
            "ClosePrice <= 0",
            "OriginalListPrice <= 0",
            "LivingArea <= 0",
            "DaysOnMarket < 0",
        ],
        "Count": [
            (listing_clean["ClosePrice"] <= 0).sum(),
            (listing_clean["OriginalListPrice"] <= 0).sum(),
            (listing_clean["LivingArea"] <= 0).sum(),
            (listing_clean["DaysOnMarket"] < 0).sum(),
        ],
    }
)

print(validation_summary)

# Close to Original List Ratio
listing_clean["CloseToOriginalListRatio"] = (
    listing_clean["ClosePrice"] / listing_clean["OriginalListPrice"]
)
print(listing_clean["PriceRatio"].describe())

# Listing to Contract Day
listing_clean["ListingToContractDays"] = (
    listing_clean["PurchaseContractDate"] - listing_clean["ListingContractDate"]
).dt.days
print(listing_clean["ListingToContractDays"].describe())
# Contract to Close Days
listing_clean["ContractToCloseDays"] = (
    listing_clean["CloseDate"] - listing_clean["PurchaseContractDate"]
).dt.days
print(listing_clean["ContractToCloseDays"].describe())
