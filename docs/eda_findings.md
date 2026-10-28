# EDA Findings (ENG) – Late Delivery EDA (Stage 2 · TASK 02)

**Owner:** Phong · **Source:** `data/processed/research_data.csv` (99,441 rows, 34 columns; 1 row = 1 order, unique `order_id`) · **Notebook:** `notebooks/03_late_delivery_eda.ipynb` (TASK 03 is reported separately in `class_imbalance_findings_eng.md`, notebook `03b_class_imbalance_analysis.ipynb`)

> Figures below are computed from `research_data.csv`; charts are generated when the notebook is run (file names are given per section, saved in `outputs/figures/`; CSV tables in `outputs/tables/`).
> All comments are **descriptive observations** – no causal conclusions and no statistical-significance conclusions.

## 0. Sample scope & conventions

| Item | Orders | % of total |
|---|---:|---:|
| All orders | 99,441 | 100.00 |
| Orders with `delivered` status | 96,478 | 97.02 |
| **Orders with a valid `is_late` label (analysis sample)** | **96,470** | 97.01 |
| – Late (`is_late = 1`) | 6,534 | 6.57 |
| – Not Late (`is_late = 0`) | 89,936 | 90.44 |
| Orders without a label | 2,971 | 2.99 |
| – not `delivered` | 2,963 | 2.98 |
| – `delivered` but missing actual delivery date | 8 | 0.01 |

- Every late rate uses **orders with a valid label** as the denominator. Cancelled / undelivered / missing-date orders are not treated as "not late".
- Groups with `valid_orders < 100` are flagged *unstable*; `< 30` are flagged *do not interpret*.
- `estimated_window_days` (estimated date − purchase date) and `delivery_delay_days` (actual delivery − estimated date) are taken from the **existing columns** of the 34-column file (TASK 01, calendar days); the notebook recomputes them independently for **reconciliation** (never overwritten; any mismatch is only reported). Check `is_late = 1 ⇔ delivery_delay_days > 0` agrees **100%**.
- **Classification:** `delivery_delay_days` is not a model input. `estimated_window_days` may be used only if the estimated date is known at prediction time – to be confirmed in TASK 04.
- Missing values are not replaced by 0. In the valid sample: `distance_km_mean` is missing for 480 orders (0.50%), `promised_days` for 18 orders; `freight_value` and `estimated_window_days` have no missing values. `promised_days` is missing for 18 valid orders = **14 with a missing approval date + 4 with negative values turned into missing**.

---

## EDA01 – Late / Not Late distribution · `eda01_late_distribution.png`

| Label | Orders | % |
|---|---:|---:|
| Not Late (0) | 89,936 | 93.23 |
| Late (1) | 6,534 | 6.77 |

**Findings:** Late is clearly the minority class (6.77%). Details in the TASK 03 report (`class_imbalance_findings_eng.md`).

## EDA02 – Late rate by purchase weekday · `eda02_late_rate_by_weekday.png`

| Weekday | Valid | Late | Late rate |
|---|---:|---:|---:|
| Monday | 15,701 | 1,168 | 7.44% |
| Tuesday | 15,502 | 1,093 | 7.05% |
| Wednesday | 15,074 | 990 | 6.57% |
| Thursday | 14,322 | 903 | 6.31% |
| Friday | 13,684 | 960 | 7.02% |
| Saturday | 10,555 | 696 | 6.59% |
| Sunday | 11,632 | 724 | 6.22% |

**Findings:** Rates vary narrowly (6.22% – 7.44%, ~1.2 points) around the overall 6.77%; Monday/Tuesday/Friday are slightly higher, Sunday/Thursday lowest. Group sizes are large (> 10,000 orders); uncertainty is not quantified in this task and no test was run, so no claim of a real difference is made.

## EDA03 – Late rate by month · `eda03_late_rate_by_month.png`

