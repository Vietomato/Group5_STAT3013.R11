"""Create an entirely synthetic 2026 fixture; never modify research datasets."""
import csv
import json
from datetime import datetime, timedelta, date
from pathlib import Path

HERE = Path(__file__).resolve().parent
FEATURES = json.loads((HERE.parent / "outputs/tables/machine_learning/ml_calibration/final_config.json").read_text())["features"]


def build_orders():
    scenarios = [
        ("2026-11-26 10:30:00", "SP", 40, 7, 89.90, 12.0, 1, 1, 650, 2100, 1, 0.0, 0.0, 62, 60, 24, 25, "Local single-item parcel"),
        ("2026-11-27 18:15:00", "RJ", 450, 12, 249.0, 28.0, 2, 1, 1800, 8500, 1, 8.0, 3.0, 80, 74, 27, 25, "Two-item parcel with simulated rain"),
        ("2026-11-28 09:00:00", "BA", 1800, 18, 420.0, 55.0, 3, 2, 5000, 25000, 2, 18.0, 4.0, 87, 72, 28, 24, "Long-distance multi-seller order"),
        ("2026-11-29 14:45:00", "MG", 900, 15, 129.90, 22.0, 1, 1, 800, 3500, 1, 1.0, 0.5, 65, 63, 23, 24, "Medium-distance light parcel"),
        ("2026-11-30 20:10:00", "PE", 2300, 25, 850.0, 95.0, 2, 2, 12000, 95000, 2, 22.0, 7.0, 90, 81, 29, 26, "Large parcel with a Christmas delivery estimate"),
        ("2026-12-01 08:20:00", "PR", 100, 10, 59.90, 9.5, 1, 1, 300, 1200, 1, 0.0, 0.0, 58, 61, 20, 22, "Small parcel on a short route"),
        ("2026-12-05 16:00:00", "RS", 700, 14, 310.0, 32.0, 4, 2, 3200, 18000, 3, 6.0, 2.0, 76, 70, 21, 24, "Multi-category weekend purchase"),
        ("2026-12-10 11:40:00", "CE", 1400, 20, 180.0, 42.0, 1, 1, 1500, 7000, 1, 12.0, 1.0, 84, 66, 30, 25, "Longer delivery window before Christmas"),
        ("2026-12-15 19:25:00", "SC", 250, 8, 199.0, 19.0, 2, 1, 1300, 6800, 1, 3.0, 1.0, 71, 65, 22, 24, "Two products from one seller"),
        ("2026-12-20 13:00:00", "AM", 3200, 30, 1200.0, 130.0, 3, 2, 18000, 140000, 2, 30.0, 5.0, 93, 78, 29, 25, "Distant destination across two assumed holidays"),
        ("2026-12-24 21:15:00", "GO", 1200, 16, 520.0, 48.0, 2, 1, 4500, 22000, 2, 9.0, 2.0, 79, 69, 26, 25, "Christmas Eve scenario"),
        ("2026-12-25 10:00:00", "SP", 60, 7, 75.0, 11.0, 1, 1, 500, 1800, 1, 2.0, 0.0, 68, 61, 25, 24, "Purchase on an assumed holiday"),
    ]
    return [make_row(f"MOCK-2026-{i:03d}", values, "synthetic_demo_2026") for i, values in enumerate(scenarios, 1)]


