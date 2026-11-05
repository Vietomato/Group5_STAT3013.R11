# Price, Product, Holiday and Weather Feature Dictionary

## 1. Purpose

This document describes the additional features created for the
late-delivery study: price, product characteristics, holidays,
and pre-purchase weather.

These variables support descriptive analysis, hypothesis testing,
regression, and machine learning. Their presence in the dataset
does not automatically make them approved purchase-time predictors.

The prediction point is `order_purchase_timestamp`.
The target is `is_late`.

## 2. Datasets and Unit of Analysis

Each research table contains one row per `order_id`.

| Dataset | Rows | Columns | Description |
|---|---:|---:|---|
| `research_data.csv` | 99,441 | 34 | Original research table |
| `research_data_price_product.csv` | 99,441 | 44 | Original table plus price and product features |
| `research_data_weather_price_holiday_assume_utc.csv` | 99,441 | 74 | Combined table under the UTC assumption |
| `research_data_weather_price_holiday_assume_sao_paulo.csv` | 99,441 | 74 | Combined table under the São Paulo assumption |

All four tables preserve the original delivery labels:

- Not Late: 89,936 orders.
- Late: 6,534 orders.
- Missing label: 2,971 orders.

The two timezone scenarios represent the same orders.
They must be analyzed separately, not stacked as independent observations.

The 74 columns include predictors, identifiers, target information,
post-purchase variables, and quality metadata. They are not all model inputs.

## 3. Price Features

### Source

- `research_data.csv`
- `items_clean.csv`

The existing order-level totals are checked against the cleaned item table
before additional price features are created.

### Existing input variables

| Variable | Definition | Unit |
|---|---|---|
| `items_value` | Sum of item prices within an order | BRL |
| `freight_value` | Sum of item-level freight charges within an order | BRL |
| `item_count` | Number of item records within an order | Item records |

### Additional variables

| Variable | Definition and formula | Unit |
|---|---|---|
| `order_total_value` | `items_value + freight_value` | BRL |
| `freight_to_items_ratio` | `freight_value / items_value` | Ratio |
| `mean_item_value` | `items_value / item_count` | BRL per item |
| `freight_per_item` | `freight_value / item_count` | BRL per item |

### Interpretation

- `order_total_value` represents item value plus freight. It is not a verified measure of net revenue, profit, or the final amount collected.
- A `freight_to_items_ratio` of 0.25 means freight equals 25% of item value.
- `mean_item_value` describes average item price within an order.
- `freight_per_item` describes average freight charge per item record.

### Missing-value rules

- Missing inputs remain missing.
- Division is performed only when the denominator is positive.
- Zero freight is retained as a valid value.
- The 775 orders without item records have missing price features.
- Missing values are not replaced with zero during feature engineering.

### Modeling considerations

Price features are conditional purchase-time candidates.
The analysis assumes that recorded prices and freight charges
represent information available when the order was placed.

Do not include `items_value`, `freight_value`, and `order_total_value`
together in an ordinary regression model: the total is the exact
sum of the other two variables.

Other derived price variables may also be strongly related.
Their selection should be documented.

## 4. Product Features

### Source and aggregation

Cleaned item records are joined to `products_clean.csv` using `product_id`.

The join must preserve the number of item records.
Product measurements are then aggregated to one row per order.

Each item record contributes once. A product appearing in multiple
item records contributes its weight and volume for each record.

Item volume is calculated as:

`product_length_cm × product_height_cm × product_width_cm`

Missing, nonfinite, or nonpositive physical measurements are treated
as unavailable for these features.

### Variables

| Variable | Definition | Unit |
|---|---|---|
| `total_product_weight_g` | Sum of item weights, reported only when every item has valid weight | g |
| `total_product_volume_cm3` | Sum of item volumes, reported only when every item has valid dimensions | cm³ |
| `product_category_count` | Number of distinct known categories, reported only when all items have category information | Categories |
| `weight_coverage_ratio` | Items with valid weight divided by total item records | Ratio, 0–1 |
| `volume_coverage_ratio` | Items with valid volume divided by total item records | Ratio, 0–1 |
| `category_coverage_ratio` | Items with known categories divided by total item records | Ratio, 0–1 |

### Missing-value and coverage rules

- Totals are not presented as complete when some item measurements are missing.
- Coverage of 1 means all item records have the required information.
- Coverage between 0 and 1 means information is available for only part of the order.
- Coverage of 0 means the order has item records but none has the required information.
- Orders without item records have missing coverage ratios.

### Interpretation and limitations

- Total product volume is the sum of individual item volumes.
  It is not the measured volume of the shipping package.
- Total product weight is based on recorded product measurements.
  It is not a verified shipment weight including packaging.
- `product_category_count` measures category diversity, not the identity
  of the main category.
