# Machine Learning Experimental Protocol

## 1. Objective

Predict late delivery risk at the time an order is placed. Compare five learned model families (Logistic Regression, Random Forest, LightGBM, XGBoost and CatBoost) plus a DummyClassifier prior reference under shared data and evaluation rules. The study is observational and does not establish causation.

Updated 2026-11-11 after observing six Validation A baseline results. Section 8 defines the current reduced experiment sequence and replaces the earlier eight-configuration, broad-tuning and feature-ablation plan. No new model family, hyperparameter search or feature-group comparison is scheduled in this revision.

## 2. Shared inputs

- Dataset: `data/processed/research_data_weather_price_holiday_assume_utc.csv`.
- Candidate predictors: `docs/predictor_list.csv`.
- Split assignments: `data/ml_preparation/split_manifest.csv`.
- Split summary: `data/ml_preparation/split_summary.csv`.
- Preparation notebook: `notebooks/05_machine_learning/data_preparation/ml_data_preparation.ipynb`.

Record the dataset commit or file hash and package versions with the experiment outputs. Use the same dataset version and manifest for all models and references. UTC is an assumption, not a confirmed source timezone. The Sao Paulo scenario is reserved for sensitivity analysis; never stack the two scenarios as separate orders.

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

CatBoost uses train-fitted numeric median imputation and a fixed missing-category token, with native categorical handling for `customer_state` and `purchase_weekday`. The other four learned baselines use one-hot encoding; their comparison therefore includes preprocessing differences as well as classifier differences. DummyClassifier ignores predictors and learns only Train class proportions.

## 7. Roles

| Member | Responsibility |
|---|---|
| Viet | Shared data, predictors and manifest; LightGBM and XGBoost; consolidation and protocol review |
| Phong | Predictive Logistic Regression and Random Forest; final calibration and threshold workflow with Viet |
| Nguyen | Stage 4 explanatory logistic regression, adjusted odds ratios, confidence intervals and diagnostics |
| Chau | Stage 3 inference and cross-checking sample and variable definitions |

Stage 4 uses the shared training orders, with its own documented missing-data approach and analysis sample. It does not use SMOTE or class balancing as the primary inferential estimator. Predictive logistic regression is a separate Stage 5 experiment; do not present its regularised or class-weighted coefficients as Stage 4 inferential results.

## 8. Current experiment sequence

### E1: Completed unweighted baselines

Five learned baselines and one constant-probability reference have been fitted on Train and scored on Validation A only (7,661 orders, 387 Late; prevalence 5.0516%). All learned baselines use the same 21 F0-F3 predictors and seed 42. No class weighting, tuning, early stopping, calibration or threshold selection has been run in these baseline notebooks.

- `notebooks/05_machine_learning/baselines/logistic_random_forest.ipynb`: Logistic Regression C=1, max_iter=3000; Random Forest 300 trees, min_samples_leaf=2.
- `notebooks/05_machine_learning/baselines/lightgbm_xgboost.ipynb`: LightGBM 100 rounds, learning rate 0.1, 31 leaves; XGBoost 100 rounds, learning rate 0.1, depth 6, hist method; 4 CPU threads.
- `notebooks/05_machine_learning/baselines/catboost_dummy.ipynb`: CatBoost 1.2.10, 100 iterations, learning rate 0.1, depth 6, random seed 42, 4 CPU threads, native categorical handling; DummyClassifier(strategy="prior") fitted on Train.

Current comparison source: `outputs/tables/machine_learning/ml_catboost_dummy/20261111_152855_922857/six_model_comparison.csv`.

| Model | AP | ROC-AUC | Brier | Log Loss |
|---|---:|---:|---:|---:|
| CatBoost | 0.092855 | 0.655757 | 0.047227 | 0.192596 |
| LogisticRegression | 0.091637 | 0.642369 | 0.047720 | 0.196408 |
| XGBoost | 0.076845 | 0.596653 | 0.047978 | 0.199795 |
| RandomForest | 0.074766 | 0.604052 | 0.048191 | 0.200893 |
| LightGBM | 0.073623 | 0.582513 | 0.048189 | 0.201357 |
| DummyClassifier | 0.050516 | 0.500000 | 0.048166 | 0.201833 |

