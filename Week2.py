# Data Clean & EDA
import pandas as pd
import matplotlib.pyplot as plt

sold_residential = pd.read_csv("sold_combined_residential.csv")
listing_residential = pd.read_csv("listing_combined_residential.csv")

# check the row and columns
print("Sold shape:", sold_residential.shape)
print("Listing shape:", listing_residential.shape)
# check the data types
print(sold_residential.dtypes.value_counts())
print(listing_residential.dtypes.value_counts())


# show dtypes
def show_dtypes(df, name):
    print(f"\n{'=' * 50}\n{name}\n{'=' * 50}")
    for dtype in df.dtypes.unique():
        cols = df.select_dtypes(include=[dtype]).columns.tolist()
        print(f"\n{dtype} ({len(cols)} columns):")
        print(cols)


show_dtypes(sold_residential, "SOLD DATA")
show_dtypes(listing_residential, "LISTING DATA")


# missing value analysis
def missing_value_analysis(df, name, threshold=90):
    # count missing value and its percentage
    missing_count = df.isnull().sum()
    missing_pct = (df.isnull().mean() * 100).round(2)

    missing_summary = pd.DataFrame(
        {"missing_count": missing_count, "missing_pct": missing_pct}
    ).sort_values("missing_pct", ascending=False)
    print(f"\n{'=' * 50}\n{name} — Missing Value Summary\n{'=' * 50}")
    print(missing_summary)
    # flagged over 90% pct missing value
    flagged_cols = missing_summary[
        missing_summary["missing_pct"] > threshold
    ].index.tolist()
    print(f"\nColumns flagged with >{threshold}% missing ({len(flagged_cols)}):")
    print(flagged_cols)
    return missing_summary, flagged_cols


sold_missing, sold_flagged = missing_value_analysis(sold_residential, "SOLD DATA")
listing_missing, listing_flagged = missing_value_analysis(
    listing_residential, "LISTING DATA"
)

# Market Analysis columns
print(sold_residential["WaterfrontYN"].value_counts(dropna=False))
print(sold_residential["BasementYN"].value_counts(dropna=False))
print(sold_residential["BuildingAreaTotal"].value_counts(dropna=False))
print(sold_residential["TaxAnnualAmount"].value_counts(dropna=False))

# sold_data: define columns to drop
sold_columns_to_drop = [
    "AboveGradeFinishedArea",
    "TaxAnnualAmount",
    "CoveredSpaces",
    "TaxYear",
    "ElementarySchoolDistrict",
    "FireplacesTotal",
    "MiddleOrJuniorSchoolDistrict",
    "BusinessType",
    "BelowGradeFinishedArea",
    "LotSizeDimensions",
    "BuilderName",
    "CoBuyerAgentFirstName",
    "latfilled",
    "lonfilled",
]
sold_columns_to_review = [
    "WaterfrontYN",
    "BasementYN",
    "BuildingAreaTotal",
]
# Make sure only existing columns are dropped
sold_columns_to_drop_existing = [
    col for col in sold_columns_to_drop if col in sold_residential.columns
]
# create new clean dataframe
sold_data_clean = sold_residential.drop(columns=sold_columns_to_drop_existing)
# check
print("Original sold_data shape:", sold_residential.shape)
print("Clean sold_data shape:", sold_data_clean.shape)
print("\nDropped columns:")
print(sold_columns_to_drop_existing)
print("\nReview columns still kept:")
print([col for col in sold_columns_to_review if col in sold_data_clean.columns])

# =================================================================================================

# listing_data: define columns to drop
listing_columns_to_drop = [
    "TaxAnnualAmount",
    "FireplacesTotal",
    "ElementarySchoolDistrict",
    "TaxYear",
    "BusinessType",
    "MiddleOrJuniorSchoolDistrict",
    "CoveredSpaces",
    "AboveGradeFinishedArea",
    "BelowGradeFinishedArea",
    "CoBuyerAgentFirstName",
    "BuilderName",
    "LotSizeDimensions",
    "BuildingAreaTotal",
]
# create a cleaned dataset
listing_data_clean = listing_residential.drop(columns=listing_columns_to_drop)
# check
print("Original listing_data shape:", listing_residential.shape)
print("Clean listing_data shape:", listing_data_clean.shape)
print("\nDropped columns:")
print(listing_columns_to_drop)
print(sold_data_clean.columns)
print(listing_data_clean.columns)

# =================================================================================================
# sold_data_clean
# Separate market analysis fields from metadata fields
# metadata columns
metadata_columns = [
    "ListingKey",
    "ListingKeyNumeric",
    "ListingId",
    "ListAgentEmail",
    "ListAgentFirstName",
    "ListAgentLastName",
    "ListAgentFullName",
    "CoListAgentFirstName",
    "CoListAgentLastName",
    "BuyerAgentMlsId",
    "BuyerAgentFirstName",
    "BuyerAgentLastName",
    "ListOfficeName",
    "BuyerOfficeName",
    "CoListOfficeName",
    "BuyerOfficeAOR",
    "BuyerAgentAOR",
    "ListAgentAOR",
    "StreetNumberNumeric",
    "UnparsedAddress",
    "OriginatingSystemName",
    "OriginatingSystemSubName",
]
# Keep only metadata columns that exist in sold_data_clean
metadata_columns = [col for col in metadata_columns if col in sold_data_clean.columns]
# Everything else becomes market analysis columns
market_analysis_columns = [
    col for col in sold_data_clean.columns if col not in metadata_columns
]
# Create separate dataframes
sold_market_df = sold_data_clean[market_analysis_columns].copy()
sold_metadata_df = sold_data_clean[metadata_columns].copy()
# check data info
print("Market analysis shape:", sold_market_df.shape)
print("Metadata shape:", sold_metadata_df.shape)

