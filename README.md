# IDX Exchange – MLS Analytics Internship

Data Analyst Internship project for IDX Exchange's MLS Analytics & Tableau Dashboard Program.
This repo tracks the Python/Pandas work completed against the [Intern Handbook](../IDX_Exchange_Intern_Handbook_Final-version5.pdf) curriculum: cleaning CoreLogic Trestle (CRMLS) MLS listing and sold data, engineering market metrics, and (later) building Tableau dashboards.

**Data source:** Monthly `CRMLSListing*.csv` / `CRMLSSold*.csv` files (Jan 2024 – Jun 2026) pulled via FTP, stored in `../Dataset/CRMLSListing_Data/` and `../Dataset/CRMLSSold_Data/`.

Confidential — MLS data is for internal program use only, do not share or distribute externally.

## Milestone 1 (Week 0) – Data Acquisition & Orientation

Downloaded the pre-generated monthly `CRMLSListing` and `CRMLSSold` CSVs via FTP and reviewed the Trestle Property Metadata to understand field definitions, data types, and available property attributes ahead of aggregation.

## Milestone 2 (Week 1) – Monthly Dataset Aggregation

**Script:** [`Week1.py`](Week1.py)

- Concatenates all monthly Sold and Listing files from January 2024 through the most recently completed month (June 2026), preferring the `_filled` version of a month when both exist.
- Filters both combined datasets to `PropertyType == 'Residential'`.
- Saves the results as `sold_combined_residential.csv` and `listing_combined_residential.csv`.

**Outputs:**

| Dataset | Rows (Residential) | Columns |
|---|---|---|
| Sold | ~447,971 | 84 |
| Listing | ~616,050 | 84 |

## Milestone 3 (Weeks 2–3) – Dataset Structuring, Validation & EDA

**Scripts:** [`Week2.py`](Week2.py), [`EDA.ipynb`](EDA.ipynb)

- **Structure review:** row/column counts, dtype breakdown, and separation of market-analysis fields from metadata fields (agent/office identifiers, keys, addresses) for both Sold and Listing datasets.
- **Missing value analysis:** per-column null counts and percentages, with columns above the 90% threshold flagged for review (e.g. `TaxAnnualAmount`, `FireplacesTotal`, `ElementarySchoolDistrict`, `BuilderName`) and dropped from the working set; borderline fields (`WaterfrontYN`, `BasementYN`, `BuildingAreaTotal`) retained for further review.
- **Duplicate columns:** identified and dropped `.1`-suffixed duplicate columns in the Listing dataset after confirming they matched their source column.
- **Numeric distribution review:** histograms, boxplots, percentile summaries, and IQR-based outlier counts for `ClosePrice`, `ListPrice`, `OriginalListPrice`, `LivingArea`, `LotSizeAcres`, `BedroomsTotal`, `BathroomsTotalInteger`, `DaysOnMarket`, and `YearBuilt`.
- **Date consistency check:** compared recorded `DaysOnMarket` against a calculated value (`CloseDate - ListingContractDate`) and found they don't always match; flagged records with negative `DaysOnMarket` and close dates preceding listing dates.
- **EDA questions answered** (summarized in an EDA dashboard in `EDA.ipynb`):
  - Residential vs. other property type share
  - Median and average close price
  - Days on Market distribution (up to 99th percentile)
  - Share of homes sold above vs. below list price
  - Date consistency issues (close-before-listing, negative DOM records)
  - Top 10 counties by median close price

## Next Up

- Mortgage rate enrichment (FRED `MORTGAGE30US`, monthly join)
- Weeks 4–5: full data cleaning (invalid numeric values, date/geo flag columns)
- Week 6: feature engineering (price ratio, PPSF, listing/contract/close day counts, school districts)
- Week 7: IQR-based outlier flagging
- Weeks 8–12: Tableau dashboards + market intelligence report
