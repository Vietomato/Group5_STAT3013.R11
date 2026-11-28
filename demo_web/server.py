"""Local Olist demonstration. Run with the project's model environment."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
STATIC = Path(__file__).resolve().parent / "static"
DATA = ROOT / "data/processed/research_data_weather_price_holiday_assume_utc.csv"
CONFIG = ROOT / "outputs/tables/machine_learning/ml_calibration/final_config.json"
MOCK_DATA = Path(__file__).resolve().parent / "data/mock_orders_2026.csv"
TRY_DATA = Path(__file__).resolve().parent / "data/try_orders_2026.csv"
# Problem 2 (delay-duration regression): frozen outputs of notebooks/06_delay_prediction/02 and 02b.
DELAY_TABLES = ROOT / "outputs/tables/delay_prediction/regression_catboost"
DELAY_DIAGNOSTICS = ROOT / "outputs/tables/delay_prediction/regression_train_diagnostics"
DELAY_MODEL = ROOT / "outputs/models/delay_regression/CatBoostDelayRegressor.joblib"
DELAY_GROUPS = [(1, 3, "1–3"), (4, 7, "4–7"), (8, 14, "8–14"), (15, 30, "15–30"), (31, None, "31+")]
STATES = "AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO".split()
DAYS = "Monday Tuesday Wednesday Thursday Friday Saturday Sunday".split()
INTEGER_FIELDS = {"item_count", "seller_count", "purchase_hour", "estimated_window_days",
                  "product_category_count", "purchase_is_national_holiday",
                  "days_to_next_national_holiday", "national_holiday_count_in_estimated_window"}


def records(frame):
    """JSON-safe native values, including explicit nulls for missing observations."""
    return json.loads(frame.to_json(orient="records", double_precision=15))


def table(relative):
    return records(pd.read_csv(ROOT / relative))


class DemoData:
    def __init__(self):
        self.config = json.loads(CONFIG.read_text(encoding="utf-8"))
        self.features = self.config["features"]
        columns = list(dict.fromkeys(self.features + ["order_id", "is_late", "purchase_month", "delivery_delay_days"]))
        self.frame = pd.read_csv(DATA, usecols=columns, dtype={"order_id": str})
        self.labeled = self.frame.loc[self.frame.is_late.notna()].copy()
        self.reference = pd.read_csv(ROOT / "outputs/tables/machine_learning/ml_test/selected_test_predictions.csv")
        # Include successes and failures without disclosing the outcome in the sample menu.
        selected = []
        for actual, prediction in [(1, 1), (0, 1), (1, 0), (0, 0)]:
            rows = self.reference.loc[(self.reference.y_true == actual) & (self.reference.prediction == prediction)]
            selected.extend(rows.head(3).order_id.tolist())
        self.samples = self.frame.set_index("order_id").loc[selected].reset_index()
        self.pipeline = self.calibrator = None
        self.model_error = None
        self.lock = threading.Lock()
        try:
            for key, digest in [("frozen_pipeline", "pipeline_sha256"), ("calibrator", "calibrator_sha256")]:
                path = ROOT / self.config[key]
                if hashlib.sha256(path.read_bytes()).hexdigest() != self.config[digest]:
                    raise ValueError(f"Artifact hash mismatch: {self.config[key]}")
            self.pipeline = joblib.load(ROOT / self.config["frozen_pipeline"])
            self.calibrator = joblib.load(ROOT / self.config["calibrator"])
        except Exception as exc:
            self.model_error = f"{type(exc).__name__}: {exc}"
        self.analysis = {
            "tests": table("outputs/tables/inferential_statistics/statistical_test_results.csv"),
            "regression": table("outputs/tables/explanatory_regression/four_rq_adjusted_results.csv"),
            "sensitivity": table("outputs/tables/explanatory_regression/four_rq_sensitivity_results.csv"),
            "validation": table("outputs/tables/machine_learning/ml_selection/selection_comparison.csv"),
            "test_models": table("outputs/tables/machine_learning/ml_test/test_model_comparison.csv"),
            "threshold_metrics": table("outputs/tables/machine_learning/ml_test/selected_threshold_metrics.csv")[0],
            "calibration": table("outputs/tables/machine_learning/ml_test/selected_calibration_comparison.csv"),
            "splits": table("data/ml_preparation/split_summary.csv"),
        }
        self.load_delay_problem()

    def load_delay_problem(self):
        """Problem 2: frozen delay regressor, its declared baseline, validation samples and saved evidence."""
        self.delay_pipeline = None
        self.delay_error = None
        self.delay_plan = json.loads((DELAY_TABLES / "experiment_plan.json").read_text(encoding="utf-8"))
        self.delay_log = json.loads((DELAY_TABLES / "experiment_log.json").read_text(encoding="utf-8"))
        self.delay_baseline = float(self.delay_plan["baseline"]["value_days"])
        if self.delay_plan["features"] != self.features:
            raise ValueError("Delay regressor and classifier must use the same 21 predictors in the same order.")
        try:
            if hashlib.sha256(DELAY_MODEL.read_bytes()).hexdigest() != self.delay_log["model_sha256"]:
                raise ValueError("Artifact hash mismatch: " + self.delay_log["model_path"])
            self.delay_pipeline = joblib.load(DELAY_MODEL)
        except Exception as exc:
            self.delay_error = f"{type(exc).__name__}: {exc}"
        # Late validation orders (A+B) with saved predictions; Test is never used for Problem 2.
        self.delay_reference = pd.read_csv(DELAY_TABLES / "validation_predictions.csv", dtype={"order_id": str})
        ref = self.delay_reference.assign(
            catboost_error=(self.delay_reference.catboost_prediction - self.delay_reference.actual_delay_days).abs(),
            baseline_error=(self.delay_reference.baseline_prediction - self.delay_reference.actual_delay_days).abs())
        chosen = []
        # Two orders per actual-delay group: one where CatBoost is closer, one where the baseline is closer.
        for group in ["1–3", "4–7", "8–14", ">14"]:
            rows = ref.loc[ref.delay_group.eq(group)].sort_values("order_id")
            for closer in (rows.catboost_error < rows.baseline_error, rows.catboost_error > rows.baseline_error):
                if closer.any():
                    chosen.append(rows.loc[closer].order_id.iloc[0])
        self.delay_samples = self.frame.set_index("order_id").loc[chosen].reset_index()
        delay = lambda name: table(f"outputs/tables/delay_prediction/regression_catboost/{name}.csv")
        diagnostics = lambda name: table(f"outputs/tables/delay_prediction/regression_train_diagnostics/{name}.csv")
        self.analysis["delay"] = {
            "metrics": delay("validation_metrics"), "difference": delay("mae_difference_ci")[0],
            "groups": delay("delay_group_metrics"), "audit": delay("data_audit"),
            "importance": delay("feature_importance")[:8],
            "folds": diagnostics("fold_metrics"), "fold_differences": diagnostics("pooled_differences_ci"),
            "pooled_folds": diagnostics("pooled_metrics"), "fingerprint": diagnostics("weather_fingerprint"),
            "baseline": self.delay_baseline, "parameters": self.delay_plan["CatBoostDelayRegressor"],
        }

    @property
    def delay_ready(self):
        return self.delay_pipeline is not None

    def delay_sample(self, sample_id):
        match = self.delay_samples.loc[self.delay_samples.order_id == sample_id]
        if match.empty:
            raise ValueError("Unknown delay sample.")
        return {"id": sample_id, "kind": "delay_validation", "features": records(match[self.features])[0]}

    def delay_reveal(self, sample_id):
        self.delay_sample(sample_id)
        ref = self.delay_reference.loc[self.delay_reference.order_id == sample_id].iloc[0]
        return {"actual_delay_days": int(ref.actual_delay_days), "split": ref.split,
                "saved_catboost_prediction": float(ref.catboost_prediction),
                "saved_baseline_prediction": float(ref.baseline_prediction)}

    def delay_estimate(self, clean):
        """Days late if the order is late; floor of one day as declared in the protocol."""
        if not self.delay_ready:
            return None
        frame = pd.DataFrame([clean], columns=self.features)
        with self.lock:
            raw = float(self.delay_pipeline.predict(frame)[0])
        return {"days": max(raw, 1.0), "raw_days": raw, "baseline_days": self.delay_baseline}

    def predict_delay(self, values):
        if not self.delay_ready:
            raise RuntimeError("Delay model unavailable. Run notebooks/06_delay_prediction/02_delay_regression_catboost.ipynb.")
        clean = self.validate(values)
        estimate = self.delay_estimate(clean)
        return {**estimate, "warnings": self.input_warnings(clean),
                "model": "CatBoostDelayRegressor · MAE loss · late orders only",
                "features": {k: None if pd.isna(v) else v for k, v in clean.items()}}

    def input_warnings(self, clean):
        warnings = []
        missing = [feature for feature, value in clean.items() if pd.isna(value)]
        if missing:
            warnings.append(f"{len(missing)} missing input(s) use the frozen training-time imputation.")
        for feature, value in clean.items():
            if feature in self.config["categorical_features"] or pd.isna(value):
                continue
            series = self.labeled[feature]
            if value < series.min() or value > series.max():
                warnings.append(f"{feature} is outside the observed historical range.")
        return warnings

    def metadata(self):
        predictor_info = table("docs/predictor_list.csv")
        ranges = {}
        for feature in self.features:
            if feature not in self.config["categorical_features"]:
                series = self.labeled[feature].dropna()
                ranges[feature] = {"min": float(series.min()), "max": float(series.max())}
        return {
            "features": predictor_info, "states": STATES, "weekdays": DAYS,
            "months": sorted(self.labeled.purchase_month.dropna().unique().tolist()),
            "threshold": self.config["threshold"], "model_ready": self.pipeline is not None and self.calibrator is not None,
            "model_error": self.model_error, "ranges": ranges,
            "samples": [{"id": row.order_id, "label": f"Sample {i + 1:02d} · {row.customer_state} · {row.purchase_month}"}
                        for i, row in enumerate(self.samples.itertuples())],
            "delay_ready": self.delay_ready, "delay_error": self.delay_error, "delay_baseline": self.delay_baseline,
            "delay_samples": [{"id": row.order_id, "label": f"Late order D{i + 1:02d} · {row.customer_state} · {row.purchase_month}"}
                              for i, row in enumerate(self.delay_samples.itertuples())],
        }

    def sample(self, sample_id):
        match = self.samples.loc[self.samples.order_id == sample_id]
        if match.empty:
            raise ValueError("Unknown demo sample.")
        return {"id": sample_id, "features": records(match[self.features])[0]}

    def reveal(self, sample_id):
        self.sample(sample_id)
        ref = self.reference.loc[self.reference.order_id == sample_id].iloc[0]
        return {"actual": int(ref.y_true), "saved_prediction": int(ref.prediction),
                "saved_probability": float(ref.calibrated_probability)}

    def mock_orders(self):
        """Both synthetic 2026 sets: the original 12-order book and the 10 try-out orders."""
        rows = []
        for path, label in [(MOCK_DATA, "Order book"), (TRY_DATA, "Try-out 28 Nov–7 Dec")]:
            for row in records(pd.read_csv(path, dtype={"order_id": str})):
                values = {feature: row[feature] for feature in self.features}
                self.validate(values)
                rows.append({"id": row["order_id"], "kind": "mock2026", "set": label,
                             "purchase_timestamp": row["order_purchase_timestamp"],
                             "estimated_date": row["order_estimated_delivery_date"],
                             "description": row["scenario_description"], "features": values})
        return {"orders": rows, "synthetic": True, "year": 2026,
                "notice": "Synthetic inputs, including weather and an assumed holiday calendar. No actual outcomes. The historical model has not been validated for 2026; these scores illustrate inference, not measured future performance."}

    def predict_mock_orders(self):
        fixture = self.mock_orders()
        orders = [{**order, **self.predict(order["features"])} for order in fixture["orders"]]
        alerts = sum(order["prediction"] for order in orders)
        return {**fixture, "orders": orders, "count": len(orders), "alerts": alerts,
                "threshold": self.config["threshold"], "actual_outcomes_available": False}

    def dashboard(self, state="", month=""):
        if state and state not in STATES:
            raise ValueError("Unknown state filter.")
        if month and month not in self.metadata_months:
            raise ValueError("Unknown month filter.")
        frame = self.frame
        if state:
            frame = frame.loc[frame.customer_state == state]
        if month:
            frame = frame.loc[frame.purchase_month == month]
        valid = frame.loc[frame.is_late.notna()].copy()

        def grouped(column):
            if valid.empty:
                return []
            result = valid.groupby(column, observed=True).is_late.agg(orders="size", late="sum").reset_index()
            result["rate"] = result.late / result.orders
            return records(result)

        valid["distance_group"] = pd.cut(valid.distance_km_mean,
            bins=[0, 100, 300, 600, 1000, 2000, float("inf")],
            labels=["0–100", "100–300", "300–600", "600–1,000", "1,000–2,000", "2,000+"],
            include_lowest=True, right=False)
        distance = grouped("distance_group")
        late_delays = valid.loc[valid.is_late.eq(1), "delivery_delay_days"].dropna()
        delay_rows = [{"delay_group": label,
                       "orders": int(late_delays.between(low, high if high is not None else np.inf).sum())}
                      for low, high, label in DELAY_GROUPS]
        delay_summary = {"late_orders": int(len(late_delays)), "groups": delay_rows,
                         "median": float(late_delays.median()) if len(late_delays) else None,
                         "mean": float(late_delays.mean()) if len(late_delays) else None,
                         "p90": float(late_delays.quantile(.9)) if len(late_delays) else None}
        missing = valid.loc[valid.distance_km_mean.isna()]
        if not missing.empty:
            distance.append({"distance_group": "Missing", "orders": len(missing),
                             "late": int(missing.is_late.sum()), "rate": float(missing.is_late.mean())})
        return {"total": len(frame), "valid": len(valid), "late": int(valid.is_late.sum()),
                "unlabeled": int(frame.is_late.isna().sum()),
                "rate": float(valid.is_late.mean()) if len(valid) else None,
                "monthly": grouped("purchase_month"), "distance": distance, "delay": delay_summary,
                "states": sorted(grouped("customer_state"), key=lambda row: row["orders"], reverse=True),
                "source": "UTC order-level dataset · calendar-date delivery labels",
                "state": state, "month": month}

    @property
    def metadata_months(self):
        return set(self.labeled.purchase_month.dropna().unique())

    def validate(self, values):
        if not isinstance(values, dict) or set(values) != set(self.features):
            raise ValueError("Provide exactly the 21 configured predictors.")
        result = {}
        for feature in self.features:
            value = values[feature]
            if value is None or value == "":
                result[feature] = np.nan
                continue
            if feature in self.config["categorical_features"]:
                allowed = STATES if feature == "customer_state" else DAYS
                if value not in allowed:
                    raise ValueError(f"Invalid {feature}.")
                result[feature] = value
                continue
            if isinstance(value, bool):
                raise ValueError(f"{feature} must be a number.")
            try:
                number = float(value)
            except (TypeError, ValueError):
                raise ValueError(f"{feature} must be a number.") from None
            if not math.isfinite(number):
                raise ValueError(f"{feature} must be finite.")
            if "temp" not in feature and number < 0:
                raise ValueError(f"{feature} cannot be negative.")
            if feature in INTEGER_FIELDS and not number.is_integer():
                raise ValueError(f"{feature} must be an integer.")
            if feature in {"item_count", "seller_count", "product_category_count"} and number < 1:
                raise ValueError(f"{feature} must be at least one.")
            if feature == "purchase_hour" and number > 23:
                raise ValueError("Purchase hour must be between 0 and 23.")
            if feature == "purchase_is_national_holiday" and number not in (0, 1):
                raise ValueError("Holiday indicator must be zero or one.")
            if "humidity" in feature and number > 100:
                raise ValueError("Humidity must be between 0 and 100 percent.")
            result[feature] = number
        for feature in ("seller_count", "product_category_count"):
            if result[feature] > result["item_count"]:
                raise ValueError("Seller and category counts cannot exceed item count.")
        return result

    def predict(self, values):
        if self.pipeline is None or self.calibrator is None:
            raise RuntimeError("Frozen model unavailable. Use the project environment and regenerate missing artifacts; see demo_web/README.md.")
        clean = self.validate(values)
        frame = pd.DataFrame([clean], columns=self.features)
        with self.lock:
            raw = self.pipeline.predict_proba(frame)[:, 1]
            clipped = np.clip(raw, self.config["clipping_epsilon"], 1 - self.config["clipping_epsilon"])
            logits = np.log(clipped / (1 - clipped)).reshape(-1, 1)
            probability = float(self.calibrator.predict_proba(logits)[0, 1])
        return {"raw_probability": float(raw[0]), "probability": probability,
                "threshold": self.config["threshold"], "prediction": int(probability >= self.config["threshold"]),
                "model": "CatBoost · frozen baseline + sigmoid calibration", "warnings": self.input_warnings(clean),
                "delay": self.delay_estimate(clean),
                "features": {k: None if pd.isna(v) else v for k, v in clean.items()}}


def make_handler(data):
    class Handler(BaseHTTPRequestHandler):
        def send_json(self, payload, status=200):
            body = json.dumps(payload, allow_nan=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            url = urlsplit(self.path)
            query = parse_qs(url.query)
            try:
                if url.path == "/api/health":
                    self.send_json({"ok": True, "model_ready": data.pipeline is not None and data.calibrator is not None,
                                    "delay_ready": data.delay_ready})
                elif url.path == "/api/meta":
                    self.send_json(data.metadata())
                elif url.path == "/api/dashboard":
                    self.send_json(data.dashboard(query.get("state", [""])[0], query.get("month", [""])[0]))
                elif url.path == "/api/analysis":
                    self.send_json(data.analysis)
                elif url.path == "/api/sample":
                    self.send_json(data.sample(query.get("id", [""])[0]))
                elif url.path == "/api/reveal":
                    self.send_json(data.reveal(query.get("id", [""])[0]))
                elif url.path == "/api/delay/sample":
                    self.send_json(data.delay_sample(query.get("id", [""])[0]))
                elif url.path == "/api/delay/reveal":
                    self.send_json(data.delay_reveal(query.get("id", [""])[0]))
                elif url.path == "/api/mock-orders":
                    self.send_json(data.mock_orders())
                else:
                    assets = {"/": ("index.html", "text/html"), "/app.js": ("app.js", "text/javascript"),
                              "/styles.css": ("styles.css", "text/css"),
                              "/mock_orders_2026.csv": ("../data/mock_orders_2026.csv", "text/csv"),
                              "/try_orders_2026.csv": ("../data/try_orders_2026.csv", "text/csv")}
                    if url.path not in assets:
                        self.send_json({"error": "Not found"}, 404)
                        return
                    name, mime = assets[url.path]
                    body = (STATIC / name).read_bytes()
                    self.send_response(200)
                    self.send_header("Content-Type", mime + "; charset=utf-8")
                    self.send_header("Content-Length", str(len(body)))
                    self.send_header("X-Content-Type-Options", "nosniff")
                    self.end_headers()
                    self.wfile.write(body)
            except ValueError as exc:
                self.send_json({"error": str(exc)}, 400)
            except Exception as exc:
                self.log_error("Request failed: %s", exc)
                self.send_json({"error": "Unable to read project results. Check the server console and input files."}, 500)

        def do_POST(self):
            path = urlsplit(self.path).path
            if path not in {"/api/predict", "/api/predict-mock", "/api/delay/predict"}:
                self.send_json({"error": "Not found"}, 404)
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0 or length > 32768:
                    raise ValueError("Invalid request size.")
                payload = json.loads(self.rfile.read(length))
                if not isinstance(payload, dict):
                    raise ValueError("Expected a JSON object.")
                if path == "/api/predict-mock":
                    self.send_json(data.predict_mock_orders())
                elif path == "/api/delay/predict":
                    self.send_json(data.predict_delay(payload.get("features")))
                else:
                    self.send_json(data.predict(payload.get("features")))
            except (ValueError, TypeError) as exc:
                self.send_json({"error": str(exc)}, 400)
            except RuntimeError as exc:
                self.send_json({"error": str(exc)}, 503)
            except Exception as exc:
                self.log_error("Prediction failed: %s", exc)
                self.send_json({"error": "Prediction failed. Check the model environment and server console."}, 500)

    return Handler


def main():
    parser = argparse.ArgumentParser(description="Local Olist live demo")
    parser.add_argument("--port", type=int, default=8501)
    args = parser.parse_args()
    print("Loading Olist data and frozen artifacts…", flush=True)
    data = DemoData()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(data))
    print(f"Olist demo: http://127.0.0.1:{args.port}", flush=True)
    print("Problem 1 model: " + (data.model_error or "ready; frozen hashes verified"), flush=True)
    print("Problem 2 model: " + (data.delay_error or "ready; frozen hash verified"), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