| Month | Valid | Late | Late rate | Note |
|---|---:|---:|---:|---|
| 2016-09 | 1 | 1 | 100.00% | n too low, not interpreted |
| 2016-10 | 265 | 2 | 0.75% | n ≥ 100 so plotted; lowest among months with n ≥ 100 |
| 2016-12 | 1 | 0 | 0.00% | n too low, not interpreted |
| 2017-01 | 750 | 22 | 2.93% | |
| 2017-02 | 1,653 | 49 | 2.96% | |
| 2017-03 | 2,546 | 116 | 4.56% | |
| 2017-04 | 2,303 | 151 | 6.56% | |
| 2017-05 | 3,545 | 106 | 2.99% | |
| 2017-06 | 3,135 | 95 | 3.03% | |
| 2017-07 | 3,872 | 108 | 2.79% | |
| 2017-08 | 4,193 | 122 | 2.91% | |
| 2017-09 | 4,150 | 182 | 4.39% | |
| 2017-10 | 4,478 | 187 | 4.18% | |
| 2017-11 | 7,288 | 904 | 12.40% | |
| 2017-12 | 5,513 | 411 | 7.46% | |
| 2018-01 | 7,069 | 403 | 5.70% | |
| 2018-02 | 6,555 | 926 | 14.13% | |
| 2018-03 | 7,003 | 1,328 | 18.96% | highest |
| 2018-04 | 6,798 | 306 | 4.50% | |
| 2018-05 | 6,749 | 443 | 6.56% | |
| 2018-06 | 6,096 | 71 | 1.16% | lowest within 2017–2018 |
| 2018-07 | 6,156 | 208 | 3.38% | |
| 2018-08 | 6,351 | 393 | 6.19% | |

**Findings:** Among months with n ≥ 100 the lowest is **2016-10 (0.75%, n = 265)**; within 2017–2018 alone the lowest is **2018-06 (1.16%)**. Mid-2017 is ≈2.8–3.0% (2017-05 to 2017-08), then 12.4% in 2017-11, peaking at 18.96% in 2018-03 (14.1% in 2018-02). The chart uses a **datetime axis** and plots only months with n ≥ 100: **only 2016-09 (n = 1) and 2016-12 (n = 1) are dropped**; 2016-11 has no labelled orders and is left as a gap; 2016-10 is plotted but stands alone (not connected to 2017-01). No causal or seasonality claim. Wilson 95% CIs and monthly data completeness belong to TASK 06.

## EDA04 – Late rate by customer state · `eda04_late_rate_by_state.png`

Highest / lowest (all 27 states in `eda04_late_rate_by_state.csv`):

| State | Valid | Late | Late rate | | State | Valid | Late | Late rate |
|---|---:|---:|---:|---|---|---:|---:|---:|
| AL | 397 | 85 | 21.41% | | PR | 4,923 | 199 | 4.04% |
| MA | 717 | 125 | 17.43% | | SP | 40,494 | 1,820 | 4.49% |
| SE | 335 | 51 | 15.22% | | MG | 11,354 | 519 | 4.57% |
| PI | 476 | 66 | 13.87% | | DF | 2,080 | 118 | 5.67% |
| CE | 1,279 | 176 | 13.76% | | MT | 886 | 53 | 5.98% |
| BA | 3,256 | 396 | 12.16% | | RS | 5,344 | 325 | 6.08% |
| RJ | 12,350 | 1,495 | 12.11% | | GO | 1,957 | 128 | 6.54% |

**Small-sample warning (n < 100):** AP (67 orders, 2.99%), RR (41, 12.20%), AC (80, 3.75%) – not directly comparable. AM (145 orders, 2.76%) and RO (243, 2.88%) are also small; interpret with care.

**Findings:** Differences between states are very large. Some states have low rates (PR 4.0%, SP 4.5%, MG 4.6% among large states; AM 2.8% and RO 2.9% are lower but have small samples). RJ (12.1%, n = 12,350) and BA (12.2%) are almost three times SP/PR/MG; the north-eastern states (AL, MA, SE, PI, CE, BA) generally have high late rates. SP is ~42% of the sample, so the overall rate is pulled toward SP's level. No test was run; small groups cannot be judged from the rate alone.

## EDA05 – Late rate by distance group · `eda05_late_rate_by_distance_group.png`

**Grouping:** `distance_km_mean` (Haversine, straight-line), half-open intervals `[a, b)`. **Missing:** not assigned to any group; reported separately.

| Group | Valid | Late | Late rate | Share (of 96,470) |
|---|---:|---:|---:|---:|
| 0–100 km | 17,815 | 796 | 4.47% | 18.47% |
| 100–300 km | 13,440 | 693 | 5.16% | 13.93% |
| 300–600 km | 31,485 | 2,128 | 6.76% | 32.64% |
| 600–1,000 km | 17,910 | 1,272 | 7.10% | 18.57% |
| 1,000–2,000 km | 9,727 | 924 | 9.50% | 10.08% |
| ≥ 2,000 km | 5,613 | 676 | 12.04% | 5.82% |
| *Missing distance* | 480 | 45 | 9.38% | 0.50% |

