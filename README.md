# Early Prediction of Late Delivery Risk in Brazilian E-Commerce

This project uses the **Brazilian E-Commerce Public Dataset by Olist**, enriched with product attributes, Brazilian holidays and INMET weather observations, to study delivery delays and predict risk at order placement.

The completed workflow covers preprocessing, exploratory data analysis (EDA), statistical inference, explanatory regression, predictive baselines, class weighting, calibration, threshold selection and final Test evaluation. Random oversampling and undersampling were added **after Test results had been observed** and are reported separately as exploratory analyses.

## 1. Objectives and scope

- Describe delivery delays across time, geography and order characteristics.
- Test associations and report effect sizes and uncertainty.
- Compare Logistic Regression, Random Forest, LightGBM, XGBoost and CatBoost, with DummyClassifier as a reference.
- Evaluate predicted probabilities and an operating threshold under a shared protocol.

This is an observational study of historical transactions. Results do not establish causation or demonstrate production readiness.

## 2. Repository structure

```text
data/
  raw/                         # Nine original Olist tables
  processed/                   # Cleaned tables and order-level datasets
  external/
    holidays/
    inmet/processed/           # Processed weather tables
    inmet/raw/                 # Separately supplied ZIPs; excluded from Git
  ml_preparation/               # Shared split manifest and summary
docs/
  data_preprocessing/
  eda/
  inferential_statistics/
  explanatory_regression/
  machine_learning/
  predictor_list.csv            # 21 ML predictors
notebooks/
  01_data_preprocessing/
  02_eda/
  03_inferential_statistics/
  04_explanatory_regression/
  05_machine_learning/
    data_preparation/
    baselines/
    model_selection/
    calibration/
    test_evaluation/
    sampling_experiments/
outputs/
  tables/                       # Tables grouped by analysis stage
  figures/
  models/                       # Local pipelines/calibrators; excluded from Git
  migrations/                   # Local metadata backups; excluded from Git
README.md
requirements.txt
.gitignore
```

Indexes: [documentation](docs/README.md), [notebooks](notebooks/README.md), [ML workflow](notebooks/05_machine_learning/README.md), [result tables](outputs/tables/README.md).

## 3. Dataset and target

The order-level dataset contains **99,441 orders**, with one row per `order_id`. There are **96,470 valid delivery labels**, including **6,534 Late orders**, or **6.77%** of labeled orders.

For orders eligible for labeling:

- `is_late = 1`: actual delivery calendar date is after the estimated date.
- `is_late = 0`: delivery is on or before the estimated date.
- Missing label: labeling requirements are not met; **never replace this with 0**.

Label construction also checks order status and date validity. See the [dataset dictionary](docs/data_preprocessing/order_dataset_dictionary.md) and [data quality/leakage review](docs/eda/data_quality_and_leakage_review.md).

| Shared ML input | Location |
|---|---|
| Main dataset | [research_data_weather_price_holiday_assume_utc.csv](data/processed/research_data_weather_price_holiday_assume_utc.csv) |
| 21 predictors | [predictor_list.csv](docs/predictor_list.csv) |
| Order assignments | [split_manifest.csv](data/ml_preparation/split_manifest.csv) |
| Split counts | [split_summary.csv](data/ml_preparation/split_summary.csv) |

Predictors cover internal order information, price/product characteristics, holidays and weather. The dataset also contains post-purchase outcomes: use the predictor list rather than every available column.

Original and processed CSVs are currently tracked in Git. Keep raw files unchanged. Holiday sources are recorded in the `source_url` column; the [INMET review](docs/data_preprocessing/inmet_weather_preparation_review.md) documents weather preparation and aggregation.

### Inputs required to rebuild weather from source

```text
data/external/inmet/raw/2016.zip
data/external/inmet/raw/2017.zip
data/external/inmet/raw/2018.zip
```

These three archives are not currently supplied and are excluded from Git. Processed weather tables and the ML dataset are available, so the processed-data workflow and saved results can be inspected without rebuilding the archives.

## 4. Environment setup

Validated environment: **Windows, CPython 3.14.6**. Other Python versions were not verified in this handoff.

`requirements.txt` pins direct dependencies from the working environment; pip resolves transitive dependencies. It is not a complete transitive lockfile. Each experiment retains its own `package_versions.json`, and historical runs may use different environments.

