# Late Delivery in Brazilian E-Commerce - A Statistical and Machine Learning Approach.


Statistical Analysis · STAT3013.R11.CTTT · Group 5

Analyze Olist delivery patterns, test selected associations, and evaluate purchase-time risk prediction. Reviews and cancellations provide descriptive business context. The results are historical and observational; they do not establish causes or deployment readiness.

## Project scope

| Item | Summary |
|---|---|
| Research data | 99,441 unique orders, one row per order |
| Valid delivery labels | 96,470: 6,534 Late (6.77%) and 89,936 Not Late |
| Predictors | 21 basic/temporal, price/product, holiday, and weather features |
| Models | Logistic Regression, Random Forest, LightGBM, XGBoost, CatBoost |

An eligible delivered order is **Late** when its actual delivery calendar date is after its estimated date. Delivery on that date is Not Late. Cancelled, unresolved, and otherwise invalid outcomes remain unlabeled and are excluded from label-dependent analyses.

Research questions cover delivery patterns, four unadjusted associations, adjusted associations, early prediction, and descriptive reviews/cancellations. **The added predictive value of individual feature groups remains untested.** Comparing full-feature models does not answer that question.

## Statistical findings

Four two-sided tests use Holm correction across their p-values. Confidence intervals are pointwise 95%; the scope was revised after data inspection, so inference is exploratory.

| Factor | Method | Estimate [95% CI] | Holm p |
|---|---|---|---:|
| Distance | Mann–Whitney U | Rank-biserial 0.160 [0.146, 0.173] | 7.92e-102 |
| Freight | Welch t-test | Late minus Not Late: +2.641 BRL [2.049, 3.233] | 8.13e-18 |
| Holiday purchase | Chi-square | Holiday minus non-holiday: −1.928 percentage points [−2.927, −0.698] | 0.00344 |
| Destination rain | Seven-day block bootstrap | Late minus Not Late: +1.314 mm [0.794, 1.767] | 0.00100 |

All four tests reject their null hypotheses at 0.05 after correction. Effect sizes have different units; significance alone does not show business importance. Mann–Whitney is not automatically a median test.

The explanatory logistic model uses 56,553 complete-case training orders and seven-day clustered uncertainty:

| Contrast | Adjusted OR [95% CI] | Interpretation |
|---|---|---|
| Distance: 200 vs 100 km | 1.193 [1.101, 1.292] | Higher odds after adjustment |
| Freight: 20 vs 10 BRL | 1.071 [0.970, 1.183] | Association remains unclear |
| Holiday vs non-holiday | 0.593 [0.408, 0.862] | Lower observed odds; not a protective causal effect |
| Rain index: 5 vs 0 mm | 1.290 [1.168, 1.423] | Sensitive to calendar controls |

With calendar adjustment, the rain OR is about 1.036 [0.976, 1.100]. ORs are not probability changes or risk ratios. Stage 3 and Stage 4 use different samples and estimands.

Sources: [primary tests](outputs/tables/inferential_statistics/statistical_test_results.csv), [adjusted contrasts](outputs/tables/explanatory_regression/four_rq_adjusted_results.csv), [sensitivity results](outputs/tables/explanatory_regression/four_rq_sensitivity_results.csv), and [validation notes](docs/inferential_statistics/validation_review.md).

## Predictive results

All models share the same 21 predictors and chronological manifest. Preprocessing is fitted on Train only. Selected boundaries use 45-day maturation gaps and label-availability rules, excluding 18,800 labeled orders.

| Split | Orders | Late | Purpose |
|---|---:|---:|---|
| Train | 57,449 | 3,720 | Fit models |
| Validation A | 7,661 | 387 | Select configurations |
| Validation B | 3,115 | 180 | Fit calibration and select threshold |
| Test | 9,445 | 504 | Evaluate frozen decisions |

Average Precision (AP) is the primary selection metric; it measures ranking, not accuracy. ROC-AUC is supplementary. Lower Brier and Log Loss indicate better probability quality.

| Unweighted model | Validation A AP | Test AP |
|---|---:|---:|
| CatBoost | **0.09285** | 0.08284 |
| Logistic Regression | 0.09164 | 0.08124 |
| XGBoost | 0.07684 | 0.08771 |
| Random Forest | 0.07477 | **0.09781** |
| LightGBM | 0.07362 | 0.08902 |

CatBoost was selected on Validation A. Its small AP lead has no estimated uncertainty interval. Random Forest leads on Test, but Test does not change the selection. No weighted or randomly sampled configuration exceeds the original CatBoost Validation A AP. Sampling experiments are exploratory extensions after Test exposure.

