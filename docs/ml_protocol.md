# Machine Learning Experimental Protocol

## 1. Objective

Predict late delivery risk at the time an order is placed. Compare four models under a shared data and evaluation protocol: Logistic Regression, Random Forest, LightGBM and XGBoost. The study is observational and does not establish causation.

## 2. Shared inputs

- Dataset: `data/processed/research_data_weather_price_holiday_assume_utc.csv`.
- Candidate predictors: `docs/predictor_list.csv`.
- Split assignments: `outputs/tables/ml_preparation/split_manifest.csv`.
- Split summary: `outputs/tables/ml_preparation/split_summary.csv`.
- Preparation notebook: `notebooks/ml_data_preparation.ipynb`.

Record the dataset commit or file hash and package versions with the experiment outputs. Use the same dataset version and manifest for all four models. UTC is an assumption, not a confirmed source timezone. The Sao Paulo scenario is reserved for sensitivity analysis; never stack the two scenarios as separate orders.

The source dataset contains 99,441 unique orders and 96,470 valid delivery labels. Do not modify the source CSV to enforce a split or remove excluded orders.

## 3. Target and prediction point

- Target: `is_late`, with 1 = Late and 0 = Not Late.
- The label compares actual and estimated delivery calendar dates for eligible orders. Delivery on the estimated date is Not Late.
- Prediction point: `order_purchase_timestamp`.
- Fit and evaluation use valid labels only. Missing labels are not converted to 0.

This design studies orders that ultimately have valid delivery labels. It does not directly estimate risk for every placed order, including cancelled or unresolved orders.

## 4. Chronological split

The initial target ratio was 70/20/10, ordered by purchase date and keeping the same purchase day within one split. A 45-day maturation gap and delivery-label cutoffs were then applied. The final ratio is approximately 74/14/12; do not force it back to 70/20/10.

| Split | Purchase interval | Label requirement | Orders | Late | Share | Late rate |
|---|---|---|---:|---:|---:|---:|
| Train | Before 2018-03-02 | Actual delivery before 2018-04-16 | 57,449 | 3,720 | 73.97% | 6.48% |
| Validation A | 2018-04-16 to before 2018-05-16 | Actual delivery before 2018-07-19 | 7,661 | 387 | 9.86% | 5.05% |
| Validation B | 2018-05-16 to before 2018-06-04 | Actual delivery before 2018-07-19 | 3,115 | 180 | 4.01% | 5.78% |
| Test | 2018-07-19 onward within the original valid-labelled test cohort | Final observed labels for retrospective evaluation | 9,445 | 504 | 12.16% | 5.34% |

The test cohort ends at the last observed valid-labelled purchase, 2018-08-29 15:00:37. No future extension of the cohort is implied.

- Selected orders: **77,670**.
- Excluded valid-labelled orders: **18,800**, comprising 18,657 purchases in the gaps and 143 labels unavailable at the relevant cutoff.
- Gap intervals: `[2018-03-02, 2018-04-16)` and `[2018-06-04, 2018-07-19)`.
- Percentages use the 77,670 selected orders as the denominator.
- The manifest covers valid-labelled orders; source orders without valid labels are outside that manifest.

All order assignments must come from the manifest. Do not split randomly or independently. Join by `order_id` with a one-to-one validation and check counts against the summary. Never use manifest metadata or delivery timestamps as predictors.

Actual delivery is used as a conservative operational proxy for label availability. Historical status-update timestamps are unavailable, so exact real-time availability cannot be confirmed. Train is fitted with labels observed before 2018-04-16. Validation A and B support decisions at the 2018-07-19 boundary; their labels are not assumed available at each validation purchase date.

The 45-day gap was selected after inspecting label availability, not model metrics. All 143 remaining pending labels are ultimately Late, so excluding them creates outcome-related selection. Report this limitation and retain the 30-day gap audit as sensitivity evidence. The gaps reduce label-maturity problems but do not eliminate selection bias.

## 5. Predictor groups

The predictor list defines 21 candidate features, not a requirement to include every feature in every regression specification.

