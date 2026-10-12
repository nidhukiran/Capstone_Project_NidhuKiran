# Mamaearth Growth Analytics
## Order Returns, Revenue Integrity, and Business Insights

### 1. Project Overview
This project analyzes Mamaearth order data to investigate revenue reconciliation, data quality, and product return patterns.

### 2. Business Objectives
- Clean and validate order data.
- Identify duplicate order records.
- Handle missing values.
- Identify unusual order quantities.
- Analyze return rates by payment method and city tier.
- Evaluate the relationship between discounts and returns.
- Communicate findings through visualizations and a business narrative.

### 3. Tools and Technologies
- Python
- Pandas
- SQLite
- SQL
- Matplotlib
- JSON
- Google Colab
- Gemini API for narrative generation

### 4. Data Sources
The project uses three CSV files:
- orders.csv
- customers.csv
- products.csv

The original datasets contain 180 order records, 45 customer records, and 16 product records.

### 5. Database
The SQLite database is named `mamaearth.db` and contains three tables:
- orders
- customers
- products

### 6. Data Cleaning
The analysis includes:
- Standardizing payment method values.
- Identifying and removing five duplicate order records.
- Replacing 12 missing discount values with zero.
- Replacing 15 missing ratings with the median rating of 3.0.
- Flagging two unusually large order quantities for investigation.

The cleaned order dataset contains 175 records.

### 7. Key Findings

#### Revenue Reconciliation
- Raw revenue: ₹99,860.20
- Cleaned revenue: ₹97,358.30
- Duplicate reconciliation difference: ₹2,501.90

The difference is associated with duplicate-order reconciliation.

#### Return Rates by Payment Method
- COD: 44.4%
- CARD: 14.7%
- UPI: 18.9%

COD has the highest observed return rate.

#### Highest-Risk Segment
The Tier 2 city COD segment has an observed return rate of 54.5%. Further investigation is recommended to understand the reasons behind this pattern.

#### Monthly Revenue
March 2026 is the peak month in the analysis, with revenue of ₹20,318.90.

January 2026 revenue was ₹29,582.10 when the two flagged quantity outliers were included. Excluding these orders for sensitivity analysis reduces January revenue to ₹11,637.10.

The outlier-excluded figure is a sensitivity-analysis result, not a confirmed correction to official revenue. The orders should be investigated before deciding whether to exclude them from reporting.

#### Discount and Returns
The analysis did not support the hypothesis that higher discounts reduce returns. Correlation alone cannot establish causation. Controlled testing is recommended.

### 8. Visualizations
- `monthly_revenue_trend.png` — monthly revenue trend.
- `return_rate_by_payment.png` — return rates by payment method.

### 9. Business Recommendations
1. Introduce validation checks for unusually large order quantities.
2. Strengthen duplicate-order detection and reconciliation.
3. Investigate high COD returns, particularly in Tier 2 cities.
4. Monitor return rates by payment method and city tier.
5. Conduct controlled experiments before claiming that discounts reduce returns.
6. Maintain an audit trail for data-cleaning decisions.

### 10. Limitations
The findings describe patterns in the available dataset and do not establish causal relationships. Unusually large order quantities have been flagged for investigation and should not automatically be treated as invalid transactions.

The results should not be generalized to all Mamaearth orders without further validation.

### 11. Conclusion
The analysis identifies a revenue reconciliation difference associated with duplicate orders and elevated return rates for COD transactions, particularly in Tier 2 cities.

Improved data validation, order reconciliation, segment-level monitoring, and evidence-based experimentation can help improve reporting reliability.

### 12. How to Run
The project was developed in Google Colab.

1. Upload the CSV datasets.
2. Run the data-cleaning and exploratory-analysis script.
3. Run the visualization script.
4. Review the findings and generated narrative.
5. Use the SQLite database to inspect and query the source tables.

Check the individual Python scripts for their exact input paths and execution requirements before running them in another environment.