Sigmoid calibration improves Brier on Validation B (0.05410 → 0.05295) but worsens it on Test (0.05014 → 0.05752). B is reused for calibration fitting and threshold selection, so its scores are not independent evaluation.

At the frozen calibrated threshold of approximately **0.05418**, Test results are:

- Recall: **94.25%**; precision: **6.42%**; F1: **0.12024**.
- Alerts: **7,397/9,445 orders (78.32%)**.
- True alerts: **475**; false alerts: **6,922**; missed Late orders: **29**.

High recall creates a large review workload. These results do not support broad automatic deployment. See the [ML protocol](docs/machine_learning/experiment_protocol.md) and [saved ML runs](outputs/tables/machine_learning/) for full metrics and provenance.

## Business implications and limits

- Low-review rates are 62.40% for Late and 9.27% for Not Late orders. Test clearer delivery updates and support; no intervention benefit has been measured.
- Distance groups range from 4.47% Late at 0–100 km to 12.04% at ≥2,000 km. Review promises and capacity for routes with repeated delays and meaningful volume.
- Risk varies by period and location. Monitor rates with sample sizes; avoid ranking sparse groups by percentages alone. Cancellations are a separate outcome: 625 orders (0.63%).
- Define an alert budget and handling costs before a pilot. Measure confirmed delays found, missed delays, workload, and customer outcomes.

The data are historical and not a random sample of all Brazilian e-commerce. Missing labels and complete-case selection can affect results. Weather is a state-level pre-purchase index; publication timing and availability of some seller/estimate inputs remain assumptions. UTC is the main scenario; do not stack timezone scenarios as extra orders.

Dependence, model form, and sparse groups limit inference. Validation A was reused, Test outcomes appeared in earlier analyses, and calibration/threshold selection share B. New evaluation data are needed for further tuning. Feature-group gains, financial savings, and intervention effects remain unvalidated.

Review figures use the **latest valid review per order**. Earlier EDA uses the first review and differs slightly. Sources: [review summary](outputs/tables/inferential_statistics/review_descriptive_summary.csv) and [cancellation summary](outputs/tables/eda/cancellation_satisfaction/status_summary.csv).

## Files and execution

| Location | Contents |
|---|---|
| `data/raw/` | Original Olist CSVs |
| `data/processed/` | Cleaned and enriched order data |
| `data/external/` | Holiday calendar and INMET inputs/outputs |
| `data/ml_preparation/` | Shared chronological manifest |
| `notebooks/` | Preprocessing, EDA, tests, regression, and ML |
| `docs/` | Dictionaries, findings, and protocol |
| `outputs/` | Tables, figures, and local model artifacts |

Use the project Python environment (recorded on Windows, CPython 3.14.6). [requirements.txt](requirements.txt) pins direct dependencies; [environment.txt](environment.txt) records the installed environment rather than a portable lockfile.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m jupyterlab
```

Run notebooks in dependency order:

1. Clean Olist tables, build the order dataset, then add temporal, price/product, and holiday features in `notebooks/01_data_preprocessing/`.
2. Prepare INMET weather, then run `merge_enriched_features.ipynb`.
3. Build the shared manifest with `notebooks/05_machine_learning/data_preparation/ml_data_preparation.ipynb`.
4. Run EDA, four-question inference, and explanatory regression.
5. Run ML baselines: Logistic/Random Forest → LightGBM/XGBoost → CatBoost.
6. Run weighted CatBoost → freeze selection → calibration → final Test evaluation. References must match the intended upstream run.
7. Run oversampling, then undersampling, as separate exploratory extensions.

Raw weather requires `data/external/inmet/raw/2016.zip`, `2017.zip`, and `2018.zip`. All three archives are tracked with Git LFS; extraction was rerun successfully on 2026-11-22. Install Git LFS before cloning, then run `git lfs pull` if the ZIPs have not been downloaded. Model binaries remain excluded from Git and are regenerated by running the ML notebooks in order.

Base construction overwrites `research_data.csv`; run temporal/enrichment steps afterward. Temporal export is currently enabled and validates the CSV before replacement. Keep backups before rebuilding. Each ML experiment stores one result set directly in its `ml_*` folder. Reruns overwrite that set. Test always uses the selected pipeline, calibrator, and threshold without retuning.

Data sources: [Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce), [INMET historical archives](https://portal.inmet.gov.br/dadoshistoricos), and [local weather preparation notes](docs/data_preprocessing/inmet_weather_preparation_review.md).
