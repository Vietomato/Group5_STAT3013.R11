# Research Data Dictionary

## 1. Dataset Overview

**Project:** Early Prediction of Late Delivery Risk in Brazilian E-Commerce: A Statistical and Machine Learning Approach

**Dataset:** Brazilian E-Commerce Public Dataset by Olist (2016–2018)

**Total orders:** 99,441

**Current dataset columns:** 34 (28 base columns documented here and six temporal additions).

**Official file:** `data/processed/research_data.csv`

See `temporal_feature_dictionary.md` for the six additions and `data_leakage_review.md` for the purchase-time availability review. The latter is a separate TASK 04 deliverable and was not included in the archive reviewed for this handoff.

**Unit of analysis:** One row per unique `order_id`.

**Missing-value policy:** Missing information is retained as missing; unknown values are not automatically replaced with zero.

---

## 2. Data Completeness Summary

- Orders with valid delivery labels: 96,470
- Orders without valid delivery labels: 2,971
- Orders without item records: 775
- Orders missing a usable mean geographic distance: 1,269

---

## 3. Variable Definitions

### 3.1. `order_id`

- **Description:** Unique order identifier.
- **Unit / Type:** Identifier
- **Source:** orders_clean.csv
- **Calculation / Rule:** Preserved from the orders table; one unique value per order.
- **Missing values:** 0 (0.00%)

### 3.2. `customer_id`

- **Description:** Customer record identifier associated with the order.
- **Unit / Type:** Identifier
- **Source:** orders_clean.csv
- **Calculation / Rule:** Preserved from the orders table; links to customers.customer_id.
- **Missing values:** 0 (0.00%)

### 3.3. `order_status`

- **Description:** Recorded operational status of the order.
- **Unit / Type:** Category
- **Source:** orders_clean.csv
- **Calculation / Rule:** Preserved from the cleaned orders table.
- **Missing values:** 0 (0.00%)

### 3.4. `order_purchase_timestamp`

- **Description:** Date and time when the order was placed.
- **Unit / Type:** Datetime
- **Source:** orders_clean.csv
- **Calculation / Rule:** Parsed as a datetime; unchanged otherwise.
- **Missing values:** 0 (0.00%)

### 3.5. `order_approved_at`

- **Description:** Date and time when the order was approved.
- **Unit / Type:** Datetime
- **Source:** orders_clean.csv
- **Calculation / Rule:** Parsed as a datetime; missing values are retained.
- **Missing values:** 160 (0.16%)

### 3.6. `order_delivered_carrier_date`

- **Description:** Date and time when the order was handed to the carrier.
- **Unit / Type:** Datetime
- **Source:** orders_clean.csv
- **Calculation / Rule:** Parsed as a datetime; missing values are retained.
- **Missing values:** 1,783 (1.79%)

### 3.7. `order_delivered_customer_date`

- **Description:** Date and time when the order was delivered to the customer.
- **Unit / Type:** Datetime
- **Source:** orders_clean.csv
- **Calculation / Rule:** Parsed as a datetime; used to construct the delivery outcome label.
- **Missing values:** 2,965 (2.98%)

### 3.8. `order_estimated_delivery_date`

- **Description:** Estimated delivery date recorded for the order.
- **Unit / Type:** Date
- **Source:** orders_clean.csv
- **Calculation / Rule:** Parsed as a datetime; compared by calendar date for late-delivery labeling.
- **Missing values:** 0 (0.00%)

### 3.9. `flag_approval_before_purchase`

- **Description:** Quality-control flag indicating approval before purchase.
- **Unit / Type:** Boolean/NA
- **Source:** orders_clean.csv
- **Calculation / Rule:** Inherited from the upstream preprocessing pipeline; original flag logic is not recalculated here.
- **Missing values:** 160 (0.16%)

### 3.10. `flag_carrier_before_purchase`

- **Description:** Quality-control flag indicating carrier handoff before purchase.
- **Unit / Type:** Boolean/NA
- **Source:** orders_clean.csv
- **Calculation / Rule:** Inherited from the upstream preprocessing pipeline; original flag logic is not recalculated here.
- **Missing values:** 1,783 (1.79%)

### 3.11. `flag_delivery_before_carrier`

- **Description:** Quality-control flag indicating delivery before carrier handoff.
- **Unit / Type:** Boolean/NA
- **Source:** orders_clean.csv
- **Calculation / Rule:** Inherited from the upstream preprocessing pipeline; original flag logic is not recalculated here.
- **Missing values:** 2,966 (2.98%)

