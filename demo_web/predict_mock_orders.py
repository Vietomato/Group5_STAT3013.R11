"""Score the fixed synthetic fixture and export results without training."""
from pathlib import Path

import pandas as pd

from server import DemoData


def main():
    data = DemoData()
    batch = data.predict_mock_orders()
    rows = []
    for row in batch["orders"]:
        rows.append({"order_id": row["id"], "purchase_timestamp": row["purchase_timestamp"],
                     "estimated_date": row["estimated_date"], "set": row["set"],
                     "data_source": "synthetic_try_2026" if row["id"].startswith("TRY-") else "synthetic_demo_2026",
                     **row["features"], "raw_probability": row["raw_probability"],
                     "calibrated_probability": row["probability"], "prediction": row["prediction"],
                     "threshold": row["threshold"],
                     "delay_days_if_late": row["delay"]["days"] if row["delay"] else None,
                     "delay_baseline_days": row["delay"]["baseline_days"] if row["delay"] else None})
    path = Path(__file__).resolve().parent / "data/mock_orders_2026_predictions.csv"
    pd.DataFrame(rows).to_csv(path, index=False)
    print(batch["notice"])
    print(f"Scored {batch['count']} synthetic orders; {batch['alerts']} alerts. Actual outcomes unavailable.")
    for row in rows:
        print(f"{row['order_id']}: {row['calibrated_probability']:.2%} | {'ALERT' if row['prediction'] else 'NO ALERT'} | if late {row['delay_days_if_late']:.1f} days")
    print(f"Saved {path}")


if __name__ == "__main__":
    main()