| Group | Features |
|---|---|
| F0: Basic internal | `distance_km_mean`, `customer_state`, `item_count`, `seller_count`, `purchase_hour`, `purchase_weekday`, `estimated_window_days` |
| F1: Price and product | `items_value`, `freight_value`, `total_product_weight_g`, `total_product_volume_cm3`, `product_category_count` |
| F2: Holiday | `purchase_is_national_holiday`, `days_to_next_national_holiday`, `national_holiday_count_in_estimated_window` |
| F3: Weather | `destination_rain_state_mean_mm`, `origin_rain_state_mean_mm`, `destination_humidity_state_mean_pct`, `origin_humidity_state_mean_pct`, `destination_air_temp_state_mean_c`, `origin_air_temp_state_mean_c` |

Review every Conditional availability entry before running the purchase-time experiments. Seller assignment, prices, freight, product attributes and the delivery estimate must be assumed or verified available at purchase. Document unresolved assumptions and compare a stricter feature set if needed. Confirm the historical weather windows and aggregation from the dictionary; pre-purchase observations do not prove real-time publication availability and do not measure weather along the route.

Exclude IDs, final order status, approval and delivery timestamps, approval delay, actual delivery duration, delivery delay, reviews and flags derived from later outcomes. Keep purchase timestamp and year-month for splitting and auditing, not as raw encoded predictors. Do not select predictors only because Stage 3 p-values are below 0.05.

## 6. Preprocessing

1. Load and join the shared inputs; validate IDs, labels and split counts.
2. Keep the same evaluation orders across models and feature comparisons. Do not silently drop different rows due to missing predictors.
3. Fit numeric imputation on train only, for example median imputation. Document entirely missing or constant training columns.
4. Fit categorical imputation and encoding on train only. Handle unseen categories explicitly.
5. Standardise numerical features for predictive Logistic Regression using train-fitted parameters. Tree models do not require the same scaling.
6. Preserve missing values in the source file; apply transformations through saved pipelines or equivalent reproducible code.

Models may use suitable preprocessing, but must receive the same underlying information and evaluation orders. Any learned clipping, transformations or feature selection must also be fitted on train only.

## 7. Roles

| Member | Responsibility |
|---|---|
| Viet | Shared data, predictors and manifest; LightGBM and XGBoost; consolidation and protocol review |
| Phong | Predictive Logistic Regression and Random Forest; final calibration and threshold workflow with Viet |
| Nguyen | Stage 4 explanatory logistic regression, adjusted odds ratios, confidence intervals and diagnostics |
| Chau | Stage 3 inference and cross-checking sample and variable definitions |

Stage 4 uses the shared training orders, with its own documented missing-data approach and analysis sample. It does not use SMOTE or class balancing as the primary inferential estimator. Predictive logistic regression is a separate Stage 5 experiment; do not present its regularised or class-weighted coefficients as Stage 4 inferential results.

## 8. Experiment sequence

### E1: Initial model comparison

Run all four models with all eligible F0-F3 candidates and a fixed seed of 42. Start with no class weighting, then compare the weighted configuration. This produces eight initial configurations. Save Validation A metrics and prediction files.

### E2: Limited tuning

Use approximately 10 configurations per model under a documented common search budget. Select configurations using **Average Precision on Validation A**, and inspect probability metrics and runtime. Use Validation A for early stopping if applicable; never use Validation B or test. Record the winning boosting iteration count. Repeated use of A makes its reported scores selection scores, not an unbiased final evaluation.

### E3: Added value of feature groups

On the model family selected using Validation A, compare:

- F0.
- F0 + F1.
- F0 + F2.
- F0 + F3.
- F0 + F1 + F2 + F3.

Keep hyperparameters and evaluation orders fixed to isolate the comparison as far as practical. Fit each preprocessing pipeline on train. These results concern this model and configuration, not every possible model or tuning strategy. Do not claim that external data improve prediction before observing the comparison.

### E4: Calibration and threshold

Freeze the selected classifier and feature set. Fit a sigmoid calibrator on Validation B, which was not used to fit the classifier or tune its hyperparameters. Isotonic calibration is not required in the main experiment.

Proposed alert rule: on Validation B, choose a threshold reaching Recall of at least 70%, then prefer the highest Precision among eligible thresholds. Resolve ties by the lower alert rate. Record the exact threshold, achieved Recall and alert rate. This is an experimental operating rule, not a business-validated service requirement.

