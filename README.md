# Late Delivery in Brazilian E-Commerce

### Statistical Analysis · STAT3013.R11.CTTT · Group 5

**From order data to statistical evidence and early delivery-risk prediction.**

This course project studies late delivery in the Brazilian Olist e-commerce dataset. It combines data preparation, exploratory data analysis, statistical tests, explanatory logistic regression and machine learning. Customer reviews and cancellation provide additional business context.

The goal is to understand delivery patterns, identify selected associations and evaluate whether order information can support early risk alerts. The results describe historical transactions; they do not establish causal effects or a system ready for deployment.

[Research questions](#research-questions) · [Methods and statistical findings](#methods-and-statistical-findings) · [Machine learning results](#machine-learning-results) · [Business insights](#business-insights) · [Limitations](#limitations) · [Getting started](#getting-started)

## Project at a glance

| Item | Scope |
|---|---|
| Course | Phân tích thống kê — **STAT3013.R11.CTTT** |
| Data | Olist orders, customers, items, sellers, products, payments, reviews and geolocation; enriched with Brazilian holidays and INMET weather |
| Research sample | **99,441 orders**, one row per order |
| Valid delivery labels | **96,470**, including **6,534 Late orders (6.77%)** |
| Predictive inputs | **21 predictors**: basic/temporal, price/product, holiday and weather features |
| Learned classifiers | Logistic Regression, Random Forest, LightGBM, XGBoost and CatBoost |
| Current report | [Final Report.docx](outputs/reports/reviewed_report/Final%20Report.docx) |

An order is **Late** when its actual delivery calendar date is later than its estimated delivery date. Eligible orders delivered on or before that date are **Not Late**. Orders without a valid label, including cancelled or unresolved orders, are excluded from label-dependent analysis and are never assigned to Not Late by default.

## Research questions

| Question | Evidence and current status |
|---|---|
| **A.** How does late delivery vary across order characteristics, locations and time? | Descriptive analysis of distance, states, months and order features. |
| **B.** Which selected variables are associated with late delivery? | Four primary tests: distance, freight, purchase holiday and destination rainfall. |
| **C.** Which associations remain after adjustment for other selected variables? | Multivariable logistic regression, with calendar and block-length sensitivity checks. |
| **D.** Do price/product, holiday and weather features improve early prediction on later orders? | Full-feature model comparisons are complete. **Controlled feature-group comparisons are not yet completed**, so this question remains open. |
| **E.** How do review scores and cancellation patterns differ across groups? | Descriptive comparisons only; no review/cancellation hypothesis test or regression is claimed. |

## Methods and statistical findings

The workflow has five stages: **preprocessing → exploratory analysis → statistical inference → explanatory regression → predictive modelling**. Data preparation checks identifiers, joins, timestamps, missing values and target validity before combining order-level features.

Exploratory analysis finds late rates of **4.47%** in the 0–100 km distance group and **12.04%** at distances of at least 2,000 km. Rates also vary over time: **18.96% in March 2018**, compared with **1.16% in June 2018**. These patterns motivate temporal evaluation and careful interpretation of small groups.

### Stage 3 · Four primary tests

All tests are two-sided. Holm correction is applied across the four primary p-values; confidence intervals are pointwise 95% intervals.

| Variable | Method | Main effect | Holm p-value |
|---|---|---|---:|
| Distance | Mann–Whitney U; rank-biserial effect and bootstrap interval | Rank-biserial **0.160**, 95% CI [0.146, 0.173] | 7.92e-102 |
| Freight value | Welch two-sample t-test | Late minus Not Late: **+2.641 BRL**, CI [2.049, 3.233] | 8.13e-18 |
| Holiday purchase | Chi-square; risk difference | Holiday minus non-holiday: **−1.928 percentage points**, CI [−2.927, −0.698] | 0.00344 |
| Destination rainfall index | Seven-day temporal block bootstrap | Late minus Not Late: **+1.314 mm**, CI [0.794, 1.767] | 0.00100 |

All four tests reject their null hypotheses at 0.05 after correction. Their effects have different units, and statistical significance alone does not establish business importance. Mann–Whitney compares distributions/ranks and is not automatically a median test.

Source: [primary test results](outputs/tables/inferential_statistics/statistical_test_results.csv). See the [statistical validation review](docs/inferential_statistics/validation_review.md) for assumptions and sensitivity checks.

### Stage 4 · Adjusted delivery associations

The main explanatory logistic model uses **56,553 complete-case training orders**, transformed numerical terms and uncertainty clustered in seven-day blocks. Odds ratios describe adjusted associations, not changes in probability or causal effects.

| Contrast | Adjusted odds ratio | Pointwise 95% CI | Interpretation |
|---|---:|---|---|
| Distance: 200 vs 100 km | **1.193** | [1.101, 1.292] | Higher delivery-delay odds after adjustment. |
| Freight: 20 vs 10 BRL | **1.071** | [0.970, 1.183] | Interval includes 1; this contrast is unclear after adjustment. |
| Holiday vs non-holiday | **0.593** | [0.408, 0.862] | Lower observed odds; this does not mean holidays prevent delays. |
| Rainfall index: 5 vs 0 mm | **1.290** | [1.168, 1.423] | Sensitive to calendar controls: about **1.036 [0.976, 1.100]** after calendar adjustment. |

Sources: [main adjusted results](outputs/tables/explanatory_regression/four_rq_adjusted_results.csv), [sensitivity results](outputs/tables/explanatory_regression/four_rq_sensitivity_results.csv) and [regression findings](docs/explanatory_regression/logistic_regression_findings.md).

## Machine learning results

### Shared evaluation design

All models use the same chronological manifest and 21 predictors. Preprocessing is fitted on Train only. Selected boundaries have 45-day maturation gaps and label-availability cutoffs; **18,800 labelled orders are excluded** from the final samples.

| Split | Orders | Late orders | Purpose |
|---|---:|---:|---|
| Train | 57,449 | 3,720 | Fit preprocessing and classifiers. |
| Validation A | 7,661 | 387 | Compare and select configurations. |
| Validation B | 3,115 | 180 | Fit calibration and select the threshold. |
| Test | 9,445 | 504 | Evaluate frozen choices. |

**Average Precision (AP)** is the primary selection metric; higher is better. It measures ranking performance and is not accuracy. ROC-AUC is supplementary. Lower Brier score and Log Loss indicate better probability quality. Precision, recall, F1 and alert rate describe a chosen operating threshold.

### Five unweighted baselines

| Model | Validation A AP ↑ | Test AP ↑ | Test ROC-AUC ↑ | Test Brier ↓ | Test Log Loss ↓ |
|---|---:|---:|---:|---:|---:|
| **CatBoost — selected on A** | **0.09285** | 0.08284 | 0.67409 | 0.05014 | 0.20085 |
| Logistic Regression | 0.09164 | 0.08124 | 0.62990 | 0.05118 | 0.20698 |
| XGBoost | 0.07684 | 0.08771 | 0.68204 | 0.05059 | 0.20083 |
| Random Forest | 0.07477 | **0.09781** | **0.70379** | **0.04992** | **0.20042** |
| LightGBM | 0.07362 | 0.08902 | 0.67704 | 0.05034 | 0.20128 |

CatBoost narrowly leads on Validation A; its AP advantage over Logistic Regression is about 0.00122, without an estimated uncertainty interval. Random Forest has the highest observed Test AP, but **the model choice is not changed using Test**. The ranking changes across periods and does not establish a universally best algorithm.

Sources: [Validation A baselines](outputs/tables/machine_learning/ml_catboost/20261111_152855_922857/baseline_model_comparison.csv) and [Test comparison](outputs/tables/machine_learning/ml_test/20261111_160038_411032/test_model_comparison.csv).

### Class weighting and random sampling

Weighted CatBoost uses a Late-class weight of about **14.44**. Its Validation A AP falls to **0.07915**, compared with 0.09285 for the unweighted baseline; it is not selected. Its saved raw Test AP is 0.07391.

Random sampling is applied **only to training classifier inputs**, using preprocessing fitted on the original Train sample. The same sampled indices are shared across all five models within each method.

| Model | Baseline AP | Oversampling AP | Undersampling AP |
|---|---:|---:|---:|
| CatBoost | **0.09285** | 0.07773 | 0.07845 |
| Logistic Regression | 0.09164 | 0.09258 | 0.08765 |
| Random Forest | 0.07477 | 0.07273 | 0.07928 |
| LightGBM | 0.07362 | 0.07317 | 0.06597 |
| XGBoost | 0.07684 | 0.06585 | 0.06809 |

These are **Validation A** scores. Oversampling duplicates minority records to 53,729 per class; undersampling keeps 3,720 per class. Only Logistic Regression improves its own AP with oversampling, while only Random Forest improves with undersampling. Both methods worsen Brier and Log Loss for every model. No sampled configuration exceeds the original CatBoost baseline AP.

Sampling experiments took place after Test exposure. They are exploratory and did not change the frozen pipeline or trigger new B/Test evaluations. Source: [sampling comparison](outputs/tables/machine_learning/ml_random_undersampling/20261111_161215_292137/sampling_method_comparison.csv).

### CatBoost calibration and the frozen threshold

Sigmoid calibration is fitted on Validation B. The calibrated threshold **0.054178902872422004** is selected to achieve recall of at least 70%, prioritising precision, then lower alert rate and a larger threshold. Validation B serves both fitting and selection, so its results are not independent evaluation.

| Probability quality | Validation B: raw → calibrated | Test: raw → calibrated |
|---|---|---|
| Mean predicted probability | 2.75% → 5.78% | 5.23% → 11.81% |
| Observed late rate | 5.78% | 5.34% |
| Brier score ↓ | 0.05410 → 0.05295 | 0.05014 → 0.05752 |
| Log Loss ↓ | 0.21686 → 0.20294 | 0.20085 → 0.22789 |

| Frozen-threshold result | Validation B | Test |
|---|---:|---:|
| Precision | 10.97% | **6.42%** |
| Recall | 71.11% | **94.25%** |
| F1 | 0.19005 | **0.12024** |
| Alert rate | 37.46% | **78.32%** |
| True / false alerts | 128 / 1,039 | **475 / 6,922** |
| Missed Late orders | 52 | **29** |

Calibration improves its fitting sample but **worsens on the later Test period**. High recall comes with many false alerts: 7,397 of 9,445 Test orders are flagged. The pipeline is an experimental reference; broad automatic deployment is not supported by these results.

Sources: [calibration on B](outputs/tables/machine_learning/ml_calibration/20261111_154951_108593/calibration_comparison.csv), [Test calibration](outputs/tables/machine_learning/ml_test/20261111_160038_411032/selected_calibration_comparison.csv) and [Test threshold metrics](outputs/tables/machine_learning/ml_test/20261111_160038_411032/selected_threshold_metrics.csv).

## Business insights

| Evidence | Business implication and next step |
|---|---|
| Low-review rates are **62.40% for Late** and **9.27% for Not Late** orders; mean scores are 2.27 and 4.29. | Delivery reliability deserves attention in customer support. Test clearer status messages and early contact; the observed association does not prove that these actions improve reviews. |
| Longer routes have higher descriptive late rates and an adjusted distance OR above 1. | Review delivery promises and capacity for route/seller groups with repeated delays and substantial volume. A 200 km comparison is not an intervention cutoff. |
| Late rates and model rankings change across periods. | Monitor risk and performance by period and route. A threshold or probability correction may not transfer to the next period. |
| The frozen Test rule creates **6,922 false alerts** for 475 true alerts. | Define staff capacity and intervention costs before a pilot. Compare precision and late-order coverage within a realistic daily review budget. |
| Freight is unclear after adjustment; rainfall is sensitive to calendar controls. | Do not justify higher shipping charges or weather-based decisions from these associations alone. Test added predictive value through controlled feature-group comparisons. |
| There are **625 cancellations (0.63%)**. Sao Paulo has 327, while Rondonia has three despite its higher percentage. | Prioritise investigations using both event volume and rate. Keep cancellation separate from the delivery-delay target and avoid ranking small groups too strongly. |

Review figures use one **latest valid review per order**. Older EDA outputs select the first review and have slightly different percentages. Sources: [review summary](outputs/tables/inferential_statistics/review_descriptive_summary.csv), [review coverage](outputs/tables/inferential_statistics/review_coverage.csv) and [cancellation by state](outputs/tables/eda/cancellation_satisfaction/state_cancellation.csv).

Business value still needs a controlled pilot. Possible measures include alerts handled per day, confirmed late orders found, missed delays, support workload and customer outcomes. No intervention effect, financial saving or return on investment has been measured.

## Limitations

- **Observational and historical data:** Olist transactions are not a random sample of all Brazilian e-commerce. Associations do not establish causes.
- **Selected cohorts:** prediction requires a valid delivery label. Cancelled/unresolved orders, maturation exclusions and complete-case regression can change the population represented.
- **Information availability:** purchase-time availability of some seller, estimate and weather inputs remains an assumption. Weather publication timing and the timezone convention need further verification; state averages do not describe an exact route.
- **Dependence and model assumptions:** order-level distance bootstrap intervals and Welch tests do not fully address seller/time dependence. Block-based uncertainty and regression diagnostics also have limits; some covariance matrices are rank deficient.
- **Evaluation reuse:** Validation A was reused for selection. Test outcomes appeared earlier in exploratory/statistical analysis, and sampling followed Test exposure. Test was therefore not completely unseen in the wider research process.
- **Uncertain performance differences:** model comparisons lack uncertainty intervals. Calibration and threshold selection share Validation B, and the fitted correction transfers poorly to Test.
- **Incomplete question D:** full-feature algorithm comparison does not establish the incremental value of product/price, holiday or weather features.
- **Reconstruction and deployment:** original INMET ZIPs and frozen model binaries are not supplied in Git. Operational costs, alert budgets and intervention benefits remain unvalidated.

Further development should use an appropriate new evaluation design rather than repeatedly tuning against the existing Test results.

## Repository guide

```text
data/
  raw/                         Original Olist tables
  processed/                   Cleaned and enriched order-level data
  external/                    Holiday and processed weather inputs
  ml_preparation/              Shared split manifest and summary
docs/                          Dictionaries, findings, validation and ML protocol
notebooks/
  01_data_preprocessing/       Cleaning, aggregation and feature preparation
  02_eda/                     Delivery, time, reviews and cancellation exploration
  03_inferential_statistics/  Four primary delivery tests
  04_explanatory_regression/  Adjusted delivery associations and sensitivity
  05_machine_learning/        Baselines, selection, calibration, Test and sampling
outputs/
  tables/                     Results grouped by stage and timestamped ML run
  figures/                    Exported analytical charts
  reports/                    Current reviewed report and earlier versions
  presentations/              Existing slides and previews
  models/                     Local binary artifacts; excluded from Git
requirements.txt              Shared direct dependencies
environment.txt               Installed project environment snapshot
README.md                     Single project overview
```

| Start here | Location |
|---|---|
| Main predictive dataset | [Enriched order data](data/processed/research_data_weather_price_holiday_assume_utc.csv) |
| Predictor definitions | [21-predictor list](docs/predictor_list.csv) |
| Temporal assignments | [Split manifest](data/ml_preparation/split_manifest.csv), [summary](data/ml_preparation/split_summary.csv) |
| Statistical notebook | [Four delivery tests](notebooks/03_inferential_statistics/test_delivery_risk_associations.ipynb) |
| Explanatory notebook | [Adjusted logistic regression](notebooks/04_explanatory_regression/explain_late_delivery_logistic.ipynb) |
| ML design and frozen runs | [Experiment protocol](docs/machine_learning/experiment_protocol.md) |
| Current report/source comparison | [141 checks passed](outputs/reports/reviewed_report/cross_check_results.json) |

The reviewed DOCX is the current report; earlier generated reports are previous versions. Slides are retained as requested and contain older scope/model references. Use the current report and protocol for agreed conclusions. Word contents, figure/table lists and cross-references can be refreshed with **Ctrl+A → F9**; preserve manual edits instead of rebuilding an older report over it.

## Getting started

The recorded working environment is Windows with CPython 3.14.6. Direct dependencies are pinned in `requirements.txt`; historical experiments retain their own package-version records. The file is not a complete transitive lockfile.

[environment.txt](environment.txt) stores the shared installed environment snapshot, including transitive packages and notebook/document tools. It matches the direct dependency versions in `requirements.txt`. It is specific to the recorded Windows/Python setup and is not a portable lockfile.

Run from the repository root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m jupyterlab
```

Select the project environment as the notebook kernel. The practical workflow is:

1. Inspect source inputs and preprocessing notebooks, then EDA. Keep original raw data unchanged.
2. Prepare the shared manifest with [ml_data_preparation](notebooks/05_machine_learning/data_preparation/ml_data_preparation.ipynb); Stage 4 also depends on it. Inspect the Stage 3 and Stage 4 notebooks.
3. For ML, follow `baselines/` → `model_selection/` → `calibration/` → `test_evaluation/`. Sampling notebooks are separate exploratory extensions.
4. Inspect saved Test results. The final evaluation notebook guards against a second completed evaluation of the same frozen configuration; new upstream runs do not automatically replace frozen references.

**Before rebuilding:** original weather extraction requires `data/external/inmet/raw/2016.zip`, `2017.zip` and `2018.zip`, which are absent. Processed weather and the enriched dataset are available. The base construction notebook overwrites `research_data.csv`; temporal export defaults to `EXPORT=False` and includes a branch guard. Review these controls before rebuilding the canonical data.

**Frozen artifacts:** `outputs/models/` is excluded from Git. A clone does not restore pipelines or calibrators. Obtain matching artifacts separately and verify their recorded hashes before using the frozen configuration. Retraining creates new artifacts.

## Data sources

- [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
- [INMET historical weather observations](https://portal.inmet.gov.br/dadoshistoricos)
- Holiday provenance is recorded in the local holiday tables; [weather preparation notes](docs/data_preprocessing/inmet_weather_preparation_review.md) document aggregation and coverage.
