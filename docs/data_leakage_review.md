# Data Quality and Leakage Review

## 1. Objective and Scope

This review checks dataset structure, temporal feature consistency, target eligibility, missing values, and feature availability for early late-delivery prediction.

Purchase time is used as the reference prediction point. The final cutoff must be confirmed before modeling because purchase-time and approval-time prediction permit different information.

The review uses data/processed/research_data.csv. Calculations are documented in [the review notebook](../notebooks/06_data_leakage_review.ipynb).

## 2. Dataset and Target Validation

The dataset contains one row per order.

| Item | Orders |
|---|---:|
| Total orders | 99,441 |
| Valid labeled orders | 96,470 |
| Late orders | 6,534 |
| Not Late orders | 89,936 |
| Missing target | 2,971 |

There are 34 columns, with no missing or duplicated order_id values. Observed target values are restricted to 0 and 1.

Eligible orders must have delivered status, valid purchase, actual delivery, and estimated delivery timestamps, and actual delivery not preceding purchase. Late delivery is defined using calendar dates.

Independent reconstruction found no eligibility or label-value mismatches. All labeled orders have delivery_delay_days values consistent with their labels.

Six canceled orders have delivery-delay values but no valid labels. These orders remain excluded from the labeled sample. Eight orders marked delivered also lack valid labels.

## 3. Temporal Feature Quality

All five timestamp columns were parsed without introducing additional missing values. The six temporal features matched their source timestamps, with no numeric parsing failures, missing-pattern mismatches, or value mismatches.

| Feature | Missing orders |
|---|---:|
| purchase_hour | 0 |
| purchase_is_weekend | 0 |
| estimated_window_days | 0 |
| approval_delay_hours | 160 |
| actual_delivery_days | 2,965 |
| delivery_delay_days | 2,965 |

The seven temporal range checks passed. Negative delivery_delay_days values represent early delivery and are valid.

### Timestamp Anomalies

| Observation | Flagged orders |
|---|---:|
| Approval before purchase | 0 |
| Carrier handoff before purchase | 166 |
| Customer delivery before carrier handoff | 23 |
| Customer delivery before purchase | 0 |
| Carrier handoff before approval | 1,359 |

These groups may overlap. Their counts must not be added to estimate the number of distinct affected orders. Original timestamps are retained because the review does not establish corrected values.

### Potential Outliers

Tukey's 1.5 × IQR rule was applied to all nonmissing observations of each duration feature.

| Feature | Flagged orders |
|---|---:|
| estimated_window_days | 2,464 |
| approval_delay_hours | 9,141 |
| actual_delivery_days | 4,899 |
| delivery_delay_days | 4,301 |

Actual delivery duration exceeds 180 days for 14 orders. All flagged observations are retained. IQR flags identify unusual values but do not establish data errors.

## 4. EDA Sample Coverage

Missing-value counts depend on the analysis population.

Within the 96,470 labeled orders, distance_km_mean is missing for 480 orders and promised_days is missing for 18 orders. Freight value and estimated_window_days have no missing values in this sample.

The 18 missing promised_days values comprise 14 absent approval timestamps and four negative raw durations converted to missing. Across the full dataset, the corresponding counts are 160 and 10, totaling 170.

Stored promised_days values and missing patterns match the documented approval-based formula. This variable differs from estimated_window_days, which starts from purchase.

This notebook checks feature coverage within the labeled sample. The broader numerical consistency review of Stage 2 results is documented separately in [TASK 07](cross_analysis_consistency_review.md).

## 5. Feature Availability and Leakage

All 34 columns were reviewed using their source definitions and information dependencies.

| Availability | Columns |
|---|---:|
| Available at purchase | 5 |
| Conditional | 13 |
| Post-purchase | 13 |
| Identifier | 2 |
| Target | 1 |

The complete classification and reasons are provided in [feature_leakage_review.csv](../outputs/tables/data_quality/feature_leakage_review.csv).

### Direct and Post-Purchase Leakage

For eligible labeled orders, delivery_delay_days > 0 determines is_late directly. This variable must not enter early prediction inputs.

Actual delivery timestamps and durations contain future outcome information. Carrier timestamps, final order_status, and post-purchase quality flags also depend on later order progression. Their values and missingness must be excluded from purchase-time predictors.

order_approved_at, approval_delay_hours, and promised_days require realized approval. They may be reconsidered only if the team explicitly selects approval-time prediction and confirms that all required information is available before scoring.

### Conditional Features

Delivery estimates, customer location, item totals, freight charges, and seller assignments require confirmation that the recorded values correspond to the prediction point rather than later updates.

Distance and geographic coverage variables additionally require an appropriate geographic lookup available at that point. Conditional classification does not constitute approval for modeling.

Identifiers support linkage and traceability. is_late is the outcome and must never be included as an input feature.

## 6. Requirements Before Modeling

- Confirm the prediction cutoff and an explicit predictor list.
- Resolve availability assumptions for conditional features.
- Fit imputation, scaling, encoding, learned outlier rules, and any resampling on training data only.
- Use validation data for decision-threshold selection and preserve the test set for final evaluation.
- Account for delivery-outcome lag when creating chronological splits. Training labels must have been observable at the training cutoff.
- Consider dependence across customers, sellers, and time. customer_id alone cannot identify repeated customers across orders; that requires customer_unique_id.

The historical dataset supports retrospective analysis, but its contents are not automatically an approved ML feature matrix.

## 7. Reproducibility and Limitations

Run notebooks/06_data_leakage_review.ipynb from the repository root or notebooks directory using a fresh kernel. Review tables are exported to outputs/tables/data_quality.

The source CSV was read again and matched the original loaded data. No source values or orders were changed during this review.

The findings cover the implemented checks. They do not independently verify operational feature availability, explain timestamp anomalies, or establish predictive performance. The final prediction cutoff and conditional feature assumptions remain open for team confirmation.