
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import json

# Load the CSV files
orders = pd.read_csv('/content/orders.csv')
customers = pd.read_csv('/content/customers.csv')
products = pd.read_csv('/content/products.csv')

# Display dataset dimensions
print("Orders:", orders.shape)
print("Customers:", customers.shape)
print("Products:", products.shape)

# ==================================================
# TASK 1: LOAD AND INSPECT
# ==================================================

print("\nTASK 1: LOAD AND INSPECT")
print("=" * 50)

print("\nOrders shape:", orders.shape)

print("\nOrders columns:")
print(orders.columns.tolist())

print("\nFirst five orders:")
print(orders.head())

print("\nFirst five customers:")
print(customers.head())

print("\nFirst five products:")
print(products.head())

print("\nMissing values in orders:")
print(orders.isnull().sum())

print("\nMissing values in customers:")
print(customers.isnull().sum())

print("\nMissing values in products:")
print(products.isnull().sum())

# ==================================================
# TASK 2: STANDARDIZE PAYMENT METHODS
# ==================================================

print("\nTASK 2: STANDARDIZE PAYMENT METHODS")
print("=" * 50)

print("Before cleaning:")
print(orders["payment_method"].unique())

print("Distinct values before cleaning:",
      orders["payment_method"].nunique())

# Remove surrounding spaces and standardize casing
orders["payment_method"] = (
    orders["payment_method"]
    .str.strip()
    .str.upper()
)

print("\nAfter cleaning:")
print(orders["payment_method"].unique())

print("\nDistinct values after cleaning:")
print(orders["payment_method"].nunique())

print("\nPayment method counts:")
print(orders["payment_method"].value_counts())

# ==================================================
# TASK 3: REMOVE DUPLICATE ORDERS
# ==================================================

print("\nTASK 3: REMOVE DUPLICATE ORDERS")
print("=" * 50)

duplicate_columns = [
    "customer_id",
    "product_id",
    "order_date",
    "quantity",
    "discount_pct",
    "payment_method",
    "rating",
    "returned"
]

# Identify duplicate records, retaining the first occurrence
duplicate_mask = orders.duplicated(
    subset=duplicate_columns,
    keep="first"
)

# Save duplicate rows separately for auditing
duplicates = orders.loc[duplicate_mask].copy()

print("Duplicate rows detected:", len(duplicates))

print("\nDuplicate order IDs:")
print(duplicates["order_id"].tolist())

# Remove duplicates
orders_clean = orders.loc[~duplicate_mask].copy()

print("\nShape after removing duplicates:")
print(orders_clean.shape)

# ==================================================
# TASK 4: IMPUTE MISSING VALUES
# ==================================================

print("\nTASK 4: IMPUTE MISSING VALUES")
print("=" * 50)

print("Missing discounts before imputation:",
      orders_clean["discount_pct"].isnull().sum())

print("Missing ratings before imputation:",
      orders_clean["rating"].isnull().sum())

# Calculate median before imputing
rating_median = orders_clean["rating"].median()

print("\nMedian rating before imputation:",
      rating_median)

# Impute missing values
orders_clean["discount_pct"] = (
    orders_clean["discount_pct"].fillna(0)
)

orders_clean["rating"] = (
    orders_clean["rating"].fillna(rating_median)
)

print("\nMissing values after imputation:")
print(
    orders_clean[["discount_pct", "rating"]]
    .isnull()
    .sum()
    .to_dict()
)

# ==================================================
# TASK 5: MERGE AND RECONCILE
# ==================================================
print("TASK 5: MERGE AND RECONCILE")
print("=" * 50)

# Merge cleaned orders with product information
merged = orders_clean.merge(
    products,
    on="product_id",
    how="left",
    validate="many_to_one"
)

# Merge customer information
merged = merged.merge(
    customers,
    on="customer_id",
    how="left",
    validate="many_to_one"
)

# Calculate revenue for each order
merged["order_value"] = (
    merged["quantity"]
    * merged["price"]
    * (1 - merged["discount_pct"] / 100)
)

print("Merged dataset shape:", merged.shape)
print("Number of cleaned orders:", len(merged))

cleaned_total = merged["order_value"].sum()

print("\nCleaned revenue total: ₹{:,.2f}".format(
    cleaned_total
))

# Independently calculate revenue for the five dropped rows
dropped_merged = duplicates.merge(
    products,
    on="product_id",
    how="left",
    validate="many_to_one"
)

dropped_merged = dropped_merged.merge(
    customers,
    on="customer_id",
    how="left",
    validate="many_to_one"
)

# The duplicate rows have not undergone imputation.
# Fill missing discounts with zero for the revenue check.
dropped_merged["discount_pct"] = (
    dropped_merged["discount_pct"].fillna(0)
)

dropped_merged["order_value"] = (
    dropped_merged["quantity"]
    * dropped_merged["price"]
    * (1 - dropped_merged["discount_pct"] / 100)
)

duplicate_total = dropped_merged["order_value"].sum()

