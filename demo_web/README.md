# Olist local web demo

The demo runs the project's real data and frozen models on your own machine. It was built for a 15-minute recorded walkthrough. It runs on localhost and needs no account, external service, or Internet connection during the demo.

## Start the demo

From the repository root, run:

```powershell
.\.venv\Scripts\python.exe demo_web/server.py
```

Wait for two lines: `Problem 1 model: ready; frozen hashes verified` and `Problem 2 model: ready; frozen hash verified`. Then open **http://127.0.0.1:8501** in Chrome or Edge. Keep the terminal open during the demo, and press `Ctrl+C` to stop the server.

You can also use the launcher if PowerShell allows scripts. It looks for `.venv-boosting` first, then `.venv`:

```powershell
.\demo_web\run_demo.ps1
```

If port 8501 is busy, choose another port and open that address:

```powershell
.\.venv\Scripts\python.exe demo_web/server.py --port 8502
```

`server.py` can be started from any folder, because data paths are resolved from the file's location. After you edit code, stop the server, start it again, and press `Ctrl+F5` in the browser.

## Two prediction problems

| Page | Question | Data | Model | Frozen result |
|---|---|---|---|---|
| **1 · Will it be late?** | Will this order be late? | All labeled orders; demo samples come from Test | CatBoost classifier, sigmoid calibration, and a 5.418% threshold | Test: recall 94.25%, precision 6.42% |
| **2 · How many days?** | If it is late, how many days late? | Late orders only; demo samples come from Validation A + B, never Test | `CatBoostDelayRegressor` (MAE loss), compared with a baseline that always predicts 7 days | MAE 4.53 vs 4.41 days; no improvement over the baseline |

Both models use the same 21 purchase-time inputs. A Problem 1 result also shows an "if late, about X days" line from Problem 2, noting that this estimate was not more accurate than the baseline. The Mock orders 2026 table has an `If late · days` column.

## How to present each page

### Dashboard

- Shows total orders, valid labels, late orders, and the late rate. The full cohort must show 99,441 orders, 96,470 valid labels, 6,534 late orders, and a 6.77% late rate.
- **Destination state** and **Purchase month** recompute the cards and charts for the filtered cohort. The source data are not changed.
- Hover a point or bar to see its rate and order count. Groups with fewer than 30 orders are gray; do not rank risk from very small groups.
- **When an order is late, how late?** shows the distribution of days late (the Problem 2 target). The full cohort has a median of 7 days, a mean of 10.6, and a 90th percentile of 22.
- **Reset filters** returns to the full cohort. Filters apply to the Dashboard only.

### Statistical insights

- Select **Distance / Freight / Holiday / Rainfall** to read the method, sample size, estimate, CI, and Holm-adjusted p-value, alongside the adjusted odds ratio.
- Point to the OR = 1 line when explaining an interval. For rainfall, say that the association weakens after controlling for purchase period.
- Switch **Validation A / Test**: CatBoost was selected on A, while Random Forest has the highest Test AP. The model is not changed based on Test rankings.
- Point to the 6,922 false alerts in the confusion matrix to explain why 94.25% recall comes with 6.42% precision and a 78.32% alert rate.
- These are saved research results; nothing is refitted when you click. The on-screen labels state this.

### Problem 1 · Will it be late?

1. Choose **Sample 01** and select **Load sample** if you changed the selection. The page loads all 21 inputs of a real Test order without showing its outcome.
2. Read the main fields, then open **Calendar, products & weather** to show the other 14 inputs. Unedited fields keep the loaded values; the model uses all 21 inputs, not only the seven main ones.
3. Select **Run prediction**. The server calls the CatBoost pipeline's `predict_proba`, then the saved sigmoid calibrator. It does not replay stored probabilities.
4. Read the calibrated probability, the threshold of about 5.418%, and the alert label. The raw probability is shown for comparison.
5. Select **Reveal actual outcome** to show whether the order was late. The 12 samples include true alerts, false alerts, and missed delays. They were chosen to illustrate, not to represent overall performance.
6. Change an input, for example distance. The old result is marked as outdated. Run the prediction again and compare it with the original order's probability from step 3; the change can go either way or be zero.
7. Explain that this shows how the model responds to inputs, not a causal effect of an intervention. An edited order may not be realistic.
8. The actual outcome does not validate an edited scenario. Select **Restore sample** and run again to return to the original order.
9. **Download result** saves a JSON file with the current inputs and prediction. The demo never overwrites data, models, or research tables.

To show the model's limits while recording: Sample 01 is a true alert, Sample 04 a false alert, Sample 07 a missed delay, and Sample 10 a correct non-alert. This order comes from the saved Test results, not random sampling. The menu does not reveal outcomes.

### Problem 2 · How many days?

1. Choose **Late order D01–D08** and select **Load sample**. These are eight real late orders from Validation A + B: two per delay group (1–3, 4–7, 8–14, and over 14 days). In each group, CatBoost is closer for one order and the baseline for the other. The menu does not reveal the delay.
2. Select **Estimate days late**. The server calls `CatBoostDelayRegressor.predict`, raises results below 1 day to 1, and shows the 7-day baseline beside it.
3. Select **Reveal actual delay** to show the true delay and how far each guess missed. A single order is only illustrative; the conclusion rests on MAE over 567 orders.
4. Edit an input (for example distance) and run again to show the model's sensitivity. This is not a causal effect.
5. The lower part of the page shows the saved evidence: the MAE table, the confidence interval, errors by delay group, the Train-only time-split diagnostics, weather acting as a "date fingerprint", and feature importance. Sources: `outputs/tables/delay_prediction/regression_catboost/` and `regression_train_diagnostics/`.

