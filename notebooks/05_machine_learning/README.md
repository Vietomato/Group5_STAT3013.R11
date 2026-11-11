# Machine learning workflow

All ML code is in native notebooks. The main experiment and the later sampling experiments are grouped separately. Model selection, calibration and final Test evaluation are complete; saved outputs remain under their existing `outputs/` paths.

```text
05_machine_learning/
  data_preparation/
    ml_data_preparation.ipynb
  baselines/
    logistic_random_forest.ipynb
    lightgbm_xgboost.ipynb
    catboost_dummy.ipynb
  model_selection/
    catboost_weighted.ipynb
    freeze_selected_model.ipynb
  calibration/
    calibration_threshold.ipynb
  test_evaluation/
    final_test_evaluation.ipynb
  sampling_experiments/
    random_oversampling.ipynb
    random_undersampling.ipynb
```

## Main experiment

| Order | Notebook | Purpose and current status |
|---|---|---|
| 1 | [Prepare ML data](data_preparation/ml_data_preparation.ipynb) | Creates the shared chronological split manifest; also required by Stage 4 regression. |
| 2 | [Logistic Regression / Random Forest](baselines/logistic_random_forest.ipynb) | Original unweighted baselines; Train fit, Validation A scores. |
| 3 | [LightGBM / XGBoost](baselines/lightgbm_xgboost.ipynb) | Original unweighted boosting baselines and four-model comparison. |
| 4 | [CatBoost / DummyClassifier](baselines/catboost_dummy.ipynb) | CatBoost baseline and Train-prior reference; six-model comparison. |
| 5 | [Weighted CatBoost](model_selection/catboost_weighted.ipynb) | One weighted challenger; worse than the CatBoost baseline on Validation A. |
| 6 | [Freeze selected classifier](model_selection/freeze_selected_model.ipynb) | Selects CatBoost baseline on Validation A and freezes the existing fitted pipeline. |
| 7 | [Calibration and threshold](calibration/calibration_threshold.ipynb) | Fits a sigmoid calibrator and selects a Recall >=70% operating point on Validation B. |
| 8 | [Final Test evaluation](test_evaluation/final_test_evaluation.ipynb) | Completed with frozen choices; seven raw configurations plus selected calibrated/threshold results. |

The final Test notebook blocks a second completed evaluation for the same frozen configuration. Inspect existing Test outputs instead of rerunning it to tune choices. The timestamped selection and calibration records referenced by the downstream notebooks identify the completed experiment; rerunning upstream notebooks does not silently replace those frozen records.

## Post-Test exploratory experiments

| Notebook | Training sample | Scope |
|---|---|---|
| [Random oversampling](sampling_experiments/random_oversampling.ipynb) | 53,729 orders per class, 107,458 rows; minority duplicates sampled with replacement | Five unchanged classifiers; original-Train-fitted preprocessing; Validation A only. |
| [Random undersampling](sampling_experiments/random_undersampling.ipynb) | 3,720 orders per class, 7,440 unique rows; majority sampled without replacement | Five unchanged classifiers; Validation A only; includes comparison to the completed oversampling run. |

Both methods use seed 42 and share the same sampled indices across the five model families. Only Logistic Regression slightly improved AP with oversampling; only Random Forest improved AP with undersampling. Brier and Log Loss worsened for all five models with both methods. No sampling configuration exceeded the original CatBoost baseline AP. These experiments followed Test exposure and do not revise the main frozen decision or final Test results.

## Shared inputs and environment

- Dataset: `data/processed/research_data_weather_price_holiday_assume_utc.csv`.
- Predictor list: `docs/predictor_list.csv` (21 predictors).
- Split manifest and summary: `data/ml_preparation/`.
- Dependencies: the single root `requirements.txt`, Python 3.11-3.14, validated on Python 3.14.
- Select the shared project Python environment as the notebook kernel. The first cell locates the repository from any notebook subfolder.

Install from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m jupyterlab
```

[Experimental protocol](../../docs/machine_learning/experiment_protocol.md) defines model settings, selection rules and methodological limitations. Earlier runs retain their own package versions; the historical boosting environment text is reference documentation, not an installation file.

## Saved results and frozen artifacts

Output tables, models and figures remain in `outputs/tables/machine_learning/<group>/<run>/`, `outputs/models/<group>/<run>/` and `outputs/figures/<group>/<run>/`. Notebook reorganization does not alter these artifacts.

| Artifact | Repository-relative path |
|---|---|
| Weighted comparison | `outputs/tables/machine_learning/ml_catboost_weighted/20261111_153704_495324/seven_model_comparison.csv` |
| Frozen classifier selection | `outputs/tables/machine_learning/ml_selection/20261111_154450_762570/selected_config.json` |
| Frozen calibration/threshold | `outputs/tables/machine_learning/ml_calibration/20261111_154951_108593/final_config.json` |
| Final Test comparison | `outputs/tables/machine_learning/ml_test/20261111_160038_411032/seven_model_test_comparison.csv` |
| Oversampling comparison | `outputs/tables/machine_learning/ml_random_oversampling/20261111_160816_219035/oversampling_changes.csv` |
| Baseline / oversampling / undersampling | `outputs/tables/machine_learning/ml_random_undersampling/20261111_161215_292137/sampling_method_comparison.csv` |

CatBoost was selected on Validation A. Random Forest had the highest descriptive Test AP; the selection was not changed after Test. The B-fitted sigmoid calibrator worsened CatBoost probability quality on Test. At its frozen operating threshold, recall was high but false-alert volume was large. Test outcomes also appeared earlier in EDA/Stage 3; B calibration/threshold scores and post-Test sampling scores are not independent final evaluations.