Validation B is used for both calibration and threshold selection; do not claim its performance is an independent evaluation. Keep raw and calibrated probabilities for the selected model. Do not refit the classifier on additional data after calibration without rebuilding a valid calibration procedure.

### Final test evaluation

Freeze models, feature sets, weights, calibrator and thresholds before evaluating test. Evaluate the predeclared final configurations of the four model families in one final comparison; the recommended winner is selected on validation, not changed after viewing test. Report raw versus calibrated probabilities for the selected final model. Threshold-based scores for each other model require its own validation-selected threshold under the same rule.

Use test results to describe generalisation, not to select new features, weights, thresholds or hyperparameters. Subgroup and error analyses are descriptive and must not trigger undocumented tuning on the same test.

## 9. Class imbalance

| Model | Original configuration | Weighted configuration |
|---|---|---|
| Logistic Regression | `class_weight=None` | `class_weight="balanced"` |
| Random Forest | `class_weight=None` | `class_weight="balanced"` |
| LightGBM | `scale_pos_weight=1` | `scale_pos_weight=r` |
| XGBoost | `scale_pos_weight=1` | `scale_pos_weight=r` |

`r = number of Not Late training orders / number of Late training orders`.

Compute weights from the actual fitting sample only. Do not stack multiple balancing mechanisms in one initial configuration. Validation and test retain their original class distributions. Weighting is not assumed to improve AP or probability quality.

SMOTE is optional and outside the main initial comparison. If added, apply it only inside training data or training folds, and use a method suitable for mixed numeric and categorical predictors. Never resample the full dataset before splitting, or resample validation/test.

## 10. Evaluation and exports

- **Average Precision (AP):** primary ranking metric; compute with `average_precision_score`. Do not label it interchangeably with trapezoidal PR-AUC.
- **ROC-AUC:** supplementary discrimination metric.
- **Precision, Recall and F1:** classification metrics at the frozen threshold.
- **Alert rate:** predicted Late orders divided by all evaluated orders.
- **Brier Score and Log Loss:** probability quality; lower is better. Neither isolates calibration alone.
- **Calibration curve:** visual comparison of predicted probabilities and observed frequencies; state the binning rule and group sizes.
- **Confusion matrix:** TN, FP, FN and TP with Late as the positive class.

Report sample size and Late prevalence beside the metrics. Accuracy is not the primary selection measure. Report subgroup metrics only where class counts support them; mark undefined metrics rather than replacing them silently.

Suggested outputs under `outputs/tables/ml/`:

- `experiment_log.csv`: experiment ID, model, feature set, imbalance method, parameters, seed, package versions, data version, training runtime and early-stopping details.
- `model_comparison.csv`: model, configuration ID, feature set, imbalance method, split, n, Late count, AP, ROC-AUC, Brier, Log Loss, threshold, Precision, Recall, F1, alert rate, TN, FP, FN, TP and probability type.
- `validation_predictions.csv` and `test_predictions.csv`: order_id, split, model/configuration ID, y_true, raw probability, calibrated probability where applicable, prediction and threshold.
- `feature_set_comparison.csv`.
- `calibration_comparison.csv`.
- `selected_config.json`.

Save PR curves and calibration curves under `outputs/figures/ml/`. Write findings, failed configurations and limitations in `docs/ml_findings.md`. Use unique configuration IDs when consolidating outputs from different members.

## 11. Limitations and completion checks

The study uses historical, ultimately labelled orders and state-level weather summaries. The label-cutoff exclusions are not random. Original Olist timezone and real-time publication of external information are not fully verified. Test outcomes have already appeared in EDA and Stage 3, so the test cohort is not completely untouched by exploratory analysis. Freeze this modelling protocol now and disclose that limitation.

Before handoff, confirm:

- Manifest IDs are unique and splits do not overlap.
- Joined split counts match the shared summary.
- No target or post-purchase information enters predictors.
- Learned preprocessing and balancing use train only.
- Hyperparameters use Validation A; calibration and thresholds use Validation B.
- Test is not used to change model choices.
- Outputs identify data versions, model configurations and exact sample sizes.
- Statistical associations, predictive performance and causal claims are clearly separated.
