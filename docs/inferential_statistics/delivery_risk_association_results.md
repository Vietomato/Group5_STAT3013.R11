# Delivery risk association results

Four two-sided primary tests; Holm across four tests. Reviews are descriptive only. The reporting scope changed after earlier analyses; this is exploratory, not prospectively registered inference.

| RQ | Variable | n | Estimate | Pointwise 95% CI | Raw p | Holm p |
|---|---|---:|---:|---|---:|---:|
| RQ1 | distance_km_mean | 95990 | 0.159501 | [0.146281, 0.172708] | 1.98063e-102 | 7.92252e-102 |
| RQ2 | freight_value | 96470 | 2.64065 | [2.04878, 3.23252] | 2.71148e-18 | 8.13445e-18 |
| RQ3 | purchase_is_national_holiday | 96470 | -0.0192786 | [-0.0292701, -0.00697559] | 0.00343521 | 0.00343521 |
| RQ4 | destination_rain_state_mean_mm | 95544 | 1.31417 | [0.793928, 1.76708] | 0.00049975 | 0.0009995 |

RQ1: rank-biserial; RQ2: Late minus Not Late mean freight in BRL; RQ3: holiday minus non-holiday risk difference as a proportion; RQ4: Late minus Not Late mean pre-purchase rain in mm. CIs are pointwise, not simultaneous. Mann-Whitney is not automatically a median test. Weather uses whole seven-day blocks; fourteen-day sensitivity is supplementary. Dependence, selection, UTC and weather-publication assumptions remain limitations.

Review selection keeps the latest valid creation date, then answer time and ID. Missing reviews are excluded. Review coverage and descriptive rates are exported without hypothesis tests. EDA uses a first-review rule, so review rates can differ slightly.