Problem 2 needs `outputs/models/delay_regression/CatBoostDelayRegressor.joblib`, created by `notebooks/06_delay_prediction/02_delay_regression_catboost.ipynb`. The server checks its SHA-256 against `experiment_log.json` before loading. If the file is missing, the page still shows saved results but disables live estimates.

## Synthetic 2026 orders

There are two synthetic sets, each order with all 21 inputs:

| Set | IDs | Purchase dates | Used for |
|---|---|---|---|
| Order book | `MOCK-2026-001` … `012` | 26 Nov – 25 Dec 2026 | Mock orders 2026 table, including Christmas and holiday scenarios |
| Try-out | `TRY-2026-01` … `10` | 28 Nov – 7 Dec 2026, one per day | Selectable in the sample menus of **both problems** for quick trials |

The ten try-out orders are designed to show predictions changing: a same-city order with a short promise, heavy rain at the destination, a very long route with a short promise, a 30-day promise, three sellers, a bulky high-value item, a remote northern destination with rain, an early-morning order, rain at the origin, and a large multi-item order to the northeast.

On the Problem 1 or Problem 2 page, open the sample menu, pick from the **2026 try-out** group, select **Load sample**, and run. The reveal button is disabled because synthetic orders have no outcome.

The **Mock orders 2026** page lists all 22 orders; the Set column separates the two sets. **Predict all orders** runs the real classifier, calibrator, and delay regressor on the whole batch and fills Probability, Alert, and If late · days. There are no actual outcomes, so no precision, recall, or accuracy is shown.

- **Order book CSV** and **Try-out CSV** download the inputs: `demo_web/data/mock_orders_2026.csv` and `demo_web/data/try_orders_2026.csv`.
- **Download predictions** saves inputs with raw and calibrated probabilities, alerts, the threshold, and the days-late estimate.
- **Inspect** opens an order on the Problem 1 page, where you can edit inputs and compare with the original prediction. Reveal actual outcome is disabled for every mock order.
- The Dashboard and statistical results use historical data only; mock orders are never merged into the research data.

Prices, distances, product details, and weather are synthetic, not real 2026 transactions or observations. Purchase hour, weekday, delivery window, and estimated date are computed from the timestamp. The holiday calendar is an assumption covering only 25 Dec 2026 and 1 Jan 2027, not a verified national calendar. Days to the next holiday include the purchase day, and holidays in the window use `(purchase date, estimated date]`, following the project convention.

The models were trained on 2016–2018 data and have not been evaluated on real 2026 data. The calendar year is not one of the 21 inputs, so a 2026 date does not adapt the models to 2026 conditions. The scores illustrate the inference flow; they are not evidence of 2026 accuracy.

To regenerate the fixtures and export predictions without a browser:

```powershell
.\.venv\Scripts\python.exe demo_web/generate_mock_orders.py
.\.venv\Scripts\python.exe demo_web/predict_mock_orders.py
```

The first command rewrites both fixed sets; the original 12-order file is unchanged. The second writes `demo_web/data/mock_orders_2026_predictions.csv` without retraining or modifying any model.

## 15-minute recording plan

| Time | Action |
|---|---|
| 00:00–02:00 | Introduce the problem, the label, and the full-cohort dashboard |
| 02:00–04:00 | Filter by state and month, read the charts, explain class imbalance |
| 04:00–07:00 | Statistical insights: tests and regression; association is not causation |
| 07:00–09:00 | Split timeline, Validation A vs Test, and the confusion matrix |
| 09:00–12:00 | Problem 1: load a sample, run it, reveal the outcome, edit an input, run again |
| 12:00–13:00 | Problem 2: run a late order, reveal the actual delay, read the "no improvement over baseline" result |
| 13:00–15:00 | Optionally show `predict` in `server.py` to prove the live flow; conclusions and limitations |

## Environment and models

No web libraries are added. The backend uses Python's standard HTTP server, and the frontend uses plain HTML, CSS, JavaScript, and SVG. Prediction uses packages already in the research environment: NumPy, pandas, joblib, scikit-learn, and CatBoost. Use an environment compatible with the saved models; the repository records Python 3.14.6 and the versions in `requirements.txt`.

Required inputs on disk:

- Dataset `data/processed/research_data_weather_price_holiday_assume_utc.csv`.
- Predictor list `docs/predictor_list.csv`.
- Result CSVs in `outputs/tables/` and `data/ml_preparation/split_summary.csv`.
- Configuration `outputs/tables/machine_learning/ml_calibration/final_config.json`.
- Problem 1 pipeline `outputs/models/ml_selection/CatBoostBaseline.joblib` and calibrator `outputs/models/ml_calibration/sigmoid_calibrator.joblib`.
- Problem 2 model `outputs/models/delay_regression/CatBoostDelayRegressor.joblib` and its records in `outputs/tables/delay_prediction/regression_catboost/`.

The server checks the SHA-256 of every model file against its configuration before loading. Inputs are ordered as the 21 predictors. Missing values pass through the preprocessing fitted on Train. For Problem 1, the raw probability is clipped by the configured epsilon, converted to log-odds, and passed to the calibrator; the threshold is read from the configuration and cannot be changed in the interface.

Model binaries are excluded from Git by design. On a new machine or clone, regenerate them by running the notebooks listed in the root [README](../README.md#local-web-demo). If a model is missing or its hash does not match, the dashboard and statistical results still load, but that problem's prediction button is disabled; no substitute predictions are produced.

The app binds only to `127.0.0.1` and is suitable for a local recording. It is not a public deployment configuration.

## Tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s demo_web -p "test_*.py" -v
```

The tests check prediction parity with the saved Test and validation outputs, dashboard filters, missing values, invalid inputs, synthetic calendars, and the HTTP API. Running them does not retrain models or overwrite research results.