CatBoost is the provisional Validation A leader. Its AP lead over Logistic Regression is small and has not been established as statistically reliable. The CatBoost/Dummy extension was requested after reviewing the original four baselines, so these results and the next selection step are exploratory.

### E2: One weighted CatBoost challenger

Status: completed on 2026-11-11 in `notebooks/05_machine_learning/model_selection/catboost_weighted.ipynb`. Results: `outputs/tables/machine_learning/ml_catboost_weighted/20261111_153704_495324`. No B/Test predictions were made.

Fit exactly one additional CatBoost configuration on the existing Train orders, with the same 21 predictors, categorical handling, imputation and all baseline hyperparameters. Change only class weighting:

- `class_weights=[1.0, r]`, in class order [Not Late=0, Late=1].
- `r = n_train_not_late / n_train_late = 53729 / 3720`, approximately 14.4433 for the current manifest. Compute the exact ratio from the actual Train labels; do not hard-code the rounded value.
- Do not combine this with auto_class_weights, scale_pos_weight, sample balancing or SMOTE.
- Keep 100 iterations, learning_rate=0.1, depth=6, random_seed=42 and thread_count=4. No eval_set, early stopping, tuning or other parameter changes.

Save the declared configuration and input hashes before fitting. Fit Train only; predict and score Validation A only. Compare against the unweighted CatBoost and all existing learned baselines using AP first, while reporting ROC-AUC, Brier and Log Loss. Weighting is not assumed to improve performance and may worsen probability quality.

Observed Validation A weighting comparison:

| Configuration | AP | ROC-AUC | Brier | Log Loss |
|---|---:|---:|---:|---:|
| CatBoost | 0.092855 | 0.655757 | 0.047227 | 0.192596 |
| CatBoostWeighted | 0.079147 | 0.602951 | 0.159419 | 0.499574 |

The model-selection rule in E3 is unchanged. Completing this experiment does not fit a calibrator, choose a threshold or freeze a selected configuration.

### E3: Select and freeze the classifier on Validation A

Status: completed on 2026-11-11 using `notebooks/05_machine_learning/model_selection/freeze_selected_model.ipynb`. Selected CatBoost unweighted baseline from `outputs/tables/machine_learning/ml_catboost_dummy/20261111_152855_922857`. Frozen selection record: `outputs/tables/machine_learning/ml_selection/20261111_154450_762570/selected_config.json`; pipeline: `outputs/models/ml_selection/20261111_154450_762570/CatBoostBaseline.joblib`. The copied pipeline is byte-identical to the source, verified against its saved Validation A probabilities, and was not refitted. E4 was subsequently completed as recorded below; Test was subsequently evaluated once in E5; see its completed evaluation record below.

Select the highest AP among the five unweighted learned baselines and the one weighted CatBoost challenger. DummyClassifier remains a reference and is not a selectable predictive model. Resolve numerical AP ties (absolute difference <= 1e-12) by lower Log Loss, then lower Brier, then prefer the unweighted configuration; use the configuration ID for a final deterministic tie-break. These are configuration-selection rules, not tests of statistical significance.

Freeze the selected fitted pipeline, predictor list, preprocessing, parameters, weighting, data hashes and package versions in `selected_config.json` before generating any B/Test predictions. Record the comparison source and selection rationale. The unweighted CatBoost is only the provisional leader; the frozen classifier must follow the observed E2/E3 results. Do not automatically choose the weighted variant.

No broad tuning, additional model family or feature-group ablation is included in the current reduced scope. Such experiments require another documented amendment before execution and must not use B/Test feedback. Do not claim an added predictive benefit from weather, holidays or product features without a separate feature comparison.

### E4: Calibration and operating threshold on Validation B

Status: completed on 2026-11-11 in `notebooks/05_machine_learning/calibration/calibration_threshold.ipynb`. Frozen calibration and threshold record: `outputs/tables/machine_learning/ml_calibration/20261111_154951_108593/final_config.json`. The source classifier was not refitted; Test was subsequently evaluated once in E5; see its completed evaluation record below.