# =================================================================================================

# check the listing data duplicate columns
for col in listing_data_clean.columns:
    if col.endswith(".1"):
        original = col[:-2]

        if original in listing_data_clean.columns:
            same = listing_data_clean[original].equals(listing_data_clean[col])
            print(f"{original:<20} == {col:<20} : {same}")
# delete duplicate columns
duplicate_columns = [col for col in listing_data_clean.columns if col.endswith(".1")]
listing_data_clean = listing_data_clean.drop(columns=duplicate_columns)
print("Dropped duplicated columns:")
print(duplicate_columns)
print("New shape:", listing_data_clean.shape)
print(listing_data_clean.columns)

# =================================================================================================
# listing_data_clean
# Separate market analysis fields from metadata fields
# metadata columns
metadata_columns = [
    "ListingKey",
    "ListingKeyNumeric",
    "ListingId",
    "ListAgentEmail",
    "ListAgentFirstName",
    "ListAgentLastName",
    "ListAgentFullName",
    "CoListAgentFirstName",
    "CoListAgentLastName",
    "BuyerAgentMlsId",
    "BuyerAgentFirstName",
    "BuyerAgentLastName",
    "ListOfficeName",
    "BuyerOfficeName",
    "CoListOfficeName",
    "BuyerOfficeAOR",
    "BuyerAgencyCompensationType",
    "StreetNumberNumeric",
    "UnparsedAddress",
]
# Keep only metadata columns that exist
metadata_columns = [
    col for col in metadata_columns if col in listing_data_clean.columns
]
# Everything else is market analysis
market_analysis_columns = [
    col for col in listing_data_clean.columns if col not in metadata_columns
]
# Create separate dataframe
listing_metadata_df = listing_data_clean[metadata_columns].copy()
listing_market_df = listing_data_clean[market_analysis_columns].copy()
print("Market analysis shape:", listing_market_df.shape)
print("Metadata shape:", listing_metadata_df.shape)

# =================================================================================================
# Numeric Distribution
numeric_cols = [
    "ClosePrice",
    "ListPrice",
    "OriginalListPrice",
    "LivingArea",
    "LotSizeAcres",
    "BedroomsTotal",
    "BathroomsTotalInteger",
    "DaysOnMarket",
    "YearBuilt",
]

for col in numeric_cols:
    print("=" * 80)
    print(col)
    print("=" * 80)

    # Missing values
    missing = sold_market_df[col].isna().sum()
    missing_pct = sold_market_df[col].isna().mean() * 100

    print(f"Missing Values : {missing:,} ({missing_pct:.2f}%)")

    # Summary statistics
    print("\nSummary Statistics")
    print(
        sold_market_df[col].describe(
            percentiles=[0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99]
        )
    )

    # IQR Outliers
    Q1 = sold_market_df[col].quantile(0.25)
    Q3 = sold_market_df[col].quantile(0.75)
    IQR = Q3 - Q1

    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR

    outliers = sold_market_df[
        (sold_market_df[col] < lower) | (sold_market_df[col] > upper)
    ]

    # 99th percentile for visualization
    upper_99 = sold_market_df[col].quantile(0.99)

    # Create figure
    fig, ax = plt.subplots(1, 3, figsize=(18, 4))

    # Histogram (Original)
    ax[0].hist(sold_market_df[col].dropna(), bins=30, edgecolor="black")

    ax[0].set_title(f"{col}\nOriginal Distribution")
    ax[0].set_xlabel(col)
    ax[0].set_ylabel("Frequency")

    # Histogram (99th percentile)
    ax[1].hist(
        sold_market_df.loc[sold_market_df[col] <= upper_99, col],
        bins=30,
        edgecolor="black",
    )

    ax[1].set_title(f"{col}\n99th Percentile")
    ax[1].set_xlabel(col)

    # Boxplot
    ax[2].boxplot(sold_market_df[col].dropna(), vert=False)

    ax[2].set_title(f"{col}\nBoxplot")

    plt.tight_layout()
    plt.show()

    print(f"Number of Outliers (IQR): {len(outliers):,}")
    print(f"Lower Bound: {lower:,.2f}")
    print(f"Upper Bound: {upper:,.2f}")

    print("\n")

# =================================================================================================
# check the reason that DaysOnMarket has negative number
sold_market_df[sold_market_df["DaysOnMarket"] < 0][
    ["ListingContractDate", "CloseDate", "DaysOnMarket"]
]
sold_market_df["Calculated_DOM"] = (
    pd.to_datetime(sold_market_df["CloseDate"])
    - pd.to_datetime(sold_market_df["ListingContractDate"])
).dt.days
sold_market_df[["ListingContractDate", "CloseDate", "DaysOnMarket", "Calculated_DOM"]]
