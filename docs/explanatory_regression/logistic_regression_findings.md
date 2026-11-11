# Logistic Regression Findings

## 1. Objective and Scope

This analysis examines associations between late
delivery and selected purchase-time characteristics.

M0 contains the basic predictor group.
M4 adds price, product, holiday and weather variables.

Calendar-adjusted versions are supplementary sensitivity
analyses. All reported associations are observational.
They do not establish causal effects or demonstrate
out-of-sample predictive performance.

## 2. Data and Analysis Sample

Source:
`data/processed/research_data_weather_price_holiday_assume_utc.csv`

Source SHA256:
`ed604fa22a2c95695036966f80a0f8a4666fb242bc2ab9f781ed8fb68630ff4c`

Training assignments come from:
`data/ml_preparation/split_manifest.csv`

Training purchases precede 2 March 2018.
The manifest also applies a delivery-label availability
cutoff before 16 April 2018.

| Sample | Orders | Late orders | Late percentage |
|---|---:|---:|---:|
| Manifest training sample | 57,449 | 3,720 | 6.475% |
| Common complete-case sample | 56,553 | 3,649 | 6.452% |
| Excluded for missing predictors | 896 | 71 | 7.924% |

Complete cases were defined using all 13 main predictors.
Both M0 and M4 therefore use the same observations.

The excluded group had a higher observed late percentage.
Complete-case exclusion may introduce selection bias.
Manifest label-availability exclusions are another source
of outcome-related selection.

## 3. Predictor Representation

M0 includes:

- Distance.
- Customer state.
- Item count.
- Seller multiplicity.
- Purchase weekday.
- Estimated delivery window.

M4 additionally includes:

- Item value.
- Freight value.
- Product weight.
- Product volume.
- Purchase on a national holiday.
- Holiday count within the estimated delivery window.
- Destination rainfall before purchase.

Seller multiplicity compares two or more sellers
with one seller. Separate groups with three or more
sellers contained few orders and no late outcomes.

SP is the reference customer state.
Monday is the reference purchase weekday.

The transformed specifications use log1p terms for
distance, item value, freight, weight, volume and rain.

These transformations use the previously rescaled units:
100 km, 100 BRL, 10 BRL, 1 kg, 10,000 cm3 and 5 mm,
respectively.

The estimated window uses `(days - 25) / 10` and its
square. Item count and holiday count remain linear.

No class balancing, resampling or regularization was
used in these explanatory regressions.

Conditional predictors retain the shared assumptions
about availability at purchase. These include seller
assignment, prices, freight, product attributes and
the delivery estimate.

Weather is a state-level index. It does not measure
conditions at an exact address or along a delivery route.
Historical publication timing remains an assumption.

## 4. Functional Form and Calendar Sensitivity

Residual screening identified patterns in the initial
linear specifications. A transformed specification was
then examined on the same sample.

Further checks showed substantial differences between
observed and fitted late percentages across months.

For example, transformed M4 estimated 7.712% for
November 2017, compared with 12.434% observed.
For February 2018, the corresponding values were
6.996% and 12.686%.

Calendar indicators were therefore added as an
exploratory sensitivity analysis.

The shared protocol reserves year-month for splitting
and auditing. Its use as an adjustment factor here is
an explicit Stage 4 extension for review.

Purchases in 2016 were pooled into one category.
Subsequent year-months were retained separately.
January 2017 is the reference period.

The March 2018 training group contains purchases from
1 March only. It does not represent the full month.

| Specification | Parameters | AIC |
|---|---:|---:|
| M0 initial | 37 | 25669.39 |
| M4 initial | 44 | 25538.19 |
| M0 transformed | 38 | 25599.54 |
| M4 transformed | 45 | 25379.62 |
| M0 calendar-adjusted | 53 | 24290.89 |
| M4 calendar-adjusted | 60 | 24160.99 |

All specifications converged without fitting warnings.

Lower AIC and closer training-period agreement do not
independently validate predictive performance.
Transformations and calendar adjustment were developed
after inspecting training diagnostics.

## 5. Uncertainty Estimation

The main intervals use cluster-robust covariance
with 65 nonempty seven-day blocks.

Sensitivity intervals use 35 nonempty fourteen-day
blocks. Both use the UTC anchor of 12 September 2016.

Finite-sample covariance correction and t-based
inference are applied. Degrees of freedom are 64
and 34, respectively.

The method allows dependence within each block.
Dependence between blocks may remain.

Some covariance matrices are rank deficient, including
the seven-day calendar-adjusted specifications.
Full-model joint Wald tests are not reported.
Each reported scalar contrast has a finite, positive
estimated variance.

Intervals and p-values are pointwise, without multiple
comparison adjustment. They do not account for the
exploratory selection of functional forms.