Fit one sigmoid calibrator on Validation B for the frozen selected classifier. The implementation is fixed before fitting: transform the frozen raw probabilities to log-odds after clipping to [1e-6, 1-1e-6], then fit an unweighted LogisticRegression(penalty=None, solver="lbfgs", max_iter=1000, tol=1e-10) with intercept on B. This fits only the two sigmoid parameters; the CatBoost pipeline stays unchanged. Use 10 fixed equal-width [0,1] bins for calibration plots and report empty bins/counts. No alternative calibration family or probability transform is searched. B must not be used to refit its preprocessing/classifier, select a model family, change class weights or tune hyperparameters. Keep raw and calibrated probabilities; report Brier, Log Loss and calibration curves for both. Use the calibrated probabilities for the operating-threshold procedure rather than choosing the probability type after looking at Test.

On Validation B, enumerate thresholds at distinct calibrated probabilities, with predicted Late defined as probability >= threshold. Require Recall >= 70%; among eligible thresholds choose the highest Precision, then the lowest alert rate, then the largest threshold. Persist the exact numeric threshold, Recall, Precision, F1, alert rate and confusion matrix. This is an experimental rule, not a business-validated requirement; it may produce a high alert rate or low precision.

Calibration and threshold selection share Validation B, so neither its probability nor threshold metrics are an independent final evaluation. Do not refit the selected classifier on additional data after calibration without establishing a new valid calibration procedure.

Observed Validation B operating point (calibrated probability >= 0.054178902872422004): Recall 0.711111, Precision 0.109683, F1 0.190052, alert rate 0.374639. Of 3,115 orders (180 Late), TP=128, FP=1039, FN=52, TN=1896. Calibration and threshold metrics are fitting/selection results on B, not independent final performance. The high alert volume and low precision must be reported alongside recall. The frozen E4 record and its artifact hashes are the inputs to E5; no further fitting is scheduled before Test.

### E5: Final Test evaluation

Status: completed on 2026-11-11 in `notebooks/05_machine_learning/test_evaluation/final_test_evaluation.ipynb`. Final results: `outputs/tables/machine_learning/ml_test/20261111_160038_411032`. Artifact/configuration hashes were verified; no training, calibration fitting, threshold search or selection changes were performed.

Evaluate the six existing baseline/reference configurations and the single weighted challenger in one predeclared final raw-probability comparison (seven distinct configurations). Identify the selected configuration using its Validation A decision; do not switch the recommended model after seeing Test.

For the selected configuration also report calibrated probability metrics and threshold-based Precision, Recall, F1, alert rate and confusion matrix using the unchanged B-selected threshold. Other configurations need only raw AP, ROC-AUC, Brier and Log Loss in the main comparison; do not silently apply the selected model's threshold to them. Any additional threshold-based model comparison would require thresholds separately frozen on B before Test evaluation.

Use Test results to describe generalisation. Do not alter features, weights, calibrator, threshold or hyperparameters based on Test. Subgroup and error analyses are descriptive. Preserve the disclosure that Test outcomes have previously appeared in EDA and Stage 3.

Observed final Test results (9,445 orders, 504 Late): Random Forest had the highest descriptive raw AP (0.097815); the selected CatBoost baseline had raw AP 0.082843 and ROC-AUC 0.674094. This does not change the preselected CatBoost recommendation. Its B-fitted calibrator worsened Test Brier from 0.050143 to 0.057522 and Log Loss from 0.200854 to 0.227891. At the frozen calibrated threshold, Recall was 0.942460, Precision 0.064215 and alert rate 0.783166 (TP=475, FP=6922, FN=29, TN=2019). High recall came with a very high false-alert burden. These results do not demonstrate operational readiness; no model/calibration/threshold choices were revised using Test.

## 9. Class imbalance in the reduced scope

| Configuration | Class weighting | Status |
|---|---|---|
| Logistic Regression baseline | None | Completed |
| Random Forest baseline | None | Completed |
| LightGBM baseline | scale_pos_weight=1 | Completed |
| XGBoost baseline | scale_pos_weight=1 | Completed |
| CatBoost baseline | None | Completed |
| DummyClassifier prior | None; returns Train prevalence | Completed reference |
| CatBoost weighted challenger | class_weights=[1.0, n_train_not_late / n_train_late] | Completed; rejected on Validation A |

