
import os
import matplotlib.pyplot as plt

# Create the output folder if it does not exist
os.makedirs("/content/visualizations", exist_ok=True)

print("TASK 11: CREATE VISUALIZATIONS")
print("=" * 50)

# ==================================================
# TASK 11A: RETURN RATE BY PAYMENT METHOD
# ==================================================

# Sort payment methods by return rate, descending
plot_data = return_summary.sort_values(
    "return_rate_pct",
    ascending=False
)

fig, ax = plt.subplots(figsize=(8, 5))

bars = ax.bar(
    plot_data.index,
    plot_data["return_rate_pct"]
)

# Label every bar with its exact percentage
ax.bar_label(
    bars,
    labels=[
        "{:.1f}%".format(value)
        for value in plot_data["return_rate_pct"]
    ],
    padding=4
)

ax.set_title("COD Returns at 44.4% — 3x Card")
ax.set_xlabel("Payment Method")
ax.set_ylabel("Return Rate (%)")

ax.set_ylim(
    0,
    plot_data["return_rate_pct"].max() + 10
)

plt.tight_layout()

plt.savefig(
    "/content/visualizations/return_rate_by_payment.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()

print("Saved: visualizations/return_rate_by_payment.png")

# ==================================================
# TASK 11B: MONTHLY REVENUE TREND
# ==================================================

fig, ax = plt.subplots(figsize=(10, 5))

ax.plot(
    monthly_corrected.index,
    monthly_corrected.values,
    marker="o",
    linewidth=2
)

# Highlight the peak month
peak_revenue = monthly_corrected.loc[peak_month]

ax.annotate(
    "Peak: {} (₹{:,.2f})".format(
        peak_month,
        peak_revenue
    ),
    xy=(peak_month, peak_revenue),
    xytext=(10, 10),
    textcoords="offset points"
)

ax.set_title("Monthly Revenue Trend — March 2026 Is the True Peak")
ax.set_xlabel("Month")
ax.set_ylabel("Revenue (₹)")

plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig(
    "/content/visualizations/monthly_revenue_trend.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()

print("Saved: visualizations/monthly_revenue_trend.png")

# ==================================================
# TASK 7: COD RETURN-RATE HYPOTHESIS
# ==================================================

# Load the datasets
orders = pd.read_csv('/content/orders.csv')
customers = pd.read_csv('/content/customers.csv')
products = pd.read_csv('/content/products.csv')

# Standardize payment methods
orders["payment_method"] = (
    orders["payment_method"].str.strip().str.upper()
)

# Remove duplicate orders using the natural key
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

orders = orders.drop_duplicates(
    subset=duplicate_columns,
    keep="first"
).copy()

# Impute missing values
orders["discount_pct"] = orders["discount_pct"].fillna(0)
orders["rating"] = orders["rating"].fillna(orders["rating"].median())

# Merge datasets
merged = orders.merge(products, on="product_id", how="left")
merged = merged.merge(customers, on="customer_id", how="left")

# Calculate return rates
return_summary = merged.groupby(
    "payment_method"
)["returned"].agg(["count", "mean"])

return_summary["return_rate_pct"] = (
    return_summary["mean"] * 100
)

print("\nReturn rate by payment method:")
print(return_summary.round(3))