## 6. Calendar-Adjusted Results and Sensitivity

> Draft for review. Report sections 4.4.1 and 6.1 and
> a detailed numerical comparison with Stage 3 are pending.
> M0 and M4 were prioritised. Supplementary models M1–M3
> have not been fitted.

The following results use calendar-adjusted M4 and
seven-day clustering.

| Contrast | Adjusted OR | 95% CI | p-value |
|---|---:|---|---:|
| Distance: 200 vs 100 km | 1.2106 | [1.1490, 1.2756] | 5.43e-10 |
| Freight: 20 vs 10 BRL | 1.0336 | [0.9263, 1.1532] | 0.549 |
| Purchase holiday vs non-holiday | 0.5116 | [0.3352, 0.7810] | 0.00237 |
| Holiday count in estimated window: 1 vs 0 | 0.9013 | [0.6704, 1.2118] | 0.486 |
| Rainfall index: 5 vs 0 mm | 1.0361 | [0.9757, 1.1001] | 0.242 |

For the specified distance contrast, estimated odds
were approximately 21.1% higher after adjustment.
This is an odds comparison, not a probability increase.

The freight and delivery-window holiday-count
intervals included 1. The estimates do not establish
an absence of association.

Purchase on a holiday was associated with lower odds.
This does not establish that holiday purchases reduce
delivery delays.

### Rainfall Sensitivity

Without calendar adjustment, the OR for a rainfall
index of 5 versus 0 mm was 1.2895, with a 95% CI of
[1.1685, 1.4231].

After calendar adjustment, the OR was 1.0361, with
a 95% CI of [0.9757, 1.1001].

The rainfall result is sensitive to calendar adjustment.
It should not be presented as a robust independent
association across the examined specifications.

This change does not quantify the proportion explained
by time. It does not prove that rainfall has no
association or no predictive value.

The main interpretations were unchanged under
fourteen-day clustering.

## 7. Additional Diagnostic Findings

The largest screened numeric or binary VIF in
transformed M4 was 4.094. These VIF checks apply to
the specifications before calendar adjustment.

Calendar-adjusted design matrices were full rank.
This differs from rank deficiency of clustered
covariance matrices.

In transformed M4, 3,327 observations exceeded the
Cook review threshold and 5,513 exceeded the leverage
review threshold. These are screening flags, not
evidence of incorrect records. All orders were retained.

Several state estimates depend on only one or two
late orders. Their intervals can be very wide.

For example, RR versus SP had an OR of 3.4091 with
a clustered interval of [0.2726, 42.6371] in
calendar-adjusted M4.

Such results should not be used to rank states
confidently. Cluster adjustment does not resolve
sparse outcome groups.

Transformed M4 still showed residual structure
by rainfall before calendar adjustment.
The transformed specification was not treated as
a complete solution to model misspecification.

## 8. Relationship to Stage 3

Stage 3 compares delivery outcomes across individual
variables or groups. Stage 4 estimates conditional
associations after simultaneous adjustment.

The stages also use different analysis samples:
Stage 4 uses manifest training orders and complete
cases for the main predictors.

A Stage 3 difference and an attenuated Stage 4
association can therefore coexist.
This is not, by itself, evidence of an error in
either analysis.

The rainfall findings particularly require this
distinction. Group differences should not be
interpreted as causal effects or as proof of
predictive usefulness.

## 9. Review Notes and Limitations

Review should consider:

- The explicit calendar-adjustment extension.
- Missing-data and label-availability selection.
- Conditional purchase-time availability assumptions.
- State-level weather measurement and coverage.
- Remaining model misspecification.
- Sparse state outcomes and influential observations.
- Dependence across temporal blocks.
- Limited cluster counts and covariance rank.
- Exploratory specification changes and pointwise inference.

Predictive value requires separate Stage 5 evaluation.
These regression results alone do not show whether
weather or holidays improve future-order predictions.

## 10. Deliverables

- `notebooks/04_explanatory_regression/explain_late_delivery_logistic.ipynb`
- `requirements.txt`
- `outputs/tables/explanatory_regression/sample_summary.csv`
- `outputs/tables/explanatory_regression/adjusted_odds_ratios.csv`
- `outputs/tables/explanatory_regression/diagnostics.csv`
- `outputs/figures/regression/adjusted_or_key_contrasts.png`
- `outputs/figures/regression/functional_form_residual_comparison.png`

The OR table contains 316 contrasts across four
reporting specifications and two clustering definitions.
Calendar coefficients are nuisance adjustment terms
and are excluded from that table.

The sample, methods and results support report
Section 4.4.1. Interpretation, sensitivity and
limitations support Section 6.1.