Weights use Train labels only. Validation A, B and Test retain the observed distributions and all eligible evaluation orders. Weighted variants of other families, resampling and SMOTE are outside the current reduced experiment scope. If later introduced, document the change before execution and apply resampling to training data only.

## 10. Evaluation and exports

- **Average Precision (AP):** primary ranking metric; compute with `average_precision_score`. Do not label it interchangeably with trapezoidal PR-AUC.
- **ROC-AUC:** supplementary discrimination metric.
- **Precision, Recall and F1:** classification metrics at the frozen threshold.
- **Alert rate:** predicted Late orders divided by all evaluated orders.
- **Brier Score and Log Loss:** probability quality; lower is better. Neither isolates calibration alone.
- **Calibration curve:** visual comparison of predicted probabilities and observed frequencies; state the binning rule and group sizes.
- **Confusion matrix:** TN, FP, FN and TP with Late as the positive class.

Report sample size and Late prevalence beside the metrics. Accuracy is not the primary selection measure. Report subgroup metrics only where class counts support them; mark undefined metrics rather than replacing them silently.

Suggested outputs under `outputs/tables/machine_learning/`:

- `experiment_log.csv`: experiment ID, model, feature set, imbalance method, parameters, seed, package versions, data version, training runtime and early-stopping details.
- `model_comparison.csv`: model, configuration ID, feature set, imbalance method, split, n, Late count, AP, ROC-AUC, Brier, Log Loss, threshold, Precision, Recall, F1, alert rate, TN, FP, FN, TP and probability type.
- `validation_predictions.csv` and `test_predictions.csv`: order_id, split, model/configuration ID, y_true, raw probability, calibrated probability where applicable, prediction and threshold.
- `weighting_comparison.csv`: the unweighted and weighted CatBoost comparison on Validation A.
- Feature-set comparison is deferred and is not a required output of the current reduced scope.
- `calibration_comparison.csv`.
- `selected_config.json`.

Save PR curves and calibration curves under `outputs/figures/ml/`. Write findings, failed configurations and limitations in `docs/machine_learning/ml_findings.md`. Use unique configuration IDs when consolidating outputs from different members.

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

## Supplementary extension declared 2026-11-11

After reviewing the four baseline results, add two exploratory references in `notebooks/05_machine_learning/baselines/catboost_dummy.ipynb`:

- CatBoost 1.2.10: 100 iterations, learning rate 0.1, depth 6, random seed 42, 4 CPU threads. Native categorical handling for customer state and purchase weekday; numeric medians fitted on Train and a fixed missing-category token. No class weights, tuning, eval_set, early stopping or best-iteration selection.
- DummyClassifier with strategy="prior": fit class proportions on Train only and return that constant probability on Validation A. It is a reference, not an additional learned predictor family.

Use the same 21 predictors, shared manifest and evaluation orders as the original four baselines. Fit Train only; score Validation A only. B/Test are not scored or used to select configurations. AP remains the primary comparison metric. These additions were requested after observing earlier Validation A scores, so the six-way comparison is exploratory and not an unbiased final performance estimate. The earlier broad tuning plan was not executed by this extension and is superseded by the reduced sequence in Section 8.

Save parameters before fitting, package versions, input hashes, audits, predictions, pipelines, PR curves and a six-model comparison under the `ml_catboost_dummy` output group. Require matching inputs and validation labels when consolidating earlier runs.

