# Statistical and Machine Learning Analysis of Late Delivery, Customer Reviews, and Order Cancellation in Brazilian E-Commerce


Statistical Analysis · STAT3013.R11.CTTT · Group 5

Analyze Olist delivery patterns, test selected associations, and evaluate purchase-time risk prediction. Reviews and cancellations provide descriptive business context. The results are historical and observational; they do not establish causes or deployment readiness.


## Repository, dataset, and demo video

- [GitHub repository](https://github.com/Vitchann/STAT3013.R11.Group5)
- [Demo video folder (Google Drive)](https://drive.google.com/drive/u/0/folders/1zWDZ-t7i2CkViIVRE1zhI8jtckA-wciK)
- [Olist Brazilian E-Commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
- [INMET historical weather archives](https://portal.inmet.gov.br/dadoshistoricos)
- [Source-code license: MIT](#license)

The Drive link opens the folder containing the demonstration recordings.

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

## Business insights and recommendations

The five insights below correspond to the revised business-insight slides. Counts describe the historical labeled cohort unless a review or Test sample is stated. Proposed actions require a measured pilot.

| Insight | Evidence | Proposed action |
|---|---|---|
| Prioritize where late orders accumulate | São Paulo has 1,820 late orders (4.49% of 40,494 labeled orders) and Rio de Janeiro has 1,495 (12.11% of 12,350). Together they account for **50.7% of all 6,534 late orders**. | Review high-volume routes and local capacity using both late counts and rates. |
| Include busy mid-distance routes | Routes from 300 to under 1,000 km account for **3,400 late orders, or 52.0% of all late orders**. The ≥2,000 km group has a higher late rate (12.04%) but fewer affected orders. | Allocate attention across routes using volume, risk, and repeated patterns over time. |
| Extend service-quality review beyond delivery timing | Low-review rates are **62.40% for Late** and **9.27% for Not Late** among reviewed orders. However, **8,290 of 12,272 low reviews (67.6%)** come from Not Late orders. | Test proactive support for delays and investigate other complaint categories among on-time orders. |
| Investigate delay spikes beyond order volume | March 2018 has **1,328 late orders**, about **3.3 times** January's 403, while labeled volume is similar (7,003 versus 7,069). | Investigate seller, carrier, route, and capacity changes around the spike. The comparison alone does not identify its cause. |
| Pilot within a manageable alert budget | The frozen Test rule flags **78.32%** of orders, with **94.25% recall** and **6.42% precision**: 475 true alerts and 6,922 false alerts. | Set a review capacity, assign an operational owner, and measure staff time, confirmed delays, customer outcomes, and intervention costs. |

Sources: [state counts](outputs/tables/eda/late_delivery/eda04_late_rate_by_state.csv), [distance groups](outputs/tables/eda/late_delivery/eda05_late_rate_by_distance_group.csv), [latest-valid-review summary](outputs/tables/inferential_statistics/review_descriptive_summary.csv), [monthly counts](outputs/tables/eda/time_analysis/monthly_late_delivery_summary.csv), and [frozen Test metrics](outputs/tables/machine_learning/ml_test/selected_threshold_metrics.csv).

Cancellation is a separate descriptive outcome: 625 orders (0.63%). Financial savings, intervention success rates, and causal improvements have not been measured. A pilot should compare outcomes with a suitable comparison group and retain follow-up until outcomes are known.

## Interpretation limits

The data are historical and not a random sample of all Brazilian e-commerce. Missing labels and complete-case selection can affect results. Weather is a state-level pre-purchase index; publication timing and availability of some seller/estimate inputs remain assumptions. UTC is the main scenario; do not stack timezone scenarios as extra orders.

Dependence, model form, and sparse groups limit inference. Validation A was reused, Test outcomes appeared in earlier analyses, and calibration/threshold selection share B. New evaluation data are needed for further tuning. Feature-group gains, financial savings, and intervention effects remain unvalidated.

Review figures use the **latest valid review per order**. Earlier EDA uses the first review and differs slightly. Sources: [review summary](outputs/tables/inferential_statistics/review_descriptive_summary.csv) and [cancellation summary](outputs/tables/eda/cancellation_satisfaction/status_summary.csv).

## Exploratory extension: days late among late orders

The extension asks how many days an order will be late, conditional on lateness. The target is actual delivery date minus estimated delivery date, using calendar days. CatBoostRegressor uses the same 21 purchase-time features and is fitted on **3,720 late Train orders**. A fixed configuration (100 iterations, depth 6, learning rate 0.1, MAE loss, seed 42) is compared with the **Train-median baseline of 7 days** on **567 late orders from Validation A + B**.

| Validation A + B metric | Median baseline | CatBoostRegressor |
|---|---:|---:|
| MAE (days) | **4.40564** | 4.52518 |
| RMSE (days) | **6.70386** | 6.85110 |
| Absolute error within 3 days | **47.44%** | 43.03% |

The MAE difference (CatBoost minus baseline) is **+0.11954 days**, with a purchase-date bootstrap 95% interval of **[−0.02449, +0.25777]**. The experiment does not demonstrate improvement over the baseline. This regression experiment has not scored Test.

Train-only temporal diagnostics give pooled later-period MAEs of 6.40 days for the median baseline, 6.86 for CatBoost with 21 features, and 6.70 after removing six weather features. Removing weather improves this diagnostic comparison, but both CatBoost configurations remain worse than the baseline. These findings concern the tested configurations. They do not prove that the features contain no predictive information or establish weather memorization as a causal mechanism. Delivery cutoffs and changing delay distributions limit interpretation.

Explore the [factor-analysis notebooks and regression experiments](notebooks/06_delay_prediction/), [saved regression plan](outputs/tables/delay_prediction/regression_catboost/experiment_plan.json), [validation metrics](outputs/tables/delay_prediction/regression_catboost/validation_metrics.csv), and [temporal diagnostics](outputs/tables/delay_prediction/regression_train_diagnostics/pooled_metrics.csv). The weather-removal diagnostic addresses conditional delay duration; the classification feature-group question remains open.

## Files and execution

| Location | Contents |
|---|---|
| `data/raw/` | Original Olist CSVs |
| `data/processed/` | Cleaned and enriched order data |
| `data/external/` | Holiday calendar and INMET inputs/outputs |
| `data/ml_preparation/` | Shared chronological manifest |
| `notebooks/` | Preprocessing, EDA, tests, regression, and ML |
| `notebooks/06_delay_prediction/` | Delay-duration EDA, regression, and Train-only diagnostics |
| `docs/` | Dictionaries, findings, and protocol |
| `outputs/` | Tables, figures, and local model artifacts |

Use the project Python environment (recorded on Windows, CPython 3.14.6). [requirements.txt](requirements.txt) pins direct dependencies; [environment.txt](environment.txt) records the installed environment rather than a portable lockfile.

```powershell
git clone https://github.com/Vitchann/STAT3013.R11.Group5.git
cd STAT3013.R11.Group5
git lfs pull
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m ipykernel install --user --name pttk-boosting --display-name "Python (PTTK boosting)"
.\.venv\Scripts\python.exe -m jupyterlab
```

Install Git and Git LFS before cloning. Select the **Python (PTTK boosting)** kernel in Jupyter or VS Code. The pinned environment is the recorded Windows setup; compatibility with other platforms or Python versions has not been verified here.

Run notebooks in dependency order:

1. Clean Olist tables, build the order dataset, then add temporal, price/product, and holiday features in `notebooks/01_data_preprocessing/`.
2. Prepare INMET weather, then run `merge_enriched_features.ipynb`.
3. Build the shared manifest with `notebooks/05_machine_learning/data_preparation/ml_data_preparation.ipynb`.
4. Run EDA, four-question inference, and explanatory regression.
5. Run ML baselines: Logistic/Random Forest → LightGBM/XGBoost → CatBoost.
6. Run weighted CatBoost → freeze selection → calibration → final Test evaluation. References must match the intended upstream run.
7. Run oversampling, then undersampling, as separate exploratory extensions.
8. For the delay-duration extension, run `notebooks/06_delay_prediction/01_delay_factor_analysis.ipynb`, `01b_additional_delay_factor_analysis.ipynb`, `02_delay_regression_catboost.ipynb`, then `02b_delay_regression_train_diagnostics.ipynb`. The last notebook performs diagnostics within Train.

View the application demonstration through the [demo video folder](https://drive.google.com/drive/u/0/folders/1zWDZ-t7i2CkViIVRE1zhI8jtckA-wciK). This repository update publishes the notebooks and research outputs needed to inspect the experiments.

Raw weather requires `data/external/inmet/raw/2016.zip`, `2017.zip`, and `2018.zip`. All three archives are tracked with Git LFS; extraction was rerun successfully on 2026-11-22. Install Git LFS before cloning, then run `git lfs pull` if the ZIPs have not been downloaded. Model binaries remain excluded from Git and are regenerated by running the ML notebooks in order.

Base construction overwrites `research_data.csv`; run temporal/enrichment steps afterward. Temporal export is currently enabled and validates the CSV before replacement. Keep backups before rebuilding. Each ML experiment stores one result set directly in its `ml_*` folder. Reruns overwrite that set. Test always uses the selected pipeline, calibrator, and threshold without retuning.

Data sources: [Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce), [INMET historical archives](https://portal.inmet.gov.br/dadoshistoricos), and [local weather preparation notes](docs/data_preprocessing/inmet_weather_preparation_review.md).


## License

The original source code authored by STAT3013.R11 Group 5 is licensed under the MIT License below. Third-party datasets (including Olist and INMET), libraries, and other third-party materials retain their respective licenses and terms. This source-code grant does not relicense those materials.

### MIT License

Copyright (c) 2026 STAT3013.R11 Group 5

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
