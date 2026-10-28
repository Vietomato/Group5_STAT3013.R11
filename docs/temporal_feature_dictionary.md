# Temporal Feature Dictionary
- **Project:** Olist Brazilian E-Commerce – Late Delivery Analysis
- **Stage:** Stage 2 – Research Data Validation & EDA Enhancement
- **Task:** TASK 01 – Temporal Feature Engineering Enhancement
**Dataset:** `data/processed/research_data.csv`
## 1. Overview

Six temporal features were added to the order-level research dataset to support delivery performance analysis.

The enhanced dataset contains 99,441 orders and 34 columns, including 28 original columns and 6 newly engineered features.

All existing records, original variables, and `is_late` target labels are preserved.

## 2. Temporal Feature Definitions

| Feature | Definition | Calculation | Unit | Missing |
|---|---|---|---|---:|
| `purchase_hour` | Hour when the order was placed | Hour of purchase timestamp | Hour (0–23) | 0 |
| `purchase_is_weekend` | Indicates whether the order was placed on a weekend | 1 for Saturday/Sunday, otherwise 0 | Binary | 0 |
| `estimated_window_days` | Number of calendar days between purchase and estimated delivery | Estimated Date − Purchase Date | Calendar days | 0 |
| `approval_delay_hours` | Time elapsed between purchase and order approval | (Approval Timestamp − Purchase Timestamp).total_seconds() / 3600 | Continuous hours | 160 |
| `actual_delivery_days` | Time elapsed between purchase and actual delivery | (Delivery Timestamp − Purchase Timestamp).total_seconds() / 86400 | Continuous days | 2,965 |
| `delivery_delay_days` | Number of calendar days between actual and estimated delivery | Actual Delivery Date − Estimated Delivery Date | Calendar days | 2,965 |

## 3. Feature Interpretation

### 3.1. Purchase Hour

`purchase_hour` extracts the hour from `order_purchase_timestamp`.

Values range from 0 to 23.

Example: An order placed at 20:41 has `purchase_hour = 20`.

### 3.2. Purchase Is Weekend

`purchase_is_weekend` identifies orders placed on Saturday or Sunday.

- 1: Weekend purchase.
- 0: Weekday purchase.

Example: An order placed on Saturday has `purchase_is_weekend = 1`.

### 3.3. Estimated Window Days

`estimated_window_days` measures the number of calendar days between purchase and the estimated delivery date.

Example:

- Purchase date: July 24, 2018.
- Estimated delivery date: August 13, 2018.
- Estimated window: 20 days.

This feature differs from `promised_days`, which uses the approval date rather than the purchase date.

### 3.4. Approval Delay Hours

`approval_delay_hours` measures the elapsed time between purchase and approval.

Example: If an order is approved approximately 30 minutes after purchase, its approval delay is approximately 0.5 hours.

Missing values are retained when the approval timestamp is unavailable.

### 3.5. Actual Delivery Days

`actual_delivery_days` measures the continuous duration between purchase and actual customer delivery.

Example: A duration of 8.5 days represents eight days and twelve hours.

This feature is available only after delivery and is intended for retrospective analysis.

### 3.6. Delivery Delay Days

`delivery_delay_days` measures whether and by how many calendar days delivery occurred before or after the estimated date.

- Negative value: Early delivery.
- Zero: Delivery on the estimated date.
- Positive value: Late delivery.

Example: `delivery_delay_days = -8` indicates delivery eight calendar days early.

## 4. Missing Values and Data Quality

Missing values are inherited from the original timestamp columns.

No missing values were automatically imputed or replaced with zero.

Three nonnegative durations were checked for invalid negative values:

- `estimated_window_days`
- `approval_delay_hours`
- `actual_delivery_days`

No negative values were found in these features.

Statistical outliers were identified using Tukey's 1.5 × IQR rule. Outliers were retained in the dataset because extreme values do not necessarily indicate data errors.

## 5. Target Consistency

The original `is_late` definition was preserved.

For orders with valid target labels:

- `is_late = 1` when `delivery_delay_days > 0`.
- `is_late = 0` when `delivery_delay_days <= 0`.

Validation results:

| Metric | Value |
|---|---:|
| Total orders | 99,441 |
| Valid target labels | 96,470 |
| Late orders | 6,534 |
| Not Late orders | 89,936 |
| Missing target | 2,971 |
| Target mismatches | 0 |

## 6. Feature Availability and Data Leakage

| Feature | Prediction at Purchase | EDA |
|---|---|---|
| `purchase_hour` | Yes | Yes |
| `purchase_is_weekend` | Yes | Yes |
| `estimated_window_days` | Conditional: estimate must be available at purchase | Yes |
| `approval_delay_hours` | No | Yes |
| `actual_delivery_days` | No | Yes |
| `delivery_delay_days` | No | Yes |

`actual_delivery_days` and `delivery_delay_days` must not be used as predictors for purchase-time late delivery prediction because they contain post-purchase or post-delivery information.

The presence of all six features in `research_data.csv` does not imply that all six are appropriate ML predictors.

## 7. Data Consistency

The feature engineering process preserves:

- All 99,441 original records.
- All original columns and their values.
- Unique `order_id` identifiers.
- The original `is_late` definition and labels.
- Missing values in the source data.

The number of columns increased from 28 to 34 as expected.

## 8. Reproducibility

**Notebook:** `notebooks/03_temporal_feature_engineering.ipynb`

**Output:** `data/processed/research_data.csv`

The notebook can recompute the engineered features without introducing duplicate columns.

To reconstruct the enhanced dataset from the original Olist files, run the Stage 1 dataset preparation notebook before running TASK 01.

The canonical CSV should only be updated after validation checks pass.

## 9. Independent Handoff Checks

The CSV supplied for TASK 05 was independently checked: all six formulas and missing patterns matched (absolute numeric tolerance 1e-8); 96,470 orders met the labeling rules and no label mismatches were found. This does not replace execution of the TASK 04 notebook.

At purchase time, approval_delay_hours and promised_days must also be excluded because they require the realized approval timestamp. Estimated-window use remains conditional on the original estimate being available at purchase.

The export cell currently defaults to EXPORT = False and requires the Git branch feat/temporal-feature-enhancement when enabled. Regenerating the CSV on another branch will fail that guard unless it is deliberately reviewed and adapted. Do not enable export blindly.