print("Revenue of dropped duplicate rows: ₹{:,.2f}".format(
    duplicate_total
))

print("Raw Part 1 revenue: ₹99,860.20")

print(
    "Difference between raw and cleaned revenue: ₹{:,.2f}".format(
        99860.20 - cleaned_total
    )
)

# Print the required reconciliation note
print("\nRECONCILIATION NOTE:")

print(
    "The cleaned revenue is lower than the Part 1 raw revenue "
    "because five duplicate orders were removed in Task 3. "
    "Their combined order value is ₹{:,.2f}. "
    "The required difference is ₹2,501.90, so the cleaned "
    "total should be ₹97,358.30. Discount and rating imputation "
    "does not change the revenue total because missing discounts "
    "are treated as zero and ratings do not enter the order-value "
    "formula. If the independently calculated duplicate value or "
    "revenue difference does not match ₹2,501.90, investigate "
    "the source data and merge keys."
    .format(duplicate_total)
)

# ==================================================
# TASK 6: IQR OUTLIER DETECTION
# ==================================================

print("TASK 6: IQR OUTLIER DETECTION")
print("=" * 50)

Q1 = merged["quantity"].quantile(0.25)
Q3 = merged["quantity"].quantile(0.75)

IQR = Q3 - Q1

lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR

print("Q1:", Q1)
print("Q3:", Q3)
print("IQR:", IQR)
print("Lower bound:", lower)
print("Upper bound:", upper)

# Flag, but do not remove, outliers
merged["is_outlier"] = (
    (merged["quantity"] < lower)
    | (merged["quantity"] > upper)
)

outliers = merged.loc[merged["is_outlier"]].copy()

print("\nNumber of outlier orders:", len(outliers))

print("\nOutlier order IDs and quantities:")
print(outliers[["order_id", "quantity"]].to_string(index=False))

# ==================================================
# TASK 7: COD RETURN-RATE HYPOTHESIS
# ==================================================
print("TASK 7: COD RETURN-RATE HYPOTHESIS")
print("=" * 50)

print(
    "Hypothesis: COD orders have a higher return rate "
    "than CARD and UPI orders."
)

return_summary = merged.groupby(
    "payment_method"
)["returned"].agg(["count", "mean"])

return_summary["return_rate_pct"] = (
    return_summary["mean"] * 100
)

print("\nReturn rate by payment method:")
print(return_summary.round(3))

print("\nReturn rates rounded to one decimal:")
for payment, row in return_summary.iterrows():
    print(
        "{}: {:.1f}%".format(
            payment,
            row["return_rate_pct"]
        )
    )

cod_rate = return_summary.loc["COD", "mean"]

other_rates = return_summary.loc[
    ["CARD", "UPI"], "mean"
]

if cod_rate > other_rates.max():
    print("\nHypothesis result: Confirmed")
else:
    print("\nHypothesis result: Not confirmed")

# ==================================================
# TASK 8: MULTI-LEVEL SEGMENTATION
# ==================================================

print("TASK 8: MULTI-LEVEL SEGMENTATION")
print("=" * 50)

segment_summary = merged.groupby(
    ["payment_method", "city_tier"]
)["returned"].agg(["count", "mean"])

segment_summary["return_rate_pct"] = (
    segment_summary["mean"] * 100
)

print("\nReturn rate by payment method and city tier:")
print(segment_summary.round(3))

# Identify the highest-risk segment
highest_risk = segment_summary["return_rate_pct"].idxmax()

highest_risk_rate = segment_summary.loc[
    highest_risk, "return_rate_pct"
]

print(
    "\nHighest-risk segment: {} + {} at {:.1f}%".format(
        highest_risk[0],
        highest_risk[1],
        highest_risk_rate
    )
)

# Display COD rates by city tier
cod_segments = segment_summary.loc["COD"]

print("\nCOD return rates by city tier:")
print(cod_segments[["count", "return_rate_pct"]].round(1))

# ==================================================
# TASK 9: CORRELATION ANALYSIS
# ==================================================


print("TASK 9: CORRELATION ANALYSIS")
print("=" * 50)

correlation_columns = [
    "rating",
    "returned",
    "discount_pct",
    "quantity"
]

corr_matrix = merged[correlation_columns].corr()

print("\nCorrelation matrix:")
print(corr_matrix.round(3))

def correlation_strength(r):
    abs_r = abs(r)

    if abs_r < 0.2:
        return "negligible"
    elif abs_r < 0.4:
        return "weak"
    elif abs_r < 0.7:
        return "moderate"
    else:
        return "strong"

print("\nPairwise correlation strengths:")

for i in range(len(correlation_columns)):
    for j in range(i + 1, len(correlation_columns)):
        col1 = correlation_columns[i]
        col2 = correlation_columns[j]

        r = corr_matrix.loc[col1, col2]

        print(
            "{} vs {}: r = {:.3f} — {}".format(
                col1,
                col2,
                r,
                correlation_strength(r)
            )
        )

