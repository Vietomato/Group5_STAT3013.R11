# Cross-Analysis Evidence Consistency Review

**Stage:** 2 — Exploratory Data Analysis  
**Task:** TASK 07 — Cross-Analysis Evidence Consistency Review  
**Source dataset:** `data/processed/research_data.csv`  
**Branch:** `EDA---Exploratory-Data-Analysis`

## 1. Review Scope

This review checks the consistency of the main findings produced during Stage 2, focusing on dataset coverage, target labels, exploratory analysis, class imbalance, temporal features, and monthly late-delivery patterns.

The review uses the team's existing reports and independent, read-only calculations on `research_data.csv`. Its purpose is to identify numerical discrepancies, confirm consistent definitions, and document limitations before the next stage.

This task does not conduct hypothesis testing, train machine learning models, or establish causal relationships.

## 2. Dataset and Target Consistency

The research dataset contains 99,441 orders and 34 columns, with one record per order.

| Item | Verified value |
|---|---:|
| Total orders | 99,441 |
| Orders with valid target labels | 96,470 |
| Not Late orders | 89,936 |
| Late orders | 6,534 |
| Orders without valid labels | 2,971 |
| Late prevalence among labeled orders | 6.77% |
| Class imbalance ratio (Not Late : Late) | 13.76 : 1 |

The target distribution is consistent across the EDA report, Class Imbalance report, and monthly analysis.

All 96,470 labeled orders have a valid `delivery_delay_days` value. There are no mismatches between `is_late` and the rule `delivery_delay_days > 0`.

The dataset contains 2,965 missing `delivery_delay_days` values but 2,971 missing target labels. The six-order difference was reconciled: all six orders have a recorded delivery-delay value but an `order_status` of `canceled`. They remain excluded from the labeled sample.

The 96,478 orders marked `delivered` include eight orders without valid target labels.

## 3. Cross-Analysis Validation Results

| Analysis | Validation performed | Result |
|---|---|---|
| EDA01 — Target distribution | Recalculated label counts and percentages | Matched |
| EDA02 — Purchase weekday | Recalculated seven weekday groups and checked weekday values against purchase timestamps | Counts matched; one rounding discrepancy |
| EDA03 — Purchase month | Compared monthly counts and rounded rates with TASK 06 | 23/23 reported months matched |
| EDA04 — Customer state | Checked overall totals and 14 states listed in the report | Matched |
| EDA05 — Distance group | Recreated all six distance intervals and the missing-distance group | 7/7 groups matched |
| EDA06 — Freight value | Recalculated descriptive statistics for both target classes | Matched |
| EDA07 — Estimated window | Recalculated descriptive statistics and six window groups | Counts and descriptive statistics matched; one rounding discrepancy |
| EDA08 — Delivery delay | Checked distribution, percentiles, label consistency, and histogram exclusions | Matched |
| TASK 03 — Class imbalance | Verified constant-classifier baseline and four illustrative TPR/FPR scenarios | Matched |
| TASK 01 — Temporal features | Verified missing counts, purchase hour, and weekend indicator | Matched |

The validation of EDA04 directly covered the 14 states listed in the report, together with the overall totals across all 27 states. It did not independently compare every row of the full state-level CSV.

### 3.1. Monthly Analysis Consistency

TASK 06 independently reproduced the monthly late-delivery counts and rates reported in EDA03 for all 23 months containing valid labels.

The monthly summary covers 26 calendar months from September 2016 through October 2018. It also retains periods with no orders or no valid target labels instead of treating missing rates as zero.

The TASK 06 summary includes Wilson 95% confidence intervals and monthly target-label coverage information. These additions provide context for interpreting variation and sparse periods; they do not establish causal or statistically significant differences between months.

### 3.2. Missing-Value Consistency

The EDA report's missing-value counts were reproduced within the labeled sample:

| Feature | Missing labeled orders |
|---|---:|
| `distance_km_mean` | 480 |
| `promised_days` | 18 |
| `freight_value` | 0 |
| `estimated_window_days` | 0 |

Distance-related analysis therefore uses a smaller non-missing sample. EDA05 appropriately reports the 480 missing-distance orders as a separate group.

The missing-value counts for all six features in the Temporal Feature Dictionary also matched the dataset.

## 4. Discrepancies Identified

Two minor rounding discrepancies were found in `docs/eda_findings.md`.

| Location | Reported late rate | Recalculated late rate |
|---|---:|---:|
| EDA02 — Thursday | 6.31% | 6.30% |
| EDA07 — Estimated window ≤15 days | 5.91% | 5.90% |

For EDA02, the underlying counts are 903 Late orders out of 14,322 valid orders.

For EDA07, the underlying counts are 829 Late orders out of 14,039 valid orders.

The counts are correct in both cases. The differences concern the displayed percentages after rounding to two decimal places. Neither discrepancy changes the main descriptive findings.

**Recommended action:** Ask the owner of the EDA report to review these two displayed percentages. No source files were modified during this review.

## 5. Interpretation and Evidence Limitations

The analyses use consistent target definitions and generally compatible sample denominators. Differences in sample sizes are explained by missing feature values or differences in the reported scope.

The EDA findings are descriptive. Differences by weekday, state, distance, freight value, and estimated delivery window should not be treated as statistically significant or causal without further analysis.

The Class Imbalance report correctly identifies the limitations of Accuracy as a primary evaluation metric. The constant Not Late classifier achieves 93.23% Accuracy but 0% Recall for Late orders. Its reference Average Precision is the Late prevalence of the evaluation sample, approximately 0.067731 for the full labeled dataset.

The four TPR/FPR scenarios in TASK 03 were verified as mathematical illustrations, not trained-model results.

The temporal-feature review is also consistent with purchase-time prediction requirements. Actual delivery duration and delivery delay are appropriate for retrospective EDA but not as purchase-time predictors. The estimated delivery window requires confirmation that the estimate is available at prediction time.

The review does not replace a full audit of data preprocessing, exhaustive validation of every exported table, formal statistical inference, or model evaluation.

## 6. Review Conclusion and Handoff

Independent checks found no material inconsistencies in the main numerical results examined across the EDA, Class Imbalance, Temporal Feature Engineering, and Monthly Analysis outputs.

Two minor percentage-rounding discrepancies were identified in the EDA report and should be reviewed by its owner.

The existing evidence is sufficiently consistent to support the next review stage, subject to the documented scope limitations and any additional requirements from the project leader.

**TASK 07 review status:** Main numerical consistency checks completed; document prepared for leader review.

**Next step:** Submit this review together with the relevant TASK 06 outputs for feedback before any commit or push.