# Analysis tables

Tables are grouped by analysis stage. CSV filenames and numeric contents are preserved; ML run timestamps still identify the original experiments. Notebook outputs were not recalculated during this reorganization.

```text
tables/
  data_preprocessing/
    combined_features/
    weather/
  eda/
    late_delivery/
    class_imbalance/
    time_analysis/
    cancellation_satisfaction/
    enriched_features/
    data_quality/
  inferential_statistics/
  explanatory_regression/
  machine_learning/
    ml_logistic_random_forest/
    ml_lightgbm_xgboost/
    ml_catboost_dummy/
    ml_catboost_weighted/
    ml_selection/
    ml_calibration/
    ml_test/
    ml_random_oversampling/
    ml_random_undersampling/
  validation/
```

## Groups

| Folder | Contents |
|---|---|
| [data_preprocessing](data_preprocessing/) | Combined-feature summaries and weather preparation/coverage checks. |
| [eda](eda/) | Delivery patterns, class imbalance, time analysis, cancellations/reviews, enriched features and data-quality checks. |
| [inferential_statistics](inferential_statistics/) | Primary tests, Holm correction, descriptive/sample summaries and weather tests. |
| [explanatory_regression](explanatory_regression/) | Adjusted odds ratios, complete-case sample accounting and regression diagnostics. |
| [machine_learning](machine_learning/) | Baseline/model-selection/calibration/Test and exploratory resampling outputs, each retaining timestamped run folders. |
| [validation](validation/) | Shared environment verification metadata. |

## Main ML results

- [Seven configurations on Validation A](machine_learning/ml_catboost_weighted/20261111_153704_495324/seven_model_comparison.csv).
- [Frozen classifier selection](machine_learning/ml_selection/20261111_154450_762570/selected_config.json).
- [Frozen calibration and threshold](machine_learning/ml_calibration/20261111_154951_108593/final_config.json).
- [Final Test model comparison](machine_learning/ml_test/20261111_160038_411032/seven_model_test_comparison.csv).
- [Selected CatBoost Test threshold metrics](machine_learning/ml_test/20261111_160038_411032/selected_threshold_metrics.csv).
- [Baseline / oversampling / undersampling comparison](machine_learning/ml_random_undersampling/20261111_161215_292137/sampling_method_comparison.csv).

Sampling experiments followed Test exposure and are exploratory; they did not replace the frozen CatBoost decision. Existing incomplete trial folders are retained for provenance and must not be treated as completed experiments without checking their completion records.

## Path migration

Notebook code, documentation, archived runners and artifact metadata use the new table paths. Models and figures remain at their original locations. Frozen JSON path references and dependent content hashes were migrated together; no model was refitted or recalibrated. Original metadata, old/new paths and old/new hashes are archived under `outputs/migrations/` for verification. All numeric CSVs and predictions are byte-identical to their pre-move versions; the Test model registry CSV changed only its source table paths.
