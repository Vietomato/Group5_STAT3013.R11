"""Verify real inference parity, filtering, validation, and HTTP behavior."""
import json
import threading
import unittest
from datetime import datetime, date
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import numpy as np

from server import DemoData, ROOT, make_handler
from generate_mock_orders import build_orders, build_try_orders


class DemoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = DemoData()
        if cls.data.model_error:
            raise RuntimeError(cls.data.model_error)
        cls.http = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(cls.data))
        cls.thread = threading.Thread(target=cls.http.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.http.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown()
        cls.http.server_close()
        cls.thread.join()

    def test_predictions_match_saved_test_run(self):
        outcomes = set()
        for sample_id in self.data.samples.order_id:
            sample = self.data.sample(sample_id)
            result = self.data.predict(sample["features"])
            ref = self.data.reference.set_index("order_id").loc[sample_id]
            self.assertAlmostEqual(result["raw_probability"], ref.raw_probability, places=9)
            self.assertAlmostEqual(result["probability"], ref.calibrated_probability, places=9)
            self.assertEqual(result["prediction"], int(ref.prediction))
            outcomes.add((int(ref.y_true), result["prediction"]))
        self.assertEqual(outcomes, {(1, 1), (0, 1), (1, 0), (0, 0)})

    def test_dashboard_filters_reconcile_to_source(self):
        full = self.data.dashboard()
        self.assertEqual((full["total"], full["valid"], full["late"], full["unlabeled"]),
                         (99441, 96470, 6534, 2971))
        cohort = self.data.frame
        cohort = cohort.loc[(cohort.customer_state == "SP") & (cohort.purchase_month == "2018-07")]
        filtered = self.data.dashboard("SP", "2018-07")
        self.assertEqual(filtered["total"], len(cohort))
        self.assertEqual(filtered["late"], int(cohort.is_late.sum()))
        self.assertEqual(sum(row["orders"] for row in filtered["distance"]), filtered["valid"])
        self.assertEqual(sum(row["orders"] for row in filtered["monthly"]), filtered["valid"])

    def test_missing_values_use_frozen_imputation(self):
        values = self.data.sample(self.data.samples.order_id.iloc[0])["features"]
        values["distance_km_mean"] = None
        values["customer_state"] = None
        result = self.data.predict(values)
        self.assertTrue(np.isfinite(result["probability"]))
        self.assertTrue(result["warnings"])

    def test_invalid_inputs_are_rejected(self):
        baseline = self.data.sample(self.data.samples.order_id.iloc[0])["features"]
        for feature, bad in [("freight_value", -1), ("purchase_hour", 24),
                             ("destination_humidity_state_mean_pct", 101),
                             ("item_count", 1.5), ("customer_state", "XX"),
                             ("distance_km_mean", float("nan"))]:
            with self.subTest(feature=feature), self.assertRaises(ValueError):
                self.data.predict({**baseline, feature: bad})
        with self.assertRaises(ValueError):
            self.data.predict({"item_count": 1})

    def test_mock_calendar_and_feature_schema(self):
        orders = self.data.mock_orders()["orders"]
        self.assertEqual(len(orders), 22)
        self.assertEqual(len({row["id"] for row in orders}), 22)
        generated = {row["order_id"]: row for row in build_orders() + build_try_orders()}
        for order in orders:
            values = order["features"]
            purchase = datetime.fromisoformat(order["purchase_timestamp"])
            self.assertEqual(purchase.year, 2026)
            self.assertEqual(purchase.hour, values["purchase_hour"])
            self.assertEqual(purchase.strftime("%A"), values["purchase_weekday"])
            self.assertEqual((date.fromisoformat(order["estimated_date"])-purchase.date()).days,
                             values["estimated_window_days"])
            self.assertEqual(set(values), set(self.data.features))
            for feature in self.data.features:
                self.assertEqual(values[feature], generated[order["id"]][feature])
            with self.assertRaises(ValueError):
                self.data.reveal(order["id"])
        christmas = next(o for o in orders if o["id"] == "MOCK-2026-012")["features"]
        self.assertEqual(christmas["purchase_is_national_holiday"], 1)
        self.assertEqual(christmas["days_to_next_national_holiday"], 0)
        self.assertEqual(christmas["national_holiday_count_in_estimated_window"], 1)

    def test_mock_batch_uses_real_model_without_outcomes(self):
        result = self.data.predict_mock_orders()
        self.assertFalse(result["actual_outcomes_available"])
        self.assertEqual(result["count"], 22)
        self.assertEqual(result["alerts"], sum(row["prediction"] for row in result["orders"]))
        for row in result["orders"]:
            single = self.data.predict(row["features"])
            self.assertAlmostEqual(row["probability"], single["probability"], places=12)
            self.assertEqual(row["prediction"], int(row["probability"] >= result["threshold"]))
            self.assertNotIn("actual", row)
            self.assertNotIn("y_true", row)
        request = Request(self.base + "/api/predict-mock", data=b"{}",
                          headers={"Content-Type": "application/json"})
        with urlopen(request) as response:
            self.assertEqual(json.load(response)["count"], 22)
        with urlopen(self.base + "/mock_orders_2026.csv") as response:
            self.assertIn(b"MOCK-2026-001", response.read())

    def test_http_serves_app_and_live_prediction(self):
        with urlopen(self.base + "/") as response:
            self.assertIn(b"Olist Observatory", response.read())
        sample = self.data.sample(self.data.samples.order_id.iloc[0])
        request = Request(self.base + "/api/predict", data=json.dumps({"features": sample["features"]}).encode(),
                          headers={"Content-Type": "application/json"})
        with urlopen(request) as response:
            result = json.load(response)
        self.assertIn("probability", result)
        self.assertEqual(len(result["features"]), 21)
        with self.assertRaises(HTTPError) as caught:
            urlopen(self.base + "/../requirements.txt")
        self.assertEqual(caught.exception.code, 404)
        caught.exception.close()
        bad = Request(self.base + "/api/predict", data=b'{"features": {}}',
                      headers={"Content-Type": "application/json"})
        with self.assertRaises(HTTPError) as caught:
            urlopen(bad)
        self.assertEqual(caught.exception.code, 400)
        caught.exception.close()

    def test_try_orders_2026_cover_28_nov_to_7_dec_and_run_both_models(self):
        orders = [o for o in self.data.mock_orders()["orders"] if o["id"].startswith("TRY-")]
        self.assertEqual([o["id"] for o in orders], [f"TRY-2026-{i:02d}" for i in range(1, 11)])
        dates = [datetime.fromisoformat(o["purchase_timestamp"]).date() for o in orders]
        self.assertEqual(dates, [date(2026, 11, 28) + __import__("datetime").timedelta(days=i) for i in range(10)])
        for order in orders:
            self.assertEqual(order["set"], "Try-out 28 Nov–7 Dec")
            values = order["features"]
            self.assertLessEqual(values["seller_count"], values["item_count"])
            self.assertLessEqual(values["product_category_count"], values["item_count"])
            self.assertEqual(values["purchase_is_national_holiday"], 0)
            classification = self.data.predict(values)
            delay = self.data.predict_delay(values)
            self.assertTrue(0 <= classification["probability"] <= 1)
            self.assertGreaterEqual(delay["days"], 1.0)
            self.assertAlmostEqual(classification["delay"]["days"], delay["days"], places=12)
            with self.assertRaises(ValueError):
                self.data.reveal(order["id"])
            with self.assertRaises(ValueError):
                self.data.delay_reveal(order["id"])
        with urlopen(self.base + "/try_orders_2026.csv") as response:
            self.assertIn(b"TRY-2026-10", response.read())

    # ---------- Problem 2: delay-duration regression ----------
    def test_delay_predictions_match_saved_validation_run(self):
        self.assertTrue(self.data.delay_ready, self.data.delay_error)
        self.assertEqual(self.data.delay_baseline, 7.0)
        groups = set()
        for sample_id in self.data.delay_samples.order_id:
            sample = self.data.delay_sample(sample_id)
            self.assertNotIn("actual_delay_days", sample)
            result = self.data.predict_delay(sample["features"])
            revealed = self.data.delay_reveal(sample_id)
            self.assertAlmostEqual(result["days"], revealed["saved_catboost_prediction"], places=9)
            self.assertEqual(result["baseline_days"], revealed["saved_baseline_prediction"])
            self.assertIn(revealed["split"], {"validation_a", "validation_b"})
            self.assertGreaterEqual(revealed["actual_delay_days"], 1)
            ref = self.data.delay_reference.set_index("order_id").loc[sample_id]
            groups.add(ref.delay_group)
        self.assertEqual(groups, {"1–3", "4–7", "8–14", ">14"})

    def test_delay_samples_never_come_from_test(self):
        manifest = __import__("pandas").read_csv(ROOT / "data/ml_preparation/split_manifest.csv").set_index("order_id")
        splits = set(manifest.loc[self.data.delay_samples.order_id, "split"])
        self.assertTrue(splits <= {"validation_a", "validation_b"}, splits)

    def test_delay_estimate_floor_and_validation(self):
        values = self.data.delay_sample(self.data.delay_samples.order_id.iloc[0])["features"]
        result = self.data.predict_delay(values)
        self.assertGreaterEqual(result["days"], 1.0)
        self.assertEqual(result["days"], max(result["raw_days"], 1.0))
        with self.assertRaises(ValueError):
            self.data.predict_delay({**values, "purchase_hour": 24})
        classification = self.data.predict(values)
        self.assertAlmostEqual(classification["delay"]["days"], result["days"], places=12)

    def test_delay_evidence_matches_saved_tables(self):
        delay = self.data.analysis["delay"]
        self.assertFalse(delay["difference"]["catboost_better"])
        self.assertLess(delay["difference"]["ci95_low"], 0)
        self.assertGreater(delay["difference"]["ci95_high"], 0)
        pooled = {r["model"]: r["MAE"] for r in delay["metrics"] if r["scope"] == "validation_pooled"}
        self.assertAlmostEqual(pooled["MedianBaseline"], delay["difference"]["baseline_mae"], places=12)
        self.assertEqual(len(delay["folds"]), 9)

    def test_dashboard_delay_distribution_reconciles(self):
        full = self.data.dashboard()["delay"]
        self.assertEqual(full["late_orders"], 6534)
        self.assertEqual(sum(row["orders"] for row in full["groups"]), 6534)
        self.assertEqual(full["median"], 7.0)

    def test_delay_http_endpoints(self):
        sample_id = self.data.delay_samples.order_id.iloc[0]
        with urlopen(self.base + "/api/delay/sample?id=" + sample_id) as response:
            sample = json.load(response)
        request = Request(self.base + "/api/delay/predict", data=json.dumps({"features": sample["features"]}).encode(),
                          headers={"Content-Type": "application/json"})
        with urlopen(request) as response:
            self.assertIn("days", json.load(response))
        with self.assertRaises(HTTPError) as caught:
            urlopen(self.base + "/api/delay/sample?id=" + self.data.samples.order_id.iloc[0])
        self.assertEqual(caught.exception.code, 400)
        caught.exception.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
