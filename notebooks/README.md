# Notebook workflow

Notebooks are grouped by stage. Run cells from the beginning in a fresh kernel. The first cell locates the repository and sets its root as the working directory; data and outputs remain in the shared `data/` and `outputs/` folders.

Install the shared dependencies from the repository root with `python -m pip install -r requirements.txt`. Use the same environment as the notebook kernel. See [validation results](../docs/inferential_statistics/validation_review.md).

## Execution order

1. Clean raw tables with `01_data_preprocessing/clean_olist_tables.ipynb`.
2. Build the order-level research dataset with `01_data_preprocessing/build_order_level_dataset.ipynb`.
3. Run temporal, price/product, holiday and weather preparation; then combine features. Weather preparation also requires the external INMET archives.
4. Run EDA and Stage 3 inference.
5. Run `05_machine_learning/data_preparation/ml_data_preparation.ipynb` to create shared split assignments before Stage 4 regression or predictive model training.
6. Review Stage 4 regression and run Stage 5 notebooks following their README. Existing predictive baselines score Validation A only.

## Data preprocessing and feature engineering

- [clean_olist_tables.ipynb](01_data_preprocessing/clean_olist_tables.ipynb)
- [build_order_level_dataset.ipynb](01_data_preprocessing/build_order_level_dataset.ipynb)
- [build_temporal_features.ipynb](01_data_preprocessing/build_temporal_features.ipynb)
- [merge_enriched_features.ipynb](01_data_preprocessing/merge_enriched_features.ipynb)
- [build_holiday_features.ipynb](01_data_preprocessing/build_holiday_features.ipynb)
- [build_price_product_features.ipynb](01_data_preprocessing/build_price_product_features.ipynb)
- [prepare_inmet_weather.ipynb](01_data_preprocessing/prepare_inmet_weather.ipynb)

## Exploratory data analysis (EDA)

- [explore_late_delivery.ipynb](02_eda/explore_late_delivery.ipynb)
- [analyze_class_imbalance.ipynb](02_eda/analyze_class_imbalance.ipynb)
- [review_data_leakage.ipynb](02_eda/review_data_leakage.ipynb)
- [analyze_monthly_delivery_patterns.ipynb](02_eda/analyze_monthly_delivery_patterns.ipynb)
- [explore_cancellations_and_reviews.ipynb](02_eda/explore_cancellations_and_reviews.ipynb)
- [explore_enriched_features.ipynb](02_eda/explore_enriched_features.ipynb)

## Stage 3 - Inferential statistics

- [test_delivery_risk_associations.ipynb](03_inferential_statistics/test_delivery_risk_associations.ipynb)

## Stage 4 - Explanatory regression

- [explain_late_delivery_logistic.ipynb](04_explanatory_regression/explain_late_delivery_logistic.ipynb)

## Stage 5 - Machine learning

See the [ML workflow and saved results](05_machine_learning/README.md) for execution order and completed status.

| Group | Notebooks |
|---|---|
| Data preparation | [ml_data_preparation](05_machine_learning/data_preparation/ml_data_preparation.ipynb) |
| Baselines | [logistic_random_forest](05_machine_learning/baselines/logistic_random_forest.ipynb), [lightgbm_xgboost](05_machine_learning/baselines/lightgbm_xgboost.ipynb), [catboost_dummy](05_machine_learning/baselines/catboost_dummy.ipynb) |
| Model selection | [catboost_weighted](05_machine_learning/model_selection/catboost_weighted.ipynb), [freeze_selected_model](05_machine_learning/model_selection/freeze_selected_model.ipynb) |
| Calibration | [calibration_threshold](05_machine_learning/calibration/calibration_threshold.ipynb) |
| Final Test | [final_test_evaluation](05_machine_learning/test_evaluation/final_test_evaluation.ipynb) |
| Post-Test exploratory sampling | [random_oversampling](05_machine_learning/sampling_experiments/random_oversampling.ipynb), [random_undersampling](05_machine_learning/sampling_experiments/random_undersampling.ipynb) |

Final Test evaluation is already complete. Inspect its saved outputs; do not rerun it to tune choices. Sampling experiments were conducted after Test exposure and did not change the frozen decision.
