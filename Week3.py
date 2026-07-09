# Mortgage Rate Enrichment
import pandas as pd

sold_market_df = pd.read_csv("IDXExchange-summer-da49/sold_market_residential.csv")
listing_market_df = pd.read_csv(
    "IDXExchange-summer-da49/listing_market_residential.csv"
)

url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"

mortgage = pd.read_csv(url, parse_dates=["observation_date"])
mortgage.columns = ["date", "rate_30yr_fixed"]
print(mortgage)
# avg monthly rate
mortgage["year_month"] = mortgage["date"].dt.to_period("M")
mortgage_monthly = (
    mortgage.groupby("year_month")["rate_30yr_fixed"].mean().reset_index()
)
mortgage_monthly

# create matching year_month key on MLS Data
# sold_dataset (sold_market_df)
sold_market_df["year_month"] = pd.to_datetime(sold_market_df["CloseDate"]).dt.to_period(
    "M"
)
print(sold_market_df.head(5))
# listing_dataset (listing_market_df)
listing_market_df["year_month"] = pd.to_datetime(
    listing_market_df["ListingContractDate"]
).dt.to_period("M")
print(listing_market_df)

# Merge
# sold_market_df
sold_market_df_with_rates = sold_market_df.merge(
    mortgage_monthly, on="year_month", how="left"
)
sold_market_df_with_rates.head(5)
# listing_market_df
listing_market_df_with_rates = listing_market_df.merge(
    mortgage_monthly, on="year_month", how="left"
)
listing_market_df_with_rates.head(5)

# Check for any unmatched rows (rate should not be null)
print(sold_market_df_with_rates["rate_30yr_fixed"].isnull().sum())
print(listing_market_df_with_rates["rate_30yr_fixed"].isnull().sum())

print(
    sold_market_df_with_rates[
        ["CloseDate", "year_month", "ClosePrice", "rate_30yr_fixed"]
    ].head()
)
print(
    listing_market_df_with_rates[
        ["ListingContractDate", "year_month", "ListPrice", "rate_30yr_fixed"]
    ].head()
)