Run from the repository root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m jupyterlab
```

For VS Code, install the Python and Jupyter extensions and select `.venv\Scripts\python.exe` as the kernel. Calling the environment's Python directly avoids changing PowerShell execution policy for activation.

## 5. Notebook workflow

### Preprocessing and EDA

1. [clean_olist_tables](notebooks/01_data_preprocessing/clean_olist_tables.ipynb): clean source tables.
2. [build_order_level_dataset](notebooks/01_data_preprocessing/build_order_level_dataset.ipynb): construct the order-level dataset and target.
3. [build_temporal_features](notebooks/01_data_preprocessing/build_temporal_features.ipynb): derive temporal features.
4. Prepare [price/product](notebooks/01_data_preprocessing/build_price_product_features.ipynb), [holiday](notebooks/01_data_preprocessing/build_holiday_features.ipynb) and [weather](notebooks/01_data_preprocessing/prepare_inmet_weather.ipynb) features, then [merge the enriched dataset](notebooks/01_data_preprocessing/merge_enriched_features.ipynb).
5. [02_eda](notebooks/02_eda/): examine delivery delays, class imbalance, time patterns, cancellations, reviews and data quality.

Review exports before rebuilding the canonical dataset. The order-level construction notebook overwrites `research_data.csv`; temporal export defaults to `EXPORT=False` and still checks for branch `feat/temporal-feature-enhancement` when enabled. Running the chain without reviewing these controls can leave the dataset without its temporal additions. Weather preparation also requires the three ZIPs above. These implementation limitations remain unresolved.

### Statistical analysis and ML

| Step | Notebook / folder | Purpose |
|---|---|---|
| Split preparation | [ml_data_preparation](notebooks/05_machine_learning/data_preparation/ml_data_preparation.ipynb) | Shared manifest required by Stage 4 and predictive ML |
| Stage 3 | [test_delivery_risk_associations](notebooks/03_inferential_statistics/test_delivery_risk_associations.ipynb) | 26 primary tests, Holm correction, effect sizes and intervals |
| Stage 4 | [explain_late_delivery_logistic](notebooks/04_explanatory_regression/explain_late_delivery_logistic.ipynb) | M0/M4 explanatory models, sensitivity analyses and diagnostics; 56,553 complete cases |
| Baselines | [baselines](notebooks/05_machine_learning/baselines/) | Five learned model families and DummyClassifier |
| Selection | [model_selection](notebooks/05_machine_learning/model_selection/) | Weighted CatBoost challenger; Validation A selection and pipeline freeze |
| Calibration | [calibration_threshold](notebooks/05_machine_learning/calibration/calibration_threshold.ipynb) | Sigmoid calibration and threshold selection on B |
| Test | [final_test_evaluation](notebooks/05_machine_learning/test_evaluation/final_test_evaluation.ipynb) | Evaluation of frozen configurations |
| Post-Test extensions | [sampling_experiments](notebooks/05_machine_learning/sampling_experiments/) | Oversampling/undersampling across five models, scored on A only |

ML code is implemented directly in `.ipynb` cells. Repository discovery works from notebook subfolders. Start new experiments with a fresh kernel and follow the [ML execution guide](notebooks/05_machine_learning/README.md).

**Final Test evaluation is complete.** The Test notebook blocks a second completed evaluation of the same frozen configuration. Inspect saved outputs rather than using Test to tune models or thresholds. Selection, calibration and Test notebooks reference specific recorded runs; rerunning a baseline does not silently replace those frozen references.

## 6. Experimental design

Orders are split chronologically, keeping the same purchase day within one split and applying 45-day maturation gaps and label-availability cutoffs. Models share the same manifest rather than using independent random splits.

| Split | Orders | Late orders | Role |
|---|---:|---:|---|
| Train | 57,449 | 3,720 | Fit preprocessing and classifier |
| Validation A | 7,661 | 387 | Compare and select configurations |
| Validation B | 3,115 | 180 | Calibration and threshold selection |
| Test | 9,445 | 504 | Final evaluation |
| **Total** | **77,670** | **4,791** | Selected by the manifest |

Another 18,800 valid-labeled orders are excluded by maturation gaps or label-availability requirements. Do not force the final split back to 70/20/10.

- **Average Precision (AP)** is the primary selection metric. It is not interchangeable with trapezoidal PR-AUC.
- ROC-AUC measures discrimination; lower Brier score and Log Loss indicate better probability quality.
- Imputation, encoding and scaling learn from Train only. Logistic Regression uses scaling; CatBoost uses native categorical handling; the other tree models use one-hot encoding.
- The unweighted CatBoost baseline was selected on A. Its weighted challenger performed worse and was rejected.
- Sigmoid calibration was fitted to clipped raw log-odds on B. The threshold rule requires Recall >=70%, prioritizes Precision, then lower alert rate.
- Calibration and threshold selection share B, so B metrics are not an independent evaluation.

See [experiment_protocol.md](docs/machine_learning/experiment_protocol.md) for parameters, tie-break rules, cutoffs and scope amendments.

## 7. Main results

### Raw probabilities on Test

Test contains 9,445 orders with 5.34% Late prevalence. The ranking below was not used to reselect the model.

| Model | AP (higher) | ROC-AUC (higher) | Brier (lower) | Log Loss (lower) |
|---|---:|---:|---:|---:|
| Random Forest | **0.097815** | **0.703794** | **0.049924** | **0.200420** |
| LightGBM | 0.089018 | 0.677041 | 0.050339 | 0.201280 |
| XGBoost | 0.087707 | 0.682035 | 0.050587 | 0.200834 |
| CatBoost - selected on A | 0.082843 | 0.674094 | 0.050143 | 0.200854 |
| Logistic Regression | 0.081244 | 0.629901 | 0.051185 | 0.206977 |
| Weighted CatBoost | 0.073914 | 0.624723 | 0.176899 | 0.535125 |
| DummyClassifier | 0.053362 | 0.500000 | 0.050644 | 0.209432 |

Source: [Test comparison](outputs/tables/machine_learning/ml_test/20261111_160038_411032/seven_model_test_comparison.csv).

### Selected CatBoost at the B-frozen operating threshold

The calibrated probability threshold is **0.054178902872422004**, with predicted Late defined as `p >= threshold`.

| Test measure | Result |
|---|---:|
| Recall | 94.25% - 475 of 504 Late orders detected |
| Precision | 6.42% |
| F1 | 0.120238 |
| Alert rate | 78.32% - 7,397 orders |
| TP / FP / FN / TN | 475 / 6,922 / 29 / 2,019 |

Calibration improved B scores but **worsened Test probability quality**: Brier increased from 0.050143 to 0.057522, and Log Loss from 0.200854 to 0.227891. High recall came with a large false-alert burden; operational effectiveness has not been established.

Sources: [raw versus calibrated probabilities](outputs/tables/machine_learning/ml_test/20261111_160038_411032/selected_calibration_comparison.csv), [threshold metrics](outputs/tables/machine_learning/ml_test/20261111_160038_411032/selected_threshold_metrics.csv).

### Post-Test resampling analyses

All five model families used seed 42, identical sampled indices within each method and unchanged baseline parameters. Preprocessing was fitted on original Train before resampling classifier inputs. Validation A was not resampled.

- Oversampling: 53,729 rows per class; only Logistic Regression slightly improved AP.
- Undersampling: 3,720 rows per class; only Random Forest improved AP over its own baseline.
- Both methods worsened Brier and Log Loss for all five models.
- No resampled configuration exceeded the original CatBoost baseline AP on A. The frozen decision was not changed, and B/Test were not rescored.

Source: [baseline, oversampling and undersampling comparison](outputs/tables/machine_learning/ml_random_undersampling/20261111_161215_292137/sampling_method_comparison.csv).

## 8. Artifacts and reproducibility

| Artifact | Location |
|---|---|
| Classifier selection | [selected_config.json](outputs/tables/machine_learning/ml_selection/20261111_154450_762570/selected_config.json) |
| Calibration and threshold | [final_config.json](outputs/tables/machine_learning/ml_calibration/20261111_154951_108593/final_config.json) |
| Test evaluation audit | [evaluation_manifest.json](outputs/tables/machine_learning/ml_test/20261111_160038_411032/evaluation_manifest.json) |
| Table index | [outputs/tables/README.md](outputs/tables/README.md) |

Runs record metrics, order-level predictions, audits, parameters, package versions and input hashes. Check completion records where available and required artifacts: incomplete trial folders are retained for provenance and are not completed results.

`outputs/models/` is excluded from Git because it contains large binary artifacts. **Cloning this repository does not restore the original pipelines or calibrators.** Verifying frozen artifacts or applying them to other data requires the matching model backup and SHA256. Metrics and metadata are not substitutes for the model. Retraining creates new artifacts and does not automatically replace notebook references to frozen runs.

`outputs/reruns/` was removed; notebooks do not depend on it. `outputs/migrations/` contains local metadata backups from path reorganizations and is excluded from Git. Current metadata paths and dependent hashes were migrated together; numerical results and predictions were not recomputed during those moves.

## 9. Limitations and remaining work

- Historical Olist transactions are not a random sample of all Brazilian e-commerce.
- Prediction cohorts contain ultimately valid-labeled orders, not every canceled or unresolved order.
- Label-cutoff exclusions and complete-case regression can introduce selection bias.
- Source timezone, weather publication timing and purchase-time availability of some fields remain assumptions. State-level weather does not describe an exact delivery route.
- Actual delivery timestamps/durations, reviews and post-purchase flags must not enter the purchase-time predictor set.
- A was reused for selection; Test outcomes previously appeared in EDA/Stage 3. Resampling extensions followed Test exposure.
- Model-performance differences have no uncertainty intervals; operating costs and production alert requirements have not been validated.

Remaining descriptive work includes error/subgroup analysis and examining calibration differences between B and Test. Further model development needs a new evaluation design rather than tuning against the existing Test cohort. Supply the INMET ZIPs and review temporal export controls before rebuilding preprocessing from scratch.

## 10. Commit preparation

Keep notebooks, documentation, requirements, predictor definitions, currently tracked CSV data, split manifests, result tables and figures in Git. Exclude virtual environments, secrets, caches, binary models, raw INMET ZIPs, temporary run logs and local migration backups.

```powershell
git status --short
git diff --check
git diff --stat
git add -A
git diff --cached --stat
git diff --cached --check
git commit -m "Organize project and document final experiments"
```

Review changes before staging or committing. Reorganized files may appear as deleted old paths and untracked new paths before staging; that alone does not imply data loss. `.gitignore` does not remove previously tracked files from history.