**Findings:** The late rate rises steadily with distance; the farthest group is ~2.7× the nearest. Every group has n > 5,000. Distance may co-vary with state, promised window, etc., so no causal conclusion.

## EDA06 – Freight value: Late vs Not Late · `eda06_freight_by_late.png`

| Group | n | Mean | SD | Q1 | Median | Q3 | IQR | Max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Not Late | 89,936 | 22.61 | 21.38 | 13.71 | 17.06 | 23.85 | 10.14 | 1,794.96 |
| Late | 6,534 | 25.25 | 23.72 | 15.10 | 18.23 | 26.90 | 11.80 | 711.33 |

**Findings:** No missing values. Strongly right-skewed. The Late group has slightly higher freight (median 18.23 vs 17.06; ≈ +1.17) but the spread is large, so the two distributions overlap heavily. Freight may correlate with distance/weight → possible confounding.

## EDA07 – Estimated window: Late vs Not Late · `eda07_estimated_window_by_late.png`

| Group | n | Mean | SD | Q1 | Median | Q3 | IQR | Max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Not Late | 89,936 | 24.45 | 8.83 | 19 | 24 | 29 | 10 | 156 |
| Late | 6,534 | 23.29 | 7.57 | 20 | 23 | 28 | 8 | 70 |

Supplementary – late rate by estimated-window group (`eda07_late_rate_by_estimated_window_group.png`):

| Group (days) | Valid | Late | Late rate |
|---|---:|---:|---:|
| ≤ 15 | 14,039 | 829 | 5.91% |
| 16–20 | 16,625 | 1,183 | 7.12% |
| 21–25 | 26,374 | 2,142 | 8.12% |
| 26–30 | 19,560 | 1,395 | 7.13% |
| 31–40 | 16,016 | 898 | 5.61% |
| > 40 | 3,856 | 87 | 2.26% |

**Findings:** Late orders have a slightly shorter estimated window (median 23 vs 24 days) and less spread (IQR 8 vs 10). The relationship is **non-monotonic**: the late rate is highest in the 21–25-day group and lowest in the > 40-day group (one explanatory hypothesis, not a causal conclusion: a very long window leaves extra slack). `promised_days` (counted from approval) gives similar results (median 23 vs 23); it is missing for 18 orders = 14 with a missing approval date + 4 negative values turned into missing. Other variables are not controlled for.

## EDA08 – Distribution of delivery delay days · `eda08_delivery_delay_hist.png`

| Statistic | Value |
|---|---:|
| n | 96,470 |
| Median | −12 days |
| Mean ± SD | −11.88 ± 10.18 |
| p5 / p95 / p99 | −26 / 3 / 18 |
| Min / Max | −147 / 188 |

| Group | Orders | % |
|---|---:|---:|
| Early (< 0) | 88,644 | 91.89 |
| On the promised day (= 0) | 1,292 | 1.34 |
| Late (> 0) | 6,534 | 6.77 |

Among Late orders: median 7 days, Q1–Q3 = 3–13, p90 = 22.

**Findings:** The distribution is concentrated on the early side (peak around −15 days); the right (late) tail is longer and heavier than the left. 228 orders lie outside the displayed range [−60, 40] (34 more than 60 days early, 194 more than 40 days late), so outlier-sensitive statistics (mean, SD) need care. By the checks performed there are no missing or negative values in `estimated_window_days`.

## Data limitations & caveats
1. The sample contains only **delivered** orders with valid dates → possible selection (survivorship) bias, especially in the last months.
2. Olist data is historical (2016–2018) and not a random sample of Brazil; orders of the same customer/seller/period may be dependent.
3. 2016-09, 2016-10 and 2016-12 have very few labelled orders.
4. Distance is straight-line; 480 valid orders lack a distance.
5. EDA observations may be confounded (state – distance – freight – estimated window) and are not controlled for.

## Suggested hypotheses for the Inference stage
- Late rate differs across states (Chi-square, Cramér's V).
- Late rate increases with distance (trend across groups / logistic regression).
- Estimated window differs between Late and Not Late (Welch / Mann–Whitney); note the non-monotonic relationship.
- Late rate varies by month (Chi-square / logistic regression, together with TASK 06 Wilson CIs).
