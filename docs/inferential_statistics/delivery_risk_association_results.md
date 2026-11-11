# Inferential Statistics — Stage 3

## 1. Objective

Stage 3 evaluated whether the differences observed in exploratory data analysis (EDA) were supported by inferential evidence. The goal was to estimate the magnitude of differences, quantify uncertainty, and test whether observed patterns were statistically distinguishable under the planned methods. This stage does **not** train machine-learning models and does **not** establish causation.

The main research question was:

> Which characteristics are associated with late delivery, how large are the observed differences, and how uncertain are these estimates?

## 2. Data used

- Primary analytic dataset: `data/processed/research_data_weather_price_holiday_assume_utc.csv`
- Each row represents one `order_id`
- The main late-delivery analyses used labeled orders with `is_late` equal to 0 (Not Late) or 1 (Late)
- Missing values were removed only for the specific variable used in each analysis
- RQ19 used a separate review-linked sample
- RQ20 used the full order-level dataset and was not restricted to delivered orders

## 3. Statistical design

- Significance level: 0.05
- Two-sided alternatives were used for relevant continuous and binary comparisons. Chi-square association tests use the right tail of the chi-square reference distribution.
- Multiple-testing adjustment: Holm family-wise correction across all 26 pre-specified primary tests
- Continuous variables were analysed with Welch t-tests, Mann–Whitney U tests, or temporal block bootstrap procedures, depending on the research question
- Categorical associations were analysed using Pearson chi-square, Fisher's exact test, or conditional Monte Carlo chi-square when sparse cells required it

## 4. Overall results

- Number of primary tests: 26
- Significant after Holm correction: 26
- Not significant after Holm correction: 0
- Review association: RQ19 (low review vs late delivery), signed Phi = 0.396430. Effect sizes with different units or definitions are not ranked against one another.

Of 26 primary tests, 26 met the Holm-adjusted significance criterion and 0 did not. Statistical significance alone does not establish practical importance.

## 5. Final summary table

| RQ | Variable | n | Raw p | Holm p | Reject H0 after Holm | Effect size |
|---|---|---:|---:|---:|---|---:|
| RQ1 | customer_state | 96470 | 5.00e-05 | 0.000700 | Yes | 0.136057 |
| RQ2 | purchase_weekday | 96470 | 0.000199 | 0.002393 | Yes | 0.016498 |
| RQ3 | purchase_month | 96470 | 5.00e-05 | 0.000700 | Yes | 0.193282 |
| RQ4 | has_interstate_seller | 96470 | 3.60e-96 | 8.65e-95 | Yes | 0.066996 |
| RQ5 | distance_km_mean | 95990 | 1.98e-102 | 4.95e-101 | Yes | 0.159501 |
| RQ6 | order_total_value | 96470 | 1.20e-08 | 2.04e-07 | Yes | 17.498366 |
| RQ6 | freight_value | 96470 | 2.71e-18 | 5.97e-17 | Yes | 2.640652 |
| RQ7 | freight_to_items_ratio | 96470 | 0.008439 | 0.016878 | Yes | 0.010814 |
| RQ7 | mean_item_value | 96470 | 1.98e-10 | 3.56e-09 | Yes | 18.007127 |
| RQ7 | freight_per_item | 96470 | 1.79e-37 | 4.11e-36 | Yes | 3.023919 |
| RQ8 | total_product_weight_g | 96448 | 3.04e-07 | 4.57e-06 | Yes | 0.037871 |
| RQ8 | total_product_volume_cm3 | 96454 | 0.002641 | 0.010565 | Yes | 0.022242 |
| RQ9 | seller_count_group | 96470 | 1.87e-16 | 3.74e-15 | Yes | -0.026498 |
| RQ10 | product_category_count | 95078 | 1.94e-08 | 3.10e-07 | Yes | -0.018218 |
| RQ11 | estimated_window_days | 96470 | 2.69e-12 | 5.12e-11 | Yes | -0.051689 |
| RQ12 | purchase_is_national_holiday | 96470 | 0.003435 | 0.010565 | Yes | -0.009420 |
| RQ13 | national_holiday_count_in_estimated_window | 96470 | 0.001751 | 0.008757 | Yes | 0.011471 |
| RQ14 | days_to_next_national_holiday | 96470 | 4.52e-17 | 9.50e-16 | Yes | 0.028655 |
| RQ15a | origin_rain_state_mean_mm | 96311 | 0.000500 | 0.005497 | Yes | 1.110220 |
| RQ15b | destination_rain_state_mean_mm | 95544 | 0.000500 | 0.005497 | Yes | 1.314173 |
| RQ16a | origin_humidity_state_mean_pct | 96317 | 0.000500 | 0.005497 | Yes | 2.215929 |
| RQ16b | destination_humidity_state_mean_pct | 95700 | 0.000500 | 0.005497 | Yes | 2.743005 |
| RQ17a | origin_air_temp_state_mean_c | 96332 | 0.000500 | 0.005497 | Yes | 1.163361 |
| RQ17b | destination_air_temp_state_mean_c | 95884 | 0.000500 | 0.005497 | Yes | 1.210311 |
| RQ19 | low_review | 95824 | Numerically underflowed (reported as 0) | Numerically underflowed (reported as 0) | Yes | 0.396430 |
| RQ20 | customer_state | 99441 | 0.014799 | 0.016878 | Yes | 0.021905 |