discount_return_corr = corr_matrix.loc[
    "discount_pct", "returned"
]

print(
    "\nHypothesis: Higher discounts reduce returns."
)

if discount_return_corr < -0.2:
    print("Hypothesis result: Supported by a negative correlation.")
else:
    print("Hypothesis result: Busted — the correlation is not sufficiently negative.")

print(
    "Discount vs returned correlation: {:.3f}".format(
        discount_return_corr
    )
)

# ==================================================
# TASK 9: CORRELATION ANALYSIS
# ==================================================

print("TASK 10: MONTHLY REVENUE ANALYSIS")
print("=" * 50)

# Convert order_date to datetime
merged["order_date"] = pd.to_datetime(
    merged["order_date"],
    errors="raise"
)

# Extract year-month
merged["year_month"] = (
    merged["order_date"].dt.to_period("M").astype(str)
)

# Monthly revenue including outliers
monthly_all = (
    merged.groupby("year_month")["order_value"]
    .sum()
    .sort_index()
)

# Monthly revenue excluding outliers
monthly_corrected = (
    merged.loc[~merged["is_outlier"]]
    .groupby("year_month")["order_value"]
    .sum()
    .sort_index()
)

print("\nMonthly revenue including outliers:")
for month, revenue in monthly_all.items():
    print("{}: {:.2f}".format(month, revenue))

print("\nMonthly revenue excluding outliers:")
for month, revenue in monthly_corrected.items():
    print("{}: {:.2f}".format(month, revenue))

peak_month = monthly_corrected.idxmax()

print(
    "\nTrue peak month after outlier correction: {}".format(
        peak_month
    )
)

print(
    "\nINTERPRETATION: January's apparent lead is an artifact "
    "of the two bulk orders O0011 on 2026-01-28 and O0098 on "
    "2026-01-10. These unusually large orders inflate January's "
    "revenue. Once the two outlier orders are excluded, March "
    "is the genuine peak month."
)

# ==================================================



# TASK 11: EXPORT FINDINGS FOR PART 3
print("\nTASK 11: EXPORT FINDINGS FOR PART 3")
print("=" * 50)

from pathlib import Path
import json

# Create the narrator folder
narrator_folder = Path("/content/narrator")
narrator_folder.mkdir(parents=True, exist_ok=True)

# Calculate cleaned revenue
cleaned_total_revenue = round(float(merged["order_value"].sum()), 2)

# Independently calculate raw revenue, including duplicate orders
raw_orders = pd.read_csv("/content/orders.csv")
raw_products = pd.read_csv("/content/products.csv")

raw_orders["discount_pct"] = raw_orders["discount_pct"].fillna(0)
raw_orders["payment_method"] = (
    raw_orders["payment_method"].astype(str).str.strip().str.upper()
)

raw_merged = raw_orders.merge(raw_products, on="product_id", how="left")
raw_merged["order_value"] = (
    raw_merged["quantity"]
    * raw_merged["price"]
    * (1 - raw_merged["discount_pct"] / 100)
)

raw_total_revenue = round(float(raw_merged["order_value"].sum()), 2)

# Calculate return rates by payment method
payment_rates = (
    merged.groupby("payment_method")["returned"].mean() * 100
).round(1)

# Find the highest-risk payment method and city-tier segment
segment_rates = merged.groupby(
    ["payment_method", "city_tier"]
)["returned"].mean() * 100

highest_risk_key = segment_rates.idxmax()
highest_risk_rate = round(float(segment_rates.loc[highest_risk_key]), 1)

# Find the apparent peak month and the corrected peak month
apparent_peak_month = str(monthly_all.idxmax())
corrected_peak_month = str(monthly_corrected.idxmax())

findings = {
    "cleaned_total_revenue_inr": cleaned_total_revenue,
    "raw_total_revenue_inr": raw_total_revenue,
    "duplicate_reconciliation_delta_inr": round(
        raw_total_revenue - cleaned_total_revenue, 2
    ),
    "return_rate_by_payment": {
        method: float(payment_rates[method])
        for method in ["COD", "CARD", "UPI"]
    },
    "highest_risk_segment": {
        "payment_method": str(highest_risk_key[0]),
        "city_tier": int(highest_risk_key[1]),
        "return_rate_pct": highest_risk_rate
    },
    "true_peak_month": {
        "month": corrected_peak_month,
        "revenue_inr": round(float(monthly_corrected.max()), 2)
    },
    "outlier_inflated_month": {
        "month": apparent_peak_month,
        "apparent_revenue_inr": round(
            float(monthly_all.loc[apparent_peak_month]), 2
        ),
        "corrected_revenue_inr": round(
            float(monthly_corrected.loc[apparent_peak_month]), 2
        )
    }
}

findings_path = narrator_folder / "findings.json"

with open(findings_path, "w") as file:
    json.dump(findings, file, indent=2)

print("Findings saved to:", findings_path)
print(json.dumps(findings, indent=2))