### 3.12. `flag_delivery_before_purchase`

- **Description:** Quality-control flag indicating delivery before purchase.
- **Unit / Type:** Boolean/NA
- **Source:** orders_clean.csv
- **Calculation / Rule:** Inherited from the upstream preprocessing pipeline; original flag logic is not recalculated here.
- **Missing values:** 2,965 (2.98%)

### 3.13. `flag_delivered_missing_date`

- **Description:** Quality-control flag for a delivered order with a missing delivery date.
- **Unit / Type:** Boolean/NA
- **Source:** orders_clean.csv
- **Calculation / Rule:** Inherited from the upstream preprocessing pipeline; original flag logic is not recalculated here.
- **Missing values:** 0 (0.00%)

### 3.14. `is_late`

- **Description:** Observed late-delivery outcome for an eligible delivered order.
- **Unit / Type:** 0 / 1 / NA
- **Source:** orders_clean.csv
- **Calculation / Rule:** 1 if actual delivery calendar date is after the estimated date; 0 if on or before it; NA unless status is delivered and required dates exist with delivery not preceding purchase.
- **Missing values:** 2,971 (2.99%)

### 3.15. `purchase_weekday`

- **Description:** Weekday on which the order was placed.
- **Unit / Type:** Weekday
- **Source:** orders_clean.csv
- **Calculation / Rule:** English weekday name extracted from order_purchase_timestamp.
- **Missing values:** 0 (0.00%)

### 3.16. `purchase_month`

- **Description:** Year and month in which the order was placed.
- **Unit / Type:** YYYY-MM
- **Source:** orders_clean.csv
- **Calculation / Rule:** Formatted from order_purchase_timestamp.
- **Missing values:** 0 (0.00%)

### 3.17. `promised_days`

- **Description:** Calendar days between approval and estimated delivery.
- **Unit / Type:** Days
- **Source:** orders_clean.csv
- **Calculation / Rule:** Estimated delivery date minus approval date after normalization to calendar dates; NA if either date is missing or the result is negative.
- **Missing values:** 170 (0.17%)

### 3.18. `customer_state`

- **Description:** Brazilian state code of the delivery destination.
- **Unit / Type:** State code
- **Source:** customers_clean.csv
- **Calculation / Rule:** Joined from customers using customer_id.
- **Missing values:** 0 (0.00%)

### 3.19. `items_value`

- **Description:** Total listed product price for the order, excluding freight.
- **Unit / Type:** BRL
- **Source:** items_clean.csv
- **Calculation / Rule:** Sum of price across order items, preserving NA when all prices are missing; NA for orders without items.
- **Missing values:** 775 (0.78%)

### 3.20. `freight_value`

- **Description:** Total freight charge associated with the order items.
- **Unit / Type:** BRL
- **Source:** items_clean.csv
- **Calculation / Rule:** Sum of item-level freight_value by order_id, preserving NA when all values are missing; NA for orders without items.
- **Missing values:** 775 (0.78%)

### 3.21. `item_count`

- **Description:** Number of item records associated with the order.
- **Unit / Type:** Count
- **Source:** items_clean.csv
- **Calculation / Rule:** Count of item rows grouped by order_id; NA for orders without item records.
- **Missing values:** 775 (0.78%)

### 3.22. `seller_count`

- **Description:** Number of distinct sellers associated with the order.
- **Unit / Type:** Count
- **Source:** items_clean.csv
- **Calculation / Rule:** Number of unique seller_id values by order_id; NA for orders without item records.
- **Missing values:** 775 (0.78%)

### 3.23. `has_interstate_seller`

- **Description:** Whether at least one seller is located in a different state from the customer.
- **Unit / Type:** 0 / 1 / NA
- **Source:** customers_clean.csv; sellers_clean.csv; items_clean.csv
- **Calculation / Rule:** 1 if any known seller state differs from the customer state; 0 if all seller states are known and match; NA if indeterminate.
- **Missing values:** 775 (0.78%)

### 3.24. `distance_km_mean`

- **Description:** Mean straight-line distance between the customer and distinct sellers with usable coordinates.
- **Unit / Type:** Kilometers
- **Source:** geolocation_lookup.csv; customers_clean.csv; sellers_clean.csv; items_clean.csv
- **Calculation / Rule:** Haversine distance (Earth radius 6,371 km) for each distinct order-seller pair, averaged over valid distances; NA if none is valid. Flagged geographic coordinates are excluded from the mean.
- **Missing values:** 1,269 (1.28%)