## 6. Research-question summaries

## RQ1 — Customer state and late delivery

- Variable(s): `customer_state`, `is_late`
- Sample size: 96470
- Method: Chi-square statistic with conditional Monte Carlo p
- Effect size: Cramér's V = 0.136057
- Raw p-value: 5.00e-05
- Holm-adjusted p-value: 0.000700
- Interpretation: assess the reported estimate, confidence interval and Holm-adjusted p-value together; this observational comparison does not establish causation.

## RQ2 — Purchase weekday and late delivery

- Variable(s): `purchase_weekday`, `is_late`
- Sample size: 96470
- Method: Pearson Chi-square
- Effect size: Cramér's V = 0.016498
- Raw p-value: 0.000199
- Holm-adjusted p-value: 0.002393
- Interpretation: assess the reported estimate, confidence interval and Holm-adjusted p-value together; this observational comparison does not establish causation.

## RQ3 — Purchase month and late delivery

- Variable(s): `purchase_month`, `is_late`
- Sample size: 96470
- Method: Chi-square statistic with conditional Monte Carlo p
- Effect size: Cramér's V = 0.193282
- Raw p-value: 5.00e-05
- Holm-adjusted p-value: 0.000700
- Interpretation: assess the reported estimate, confidence interval and Holm-adjusted p-value together; this observational comparison does not establish causation.

## RQ4 — Interstate seller and late delivery

- Variable(s): `has_interstate_seller`, `is_late`
- Sample size: 96470
- Method: Pearson Chi-square
- Risk difference: 3.5107 percentage points
- 95% CI: [3.2026, 3.8153] percentage points
- Effect size: Phi = 0.066996
- Raw p-value: 3.60e-96
- Holm-adjusted p-value: 8.65e-95
- Interpretation: assess the reported estimate, confidence interval and Holm-adjusted p-value together; this observational comparison does not establish causation.

## RQ5 — Distance and late delivery

- Variable(s): `distance_km_mean`, `is_late`
- Sample size: 95990
- Method: Mann-Whitney U (asymptotic, two-sided)
- Effect size: Rank-biserial correlation = 0.159501
- 95% CI: [0.146281, 0.172708]
- Raw p-value: 1.98e-102
- Holm-adjusted p-value: 4.95e-101
- Interpretation: assess the reported estimate, confidence interval and Holm-adjusted p-value together; this observational comparison does not establish causation.

## RQ6 — Order value and freight value

Two separate Welch t-tests were used.

### RQ6a — `order_total_value`
- Mean difference (Late - Not Late): 17.4984 BRL
- 95% CI: [11.4867, 23.5100]
- Raw p-value: 1.20e-08
- Holm-adjusted p-value: 2.04e-07

### RQ6b — `freight_value`
- Mean difference (Late - Not Late): 2.6407 BRL
- 95% CI: [2.0488, 3.2325]
- Raw p-value: 2.71e-18
- Holm-adjusted p-value: 5.97e-17

Sensitivity analysis using 10% trimmed means showed the same direction of differences, although the estimands differ.

## RQ7 — Relative freight cost and item value

Three separate Welch t-tests were used.

### RQ7a — `freight_to_items_ratio`
- Mean difference (Late - Not Late): 0.010814
- 95% CI: [0.002768, 0.018859]
- Raw p-value: 0.008439
- Holm-adjusted p-value: 0.016878