def build_try_orders():
    """Ten small synthetic orders from 28 Nov to 7 Dec 2026 for trying both problems live."""
    # Each scenario varies one or two inputs so differences in the two predictions are easy to discuss.
    scenarios = [
        ("2026-11-28 08:45:00", "SP", 25, 5, 49.90, 9.9, 1, 1, 400, 1500, 1, 0.5, 0.0, 60, 58, 24, 24, "Same-city small parcel, short promise"),
        ("2026-11-29 22:30:00", "RJ", 360, 9, 159.0, 21.5, 1, 1, 1200, 5000, 1, 25.0, 6.0, 88, 72, 28, 24, "Late-night order with heavy rain at destination"),
        ("2026-11-30 07:10:00", "MA", 2500, 13, 299.0, 68.0, 1, 1, 2500, 12000, 1, 14.0, 1.0, 82, 64, 30, 24, "Very long route with a short promise"),
        ("2026-12-01 12:00:00", "MG", 520, 30, 89.0, 15.0, 1, 1, 600, 2400, 1, 2.0, 0.0, 63, 60, 23, 24, "Generous 30-day delivery window"),
        ("2026-12-02 15:30:00", "BA", 1450, 21, 640.0, 74.0, 3, 3, 7000, 42000, 3, 11.0, 3.0, 85, 70, 29, 25, "Three sellers and three categories"),
        ("2026-12-03 10:15:00", "PR", 410, 11, 2100.0, 85.0, 1, 1, 25000, 160000, 1, 4.0, 1.0, 74, 66, 22, 24, "Bulky high-value item"),
        ("2026-12-04 19:45:00", "PA", 2900, 24, 210.0, 58.0, 2, 1, 1800, 9000, 1, 28.0, 2.0, 90, 68, 31, 25, "Remote northern destination with heavy rain"),
        ("2026-12-05 03:20:00", "SP", 15, 4, 35.0, 7.5, 1, 1, 200, 800, 1, 0.0, 0.0, 57, 57, 21, 21, "Early-morning local order, tight promise"),
        ("2026-12-06 17:05:00", "RS", 1100, 16, 360.0, 36.0, 2, 2, 3000, 15000, 2, 7.0, 18.0, 77, 86, 20, 27, "Two sellers with heavy rain at origin"),
        ("2026-12-07 13:40:00", "CE", 2300, 19, 1150.0, 102.0, 4, 2, 9000, 60000, 3, 16.0, 5.0, 86, 73, 30, 25, "Large multi-item order to the northeast"),
    ]
    return [make_row(f"TRY-2026-{i:02d}", values, "synthetic_try_2026") for i, values in enumerate(scenarios, 1)]


def make_row(order_id, values, source):
    # A deliberately limited scenario calendar, not a verified federal calendar.
    assumed_holidays = [date(2026, 12, 25), date(2027, 1, 1)]
    (timestamp, state, distance, window, price, freight, items, sellers, weight, volume,
     categories, rain_to, rain_from, humid_to, humid_from, temp_to, temp_from, description) = values
    purchase = datetime.fromisoformat(timestamp)
    estimated = purchase.date() + timedelta(days=window)
    # Match project conventions: next holiday includes today; window is (purchase, estimate].
    row = {
        "order_id": order_id, "order_purchase_timestamp": timestamp,
        "order_estimated_delivery_date": estimated.isoformat(), "scenario_description": description,
        "data_source": source, "weather_day_utc": (purchase.date() - timedelta(days=1)).isoformat(),
        "distance_km_mean": distance, "customer_state": state, "item_count": items, "seller_count": sellers,
        "purchase_hour": purchase.hour, "purchase_weekday": purchase.strftime("%A"),
        "estimated_window_days": window, "items_value": price, "freight_value": freight,
        "total_product_weight_g": weight, "total_product_volume_cm3": volume,
        "product_category_count": categories, "purchase_is_national_holiday": int(purchase.date() in assumed_holidays),
        "days_to_next_national_holiday": min((day-purchase.date()).days for day in assumed_holidays if day>=purchase.date()),
        "national_holiday_count_in_estimated_window": sum(purchase.date()<day<=estimated for day in assumed_holidays),
        "destination_rain_state_mean_mm": rain_to, "origin_rain_state_mean_mm": rain_from,
        "destination_humidity_state_mean_pct": humid_to, "origin_humidity_state_mean_pct": humid_from,
        "destination_air_temp_state_mean_c": temp_to, "origin_air_temp_state_mean_c": temp_from,
    }
    return row


def write(rows, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    metadata = [key for key in rows[0] if key not in FEATURES]
    with destination.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=metadata + FEATURES)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} synthetic orders to {destination}")


def main():
    write(build_orders(), HERE / "data/mock_orders_2026.csv")
    write(build_try_orders(), HERE / "data/try_orders_2026.csv")


if __name__ == "__main__":
    main()