### 3.25. `seller_count_with_geo`

- **Description:** Number of distinct sellers with a usable customer-to-seller distance.
- **Unit / Type:** Count
- **Source:** geolocation_lookup.csv; items_clean.csv
- **Calculation / Rule:** Count of nonmissing screened Haversine distances per order; NA for orders without items.
- **Missing values:** 775 (0.78%)

### 3.26. `seller_count_total`

- **Description:** Total distinct sellers in the order-seller geographic aggregation.
- **Unit / Type:** Count
- **Source:** items_clean.csv
- **Calculation / Rule:** Distinct seller_id count per order before coordinate screening; NA for orders without items.
- **Missing values:** 775 (0.78%)

### 3.27. `has_partial_missing_geo`

- **Description:** Whether only some distinct sellers lack a usable distance.
- **Unit / Type:** Boolean/NA
- **Source:** Derived geographic features
- **Calculation / Rule:** True when 0 < seller_count_with_geo < seller_count_total; False otherwise for orders with items; NA for orders without items.
- **Missing values:** 775 (0.78%)

### 3.28. `has_all_missing_geo`

- **Description:** Whether no distinct seller has a usable distance.
- **Unit / Type:** Boolean/NA
- **Source:** Derived geographic features
- **Calculation / Rule:** True when seller_count_with_geo equals zero for orders with items; False otherwise; NA for orders without items.
- **Missing values:** 775 (0.78%)

---

## 4. Data Processing Rules

### 4.1. Order-Level Aggregation

- Each output record represents one unique order.
- Item-level and order-seller information are aggregated before joining to the orders table.
- Left joins preserve all original orders; orders without items retain missing item-derived features.

### 4.2. Late Delivery Labeling

- Labels are assigned only to delivered orders with valid purchase, actual delivery, and estimated delivery timestamps, and with actual delivery not preceding purchase.
- Actual and estimated delivery dates are compared by calendar date, not time of day.
- Canceled, undelivered, or otherwise ineligible orders are not coded as on-time deliveries.

### 4.3. Multiple Sellers and Missing Coordinates

- Each distinct seller is counted once per order when computing mean distance.
- The mean uses available valid distances; partially missing seller coordinates are flagged.
- A missing coordinate never implies zero distance.

### 4.4. Temporal Variables

- `purchase_weekday` and `purchase_month` are derived from the purchase timestamp.
- `promised_days` counts calendar days from approval to the estimated delivery date.
- Negative or unavailable promised durations remain missing.

---

## 5. Geolocation Quality Control

- Seller-to-customer distances use the Haversine formula with Earth radius 6,371 km.
- The resulting values are approximate straight-line geographic distances, not transport routes.
- A preliminary screening rule flags coordinates outside latitude [-35, 6] and longitude [-75, -30] degrees.
- Flagged ZIP prefixes: 8.
- Affected distinct order-seller pairs: 5.
- Affected distinct orders: 5.
- Orders with missing distance before coordinate screening: 1,264.
- Orders with missing distance after coordinate screening: 1,269.
- Additional orders with missing distance after screening: 5.
- Screened distances are set to missing; no orders or ZIP identifiers are deleted.
- This approximate geographic screen is an additional methodological quality-control decision, not an exact national-boundary test or proof of erroneous coordinates.
- Statistical IQR outliers are not automatically removed.

---

## 6. Limitations and Appropriate Use

- The dataset describes historical Olist transactions from 2016–2018 and is not a random sample of all Brazilian e-commerce orders.
- ZIP-level coordinates are approximations rather than precise delivery addresses.
- Descriptive statistics and observed associations do not establish causality or predictive performance.
- The complete research dataset contains outcomes and post-confirmation information for historical analysis.
- Before early prediction modeling, input features must be independently restricted to information available at the chosen prediction timestamp to prevent data leakage.

---

*Base definitions originate from `02_research_data_eda.ipynb`; this version includes manually maintained handoff notes. Regeneration may overwrite these notes.*


## 7. Loading and Sample Denominators

CSV does not preserve pandas dtypes. Preserve identifiers as strings and explicitly parse dates and numeric fields. Missing counts above refer to all 99,441 orders. The labeled EDA sample contains 96,470 orders; 480 of these lack distance. Do not confuse full-dataset and labeled-sample missing counts.
