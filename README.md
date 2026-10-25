# Early Prediction of Late Delivery Risk in Brazilian E-Commerce

## 1. Project overview

This project uses the Brazilian E-Commerce Public Dataset by Olist to study delivery delays and prepare data for early late-delivery risk prediction.

The current work covers data cleaning, order-level dataset construction, exploratory data analysis, and temporal feature engineering. Statistical inference and machine learning experiments will follow.

## 2. Repository structure

```text
data/
├── raw/         # Original Olist CSV files
└── processed/   # Cleaned tables and research_data.csv

docs/
├── data_dictionary.md
└── temporal_feature_dictionary.md

notebooks/
├── 01_data_preprocessing.ipynb
├── 02_research_data_eda.ipynb
└── 03_temporal_feature_engineering.ipynb
```

Raw and processed CSV files are tracked in this repository. Raw files must remain unchanged.

## 3. Environment setup

Use Python 3.10 or later.

From the repository root, create a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Open the repository in VS Code with the Python and Jupyter extensions installed. Select the `.venv` Python environment as the notebook kernel.

## 4. Notebook workflow

Run the notebooks in this order:

1. **01_data_preprocessing.ipynb**
   - Inspect the nine source tables.
   - Check missing values, duplicates, keys, numeric values, and timestamps.
   - Apply documented cleaning rules and export cleaned tables.

2. **02_research_data_eda.ipynb**
   - Join and aggregate cleaned tables.
   - Build research_data.csv with one row per order_id.
   - Construct the is_late label and describe sample completeness.

3. **03_temporal_feature_engineering.ipynb**
   - Create six additional temporal features.
   - Check missingness, duration plausibility, outliers, and label consistency.
   - Update research_data.csv only after reviewing validation results and enabling export.

## 5. Late-delivery label

For eligible delivered orders:

- is_late = 1: actual delivery calendar date is after the estimated delivery date.
- is_late = 0: actual delivery calendar date is on or before the estimated date.
- is_late is missing when the order does not meet the labeling requirements.

Missing labels must not be automatically treated as on-time deliveries.

## 6. Feature availability and data leakage

The research dataset contains both potential predictors and historical outcomes.

actual_delivery_days and delivery_delay_days are known only after delivery and must not be used as predictors for early late-delivery prediction.

Other features must be reviewed against the selected prediction time before modeling. Missing-value imputation, encoding, and other learned transformations must be fitted using training data only.

## 7. Data documentation

- docs/data_dictionary.md describes the original order-level research variables.
- docs/temporal_feature_dictionary.md describes the six additional temporal features, calculations, missingness, and prediction-time availability.