### RQ7b — `mean_item_value`
- Mean difference (Late - Not Late): 18.0071 BRL/item
- 95% CI: [12.4677, 23.5465]
- Raw p-value: 1.98e-10
- Holm-adjusted p-value: 3.56e-09

### RQ7c — `freight_per_item`
- Mean difference (Late - Not Late): 3.0239 BRL/item
- 95% CI: [2.5632, 3.4846]
- Raw p-value: 1.79e-37
- Holm-adjusted p-value: 4.11e-36

Sensitivity analysis showed that `freight_to_items_ratio` was the most fragile among the three variables: the trimmed-mean test was weaker than the primary Welch result. This should be discussed carefully.

## RQ8 — Product weight and volume

Two separate Mann–Whitney U tests were used.

### RQ8a — `total_product_weight_g`
- Rank-biserial correlation: 0.037871
- 95% CI: [0.026322, 0.051129]
- Raw p-value: 3.04e-07
- Holm-adjusted p-value: 4.57e-06

### RQ8b — `total_product_volume_cm3`
- Rank-biserial correlation: 0.022242
- 95% CI: [0.008577, 0.034281]
- Raw p-value: 0.002641
- Holm-adjusted p-value: 0.010565

Both effects were statistically significant but small.

## RQ9 — Seller count group and late delivery

- Variable(s): `seller_count_group`, `is_late`
- Method: Pearson Chi-square
- Risk difference: -5.8305 percentage points
- 95% CI: [-6.2834, -5.0961]
- Holm-adjusted p-value: 3.74e-15
- Interpretation: assess the reported estimate, confidence interval and Holm-adjusted p-value together; this observational comparison does not establish causation.

## RQ10 — Product-category count group and late delivery

- Variable(s): `product_category_count_group`, `is_late`
- Method: Pearson Chi-square
- Risk difference: -5.2782 percentage points
- 95% CI: [-5.9701, -4.0805]
- Holm-adjusted p-value: 3.10e-07
- Interpretation: assess the reported estimate, confidence interval and Holm-adjusted p-value together; this observational comparison does not establish causation.

## RQ11 — Estimated delivery window and late delivery

- Variable(s): `estimated_window_days`, `is_late`
- Method: Mann-Whitney U (two-sided)
- Rank-biserial correlation: -0.051689
- 95% CI: [-0.064536, -0.039512]
- Holm-adjusted p-value: 5.12e-11
- Interpretation: assess the reported estimate, confidence interval and Holm-adjusted p-value together; this observational comparison does not establish causation.

## RQ12 — National holiday purchase day and late delivery

- Variable(s): `purchase_is_national_holiday`, `is_late`
- Method: Pearson Chi-square
- Risk difference: -1.9279 percentage points
- 95% CI: [-2.9270, -0.6976]
- Holm-adjusted p-value: 0.010565
- Interpretation: assess the reported estimate, confidence interval and Holm-adjusted p-value together; this observational comparison does not establish causation.

## RQ13 — Number of holidays in the estimated delivery window

- Variable(s): `national_holiday_count_group`, `is_late`
- Method: Pearson Chi-square
- Effect size: Cramér's V = 0.011471
- Holm-adjusted p-value: 0.008757
- Interpretation: assess the reported estimate, confidence interval and Holm-adjusted p-value together; this observational comparison does not establish causation.

## RQ14 — Days to the next national holiday

- Variable(s): `days_to_next_holiday_group`, `is_late`
- Method: Pearson Chi-square
- Effect size: Cramér's V = 0.028655
- Holm-adjusted p-value: 9.50e-16
- Interpretation: assess the reported estimate, confidence interval and Holm-adjusted p-value together; this observational comparison does not establish causation.

## RQ15–RQ17 — Weather before purchase and late delivery

Six separate temporal block bootstrap analyses were used (7-day blocks as primary analysis; 14-day blocks as sensitivity analysis).