- Coverage variables describe data completeness. They are not physical
  characteristics of an order.

Product features are conditional purchase-time candidates.
Their use assumes that the product attributes were available at purchase.

## 5. Holiday Features

### Source files

- `data/external/holidays/brazil_national_holidays.csv`
- `data/processed/order_holiday_features.csv`

The calendar contains 27 dates: nine dates in each year from 2016 to 2018.

### Calendar fields

| Field | Description |
|---|---|
| `holiday_date` | Calendar date in YYYY-MM-DD format |
| `holiday_name` | Original holiday name |
| `holiday_name_en` | English holiday name |
| `holiday_type` | Classification used in the research calendar |
| `source_year` | Year covered by the source calendar |
| `source_url` | Source used to verify the entry |

The selected classification is:

`national_as_listed_in_federal_calendar`

Only dates listed as national holidays in the source calendars are included.
Optional days off, local holidays, and partial-day observances are excluded.

This calendar does not establish that all sellers or carriers stopped
operating on those dates.

### Order-level variables

| Variable | Definition | Unit |
|---|---|---|
| `purchase_is_national_holiday` | 1 if the purchase date appears in the selected calendar; otherwise 0 | Binary |
| `days_to_next_national_holiday` | Calendar days from purchase to the next listed holiday, including the purchase date | Days |
| `national_holiday_count_in_estimated_window` | Number of listed holidays after purchase and on or before the estimated delivery date | Holidays |

### Calculation rules

Dates are normalized to calendar dates before comparison.

For `days_to_next_national_holiday`:

- A purchase on a listed holiday receives 0.
- If no next holiday is available within calendar coverage, the result is missing.

For `national_holiday_count_in_estimated_window`, the interval is:

`(purchase_date, estimated_delivery_date]`

Therefore:

- A holiday on the purchase date is excluded.
- A holiday on the estimated delivery date is included.
- Missing or invalid date ranges produce missing values.
- Insufficient calendar coverage must not be interpreted as zero holidays.

### Modeling considerations

The purchase-date flag and distance to the next holiday are calendar-based
candidates, subject to the documented calendar scope.

The holiday count in the estimated window additionally requires the
estimated delivery date to have been known at purchase.

A longer estimated window has more opportunities to contain a holiday.
Regression should consider window length and purchase timing when
interpreting holiday associations.

## 6. Weather Data Preparation

### Source

Weather data come from INMET automatic-station archives for 2016–2018.

Detailed preparation and limitations are documented in:

`docs/inmet_weather_review.md`

### Intermediate files

| File | Role |
|---|---|
| `inmet_state_daily_weather_utc.csv` | Weather measurements at state-day level |
| `order_seller_state_bridge.csv` | Order-to-seller-state mapping and seller weights |
| `order_weather_purchase_scenarios.csv.gz` | Pre-purchase weather under two timezone assumptions |
| `order_weather_retrospective_scenarios.csv.gz` | Handoff-day and arrival-day weather for retrospective analysis only |

These files are stored under:

`data/external/inmet/processed/`

### Daily aggregation rules

- Missing-value codes such as -9999 are converted to missing.
- Missing weather is never interpreted as zero rainfall.
- Daily windows are defined in UTC.
- Hourly rainfall represents the preceding hour.
  The following midnight observation belongs to the preceding rainfall day.
- Each station-day feature requires 24 valid source measurements.
- State values are means across eligible stations.
- A state-level feature requires at least two usable stations and
  at least 50% of the annual station inventory.
- Coverage is evaluated separately for each weather variable.

The annual inventory is a historical coverage reference.
It is not necessarily an operational inventory available at purchase time.

## 7. Weather Feature Names and Units

Weather measurements use two prefixes:

- `destination_`: weather in the customer's state.
- `origin_`: weather aggregated across the states of the order's sellers.

Each suffix below appears with both prefixes.

| Feature suffix | Definition | Unit |
|---|---|---|
| `rain_state_mean_mm` | Mean of complete daily rainfall totals across eligible stations | mm |
| `air_temp_state_mean_c` | Mean of station daily mean air temperatures | °C |
| `air_temp_max_station_mean_c` | Mean of station daily maximum temperatures derived from hourly maxima | °C |
| `air_temp_min_station_mean_c` | Mean of station daily minimum temperatures derived from hourly minima | °C |
| `humidity_state_mean_pct` | Mean of station daily mean relative humidity | % |
| `wind_speed_sample_state_mean_ms` | Mean of station daily averages of reported wind-speed samples | m/s |
| `wind_gust_max_station_mean_ms` | Mean of station daily maximum reported wind gusts | m/s |

Examples:

- `destination_rain_state_mean_mm`
- `origin_rain_state_mean_mm`
- `destination_air_temp_state_mean_c`
- `origin_humidity_state_mean_pct`

There are 14 weather measurement columns: seven at destination
and seven at origin.

### Interpretation limits

- These measurements represent observed stations within states.
- They do not measure weather at the exact customer or seller address.
- They do not describe weather along the full delivery route.
- Temperature extremes and gust values are averages of station-level
  extremes, not the absolute extreme across the entire state.
- Rainfall values are daily weather indices, not monthly rainfall totals.

## 8. Origin Weather and Seller Coverage

### Seller weights

Distinct sellers are counted once per order, regardless of how many
item records they contribute.

For each seller state:

`seller_weight = sellers_in_state / source_seller_count`

Origin weather is calculated as:

`sum(seller_weight × state_weather_value)`

If all seller-state contributions are available, this is equivalent
to averaging state weather across the distinct sellers in the order.

### Missing contributions

If any required seller-state weather contribution is missing,
the full origin weather feature remains missing.

Available weights are not renormalized to produce a partial average.

### Coverage columns

Each origin weather feature has a corresponding column ending in:

`_seller_coverage`

For example:

`origin_rain_state_mean_mm_seller_coverage`

Coverage is the sum of seller weights with valid weather information.

| Coverage | Meaning |
|---|---|
| 1 | All seller contributions have valid weather |
| Between 0 and 1 | Only part of the seller contributions has valid weather |
| 0 | No valid seller-weather contribution |

`has_seller_links` must also be checked to distinguish an order without
seller links from an order whose linked sellers lack weather.

Coverage measures data availability, not weather intensity.

## 9. Timezone Scenarios and Weather Matching

Olist timestamps do not contain timezone information in the supplied files.
Two assumptions are therefore retained:

| Scenario | Interpretation |
|---|---|
| `assume_utc` | Interpret Olist timestamps as UTC |
| `assume_sao_paulo` | Interpret Olist timestamps as America/Sao_Paulo |

Neither scenario is treated as a verified source-timezone convention.

For each scenario, purchase-time weather is selected from the previous
complete UTC day.

The selected weather window must end on or before the assumed
purchase timestamp.

However, completion of the measurement window does not prove that the
data had already been published. INMET publication latency remains
unverified.

Thirteen purchase timestamps remain unresolved under the conservative
São Paulo localization. Their orders are retained with missing
scenario-specific weather.

### Matching and audit fields

| Field | Role |
|---|---|
| `timezone_scenario` | Identifies the timezone assumption |
| `purchase_utc_under_assumption` | Purchase timestamp converted to UTC under that assumption |
| `weather_day_utc` | UTC date selected for the weather lookup |
| `window_end_utc` | End of the selected observation window |
| `weather_lookup` | Merge indicator used to check the destination weather lookup |
| `has_seller_links` | Indicates whether seller links are available |

A successful lookup does not guarantee that every weather measurement
is nonmissing.

These fields support validation and traceability.
They are not default predictors.

## 10. Rules for Statistical Analysis and Machine Learning

### Descriptive analysis and hypothesis testing

- Use orders with valid `is_late` labels when comparing delivery groups.
- Report valid sample sizes and missing values for each feature.
- Do not assume that every analysis uses the same number of orders.
- Orders sharing state-day weather values may be dependent.
- Differences observed in EDA do not establish causality or
  statistical significance.

### Regression

- Document the selected variables, transformations, and reference groups.
- Check related price and weather variables for multicollinearity.
- Consider purchase timing, geography, and estimated window length
  when interpreting additional features.
- Report how missing values change the analysis sample.
- Account for dependence where relevant when estimating uncertainty.

### Early prediction

- Use an explicit list of approved or conditionally accepted predictors.
- Document assumptions about price, seller, product, delivery-estimate,
  and weather availability at purchase.
- Exclude actual delivery dates, realized delays, final order status,
  and other post-purchase information.
- Exclude handoff-day and arrival-day weather from purchase-time inputs.
- Fit learned preprocessing and resampling only on training data.
- Evaluate timezone assumptions separately.
- Compare feature groups using the same evaluation orders and split rules.

## 11. Related Notebooks

| Notebook | Purpose |
|---|---|
| `0x_price_product_features.ipynb` | Validate totals and create price/product features |
| `0x_holiday_feature_engineering.ipynb` | Create order-level holiday features |
| `inmet_weather_preparation.ipynb` | Prepare and match weather data |
| `0x_combined_weather_price_holiday.ipynb` | Merge feature groups and export scenario-specific datasets |
| `0x_enriched_data_visualization.ipynb` | Explore the combined features and delivery labels |

Price/product, holiday, and weather preparation must be completed
before running the combined-data notebook.

Run the visualization notebook after the combined datasets are available.