API references: [CatBoostClassifier](https://catboost.ai/docs/en/concepts/python-reference_catboostclassifier), [DummyClassifier](https://scikit-learn.org/stable/modules/generated/sklearn.dummy.DummyClassifier.html).

## Post-Test exploratory extension: random oversampling (2026-11-11)

Requested after final Test results were observed. Run exactly one random oversampling configuration for each of Logistic Regression, Random Forest, LightGBM, XGBoost and CatBoost. These are exploratory Validation A comparisons; the existing frozen E3/E4 decision and final Test results are not revised.

Use identical original Train orders and 21 predictors. With seed 42, sample additional Late training indices with replacement until Late and Not Late counts are equal (53,729 each; 107,458 training rows). Shuffle once with the same RNG and reuse the identical sampled indices for all five models. Keep all original Train rows. No undersampling, class weighting, SMOTE, tuning, early stopping or calibration is added.

For each model, clone its matched baseline preprocessing, fit learned transformations on original Train only, and oversample the transformed training rows before classifier fitting. This isolates resampling from changes in learned medians/scaling/encoding. Retain every baseline classifier parameter, preprocessing representation and seed. Evaluate exactly the same Validation A orders without resampling; do not score B or Test. Native CatBoost categorical handling remains unchanged.

Record original/resampled class counts, sampled indices and multiplicities, exact model parameters, input hashes, provenance, saved pipelines, validation predictions, probability metrics and pairwise changes from the matched baseline. Do not claim an independent improvement from this exploratory extension after Test exposure.

Status: completed in `notebooks/05_machine_learning/sampling_experiments/random_oversampling.ipynb`. Results: `outputs/tables/machine_learning/ml_random_oversampling/20261111_160816_219035`. All five pipeline reload checks passed; the shared oversampled Train contained 53,729 orders per class (107,458 rows), while Validation A retained 7,661 unique orders.

| Model | Baseline AP | Oversampled AP | AP change |
|---|---:|---:|---:|
| CatBoost | 0.092855 | 0.077734 | -0.015121 |
| LogisticRegression | 0.091637 | 0.092583 | +0.000946 |
| XGBoost | 0.076845 | 0.065851 | -0.010994 |
| RandomForest | 0.074766 | 0.072725 | -0.002041 |
| LightGBM | 0.073623 | 0.073173 | -0.000450 |

Only Logistic Regression had a small AP increase; the other four AP scores decreased. Brier and Log Loss increased for every model, indicating worse raw probability quality on Validation A. Oversampling did not produce a new classifier exceeding the original CatBoost baseline AP. This is a post-Test exploratory result only; no E3/E4 frozen decision or E5 Test result was revised, and no B/Test predictions were generated in this extension.

## Post-Test exploratory extension: random undersampling (2026-11-11)

Run one random undersampling configuration for each of the same five learned model families. With seed 42, retain all 3,720 Late Train rows, draw 3,720 Not Late Train indices without replacement, and shuffle once. Reuse these 7,440 indices across all five models. Do not combine undersampling with class weighting or oversampling.

Keep every baseline classifier parameter unchanged. As in the oversampling comparison, fit preprocessing on original Train only, then select transformed training rows for classifier fitting. Validation A remains unchanged; do not score B or Test. Save sampled indices/multiplicities, exact parameters, hashes, saved pipelines and metrics. Compare to matched baselines and the completed random-oversampling experiment. This extension was requested after Test exposure; it is exploratory and does not revise the frozen decision or final Test results.

Status: completed in `notebooks/05_machine_learning/sampling_experiments/random_undersampling.ipynb`. Results: `outputs/tables/machine_learning/ml_random_undersampling/20261111_161215_292137`. Every minority Train order was retained exactly once; 3,720 majority orders were selected without replacement; all five models shared the same 7,440 training indices. Validation A retained 7,661 unique orders.

| Model | Baseline AP | Random oversampling AP | Random undersampling AP |
|---|---:|---:|---:|
| CatBoost | 0.092855 | 0.077734 | 0.078447 |
| LightGBM | 0.073623 | 0.073173 | 0.065965 |
| LogisticRegression | 0.091637 | 0.092583 | 0.087645 |
| RandomForest | 0.074766 | 0.072725 | 0.079283 |
| XGBoost | 0.076845 | 0.065851 | 0.068090 |

Random Forest was the only model with higher AP under undersampling than its own baseline. All five undersampled models had worse Brier and Log Loss than their baselines. No undersampling variant exceeded the original CatBoost baseline AP. These comparisons are post-Test exploratory findings; no uncertainty interval establishes superiority, no B/Test scores were generated, and the frozen model/calibrator/threshold decision remains unchanged.