- RQ15a (`origin_rain_state_mean_mm`): mean difference = 1.1102; 95% CI [0.5566, 1.6056]; Holm-adjusted p-value = 0.005497.
- RQ15b (`destination_rain_state_mean_mm`): mean difference = 1.3142; 95% CI [0.7939, 1.7671]; Holm-adjusted p-value = 0.005497.
- RQ16a (`origin_humidity_state_mean_pct`): mean difference = 2.2159; 95% CI [1.1715, 3.1354]; Holm-adjusted p-value = 0.005497.
- RQ16b (`destination_humidity_state_mean_pct`): mean difference = 2.7430; 95% CI [1.8343, 3.5857]; Holm-adjusted p-value = 0.005497.
- RQ17a (`origin_air_temp_state_mean_c`): mean difference = 1.1634; 95% CI [0.7218, 1.5725]; Holm-adjusted p-value = 0.005497.
- RQ17b (`destination_air_temp_state_mean_c`): mean difference = 1.2103; 95% CI [0.7698, 1.6198]; Holm-adjusted p-value = 0.005497.

Interpretation: all six weather comparisons showed positive mean differences (Late - Not Late), but conclusions remain sensitive to assumptions about temporal dependence, shared state-day weather measurements, and the adopted UTC scenario.
## RQ19 — Low review and late delivery

- Variable(s): `low_review`, `is_late`
- Review rule: low review = 1–2 stars
- Sample size after excluding missing reviews: 95824
- Missing reviews excluded: 646
- Method: Pearson Chi-square
- Low-review rate in Late group: 62.4040%
- Low-review rate in Not Late group: 9.2685%
- Risk difference: 53.1355 percentage points
- 95% CI: [51.9247, 54.3311]
- Effect size: Phi = 0.396430
- Holm-adjusted p-value: Numerically underflowed (reported as 0)

The observed review association has signed Phi = 0.396430. Reviews occur after delivery, so this result is not a purchase-time predictor and must not be interpreted causally. Duplicate valid reviews existed for some orders, and the analysis kept one selected valid review per order using a deterministic rule.

## RQ20 — Cancellation and customer state

- Variable(s): `is_canceled`, `customer_state`
- Sample size: 99441
- Method: Conditional Monte Carlo Chi-square
- Effect size: Cramér's V = 0.021905
- Raw p-value: 0.014799
- Holm-adjusted p-value: 0.016878
- Interpretation: assess the reported estimate, confidence interval and Holm-adjusted p-value together; this observational comparison does not establish causation.


## 7. Key interpretation points

1. **26 of 26 planned primary tests met the Holm-adjusted significance criterion**. Assess effect sizes and uncertainty separately.
2. **RQ19 (`low_review`) has signed Phi = 0.396430**. Reviews occur after delivery, so this result concerns outcome interpretation, not predictive feature selection at purchase time.
3. **Review practical magnitude and uncertainty separately from significance**, including:
   - RQ7 `freight_to_items_ratio`
   - RQ20 cancellation by state
   - several holiday-related variables with very small Cramér's V / Phi values
4. **Weather results were based on temporal block bootstrap**, not ordinary independent-order tests, because many orders shared the same state-day weather context.
5. **No post hoc pairwise group-comparison file was created** because the Stage 3 workflow did not include a finalized family of additional pairwise comparisons beyond the pre-specified primary tests.

## 8. Limitations

- This stage estimates association, **not causation**
- Many tests assume order-level independence or only partially address dependence
- Weather analyses still rely on assumptions about block independence and the UTC scenario
- `estimated_window_days` is conceptually related to the construction of the late-delivery outcome
- Review analysis required a deterministic rule to select one valid review per order when multiple reviews existed
- Cancellation analysis used a broad non-canceled comparison group that included delivered and in-progress orders
- Some statistically significant effects were practically small

## 9. Output files

### Tables
- `outputs/tables/inferential_statistics/sample_summary.csv`
- `outputs/tables/inferential_statistics/descriptive_summary.csv`
- `outputs/tables/inferential_statistics/statistical_test_results.csv`
- `outputs/tables/inferential_statistics/weather_test_results.csv`

### Figures
- `outputs/figures/inferential_statistics/rq1_late_rate_by_customer_state.png`
- `outputs/figures/inferential_statistics/rq3_monthly_late_delivery_rates.png`
- `outputs/figures/inferential_statistics/rq19_low_review_by_delivery_status.png`
- `outputs/figures/inferential_statistics/rq15_rq17_weather_mean_differences.png`

## 10. Completion note

Stage 3 inferential-statistics analysis is complete at the level of the planned primary tests, exported tables, and key figures. Any future Stage 4 modeling should not rely only on p-values; feature choice must also consider leakage, timing, interpretability, and dependence structure.
