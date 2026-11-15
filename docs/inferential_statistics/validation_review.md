# Code and statistical validation

## Current report scope ? 2026-11-14

The final English report uses four inferential delivery questions: distance, freight, purchase holiday and destination rain. Reviews and cancellation are descriptive only. The previously fitted review regression and five-test scope below are superseded historical records, not the current reporting plan.

Both revised statistical notebooks were executed end to end. Stage 3 exports four raw tests and recomputed four-test Holm values, plus descriptive review rates/coverage without review p-values. Stage 4 exports four focal adjusted delivery contrasts with separate four-contrast Holm and calendar/14-day sensitivity. Source hashes and notebook output audits passed. No ML model, calibrator or Test score was refitted for the report.

The report contains 17 native result/design tables and nine generated figures. Google Docs table cells were checked against local source data. Question D is explicitly not completed; neither feature-group gains nor predictive timezone sensitivity are claimed. Missing annual INMET source archives remain a reproducibility limitation.

## Historical validation records


## Current Stage 3 scope ? 2026-11-14

Stage 3 now reports five research questions only:

| Current ID | Variable | Previous analysis |
|---|---|---|
| RQ1 | distance_km_mean | RQ5 |
| RQ2 | freight_value | Freight branch of RQ6 |
| RQ3 | purchase_is_national_holiday | RQ12 |
| RQ4 | destination_rain_state_mean_mm | RQ15b |
| RQ5 | low_review | RQ19 |

The scope was reduced after the earlier larger family had been analysed. The revised five-test Holm family is a reporting decision, not a retrospectively claimed prospective plan. Primary p-values are recomputed; former adjusted p-values for 26 tests are not reused.

## Code and output changes

- Removed primary testing code for state, weekday, month, interstate seller, order value, price ratios, product weight/volume, seller/category counts, estimated window, other holiday variables, other weather variables and cancellation.
- Kept dataset validation, question-specific missingness, review deduplication and review coverage by delivery label. Missing labels/reviews are not converted to negative outcomes.
- Kept a supplementary freight trimmed-mean test and 14-day rainfall block sensitivity. Neither enters the five-test primary family.
- Corrected the distance export: estimate and interval now both refer to rank-biserial correlation. Probability superiority is a distinct descriptive quantity, not the estimate paired with this interval.
- Replaced the four existing CSV summaries with five-question outputs. Added freight/weather sensitivity and review coverage tables.
- Removed obsolete Stage 3 figures and generated one figure per current research question. Rebuilt the report from the computed objects and updated the project README.
- No source data, EDA analyses, Stage 4 model specification or ML results are removed by this scope change.

## Current validation

The Stage 3 notebook was executed from the first cell through the final audit using the existing `.venv-boosting` environment. Checks cover:

- Exactly five unique primary results, matching the declared RQ-variable pairs in order.
- Per-question sample accounting: initial = excluded + retained, and descriptive cohorts match result-table sizes.
- Raw and Holm p-values in [0, 1], finite estimates and interval endpoints, ordered confidence bounds.
- Independent Holm recomputation using the sorted step-down formula, plus agreement of rejection flags. Significance is not a pass condition.
- Only destination rainfall in the primary and sensitivity weather tables.
- Exactly one valid selected review per order; valid binary low-review outcomes and no missing scores in the analysis cohort.
- Reloaded CSV row counts and PNG file signatures for all five figures.
- SHA256 agreement before and after execution for the main research CSV and cleaned reviews CSV.

All current checks passed. The five primary Holm-adjusted p-values are below 0.05 in this run; that is an observed result, not a required outcome. RQ5's numerical zero p-value is explicitly marked as floating-point underflow, not an exact probability of zero. All reported 95% confidence intervals are pointwise and are not corrected for multiple testing.

## Interpretation and remaining limitations

Mann?Whitney tests distributions and is not automatically a median test. Welch allows unequal variances but does not solve dependence between orders. Distance confidence intervals use order-level stratified bootstrap and do not account for seller/time clustering. Binary tests can also be affected by dependent observations.

Rainfall inference resamples whole 7-day calendar blocks across locations, retaining shared observations within each block. The two-sided test uses a null-centered bootstrap-error approximation with finite-simulation correction; 14-day blocks provide sensitivity analysis. Block independence and residual spatial/seller dependence remain assumptions. Rainfall is the pre-purchase feature under the project's UTC scenario, not weather observed throughout delivery; point-in-time source availability remains unverified.

Review analysis uses the latest valid creation date, then answer timestamp and review ID. The EDA first-review rule differs, so percentages can differ. Review missingness can cause selection bias. Reviews are retrospective outcomes and must not enter purchase-time prediction.

Stage 3 uses the full labeled descriptive cohort. Stage 4 uses its own training/complete-case cohort and estimates adjusted associations. Stage 3 findings are not independent validation of ML performance and do not establish causation.

## Previous project validation ? 2026-11-11

The earlier run validated notebook syntax, dependencies and Stage 4 execution, including exported-table reloads and source hashes. These are historical checks; Stage 4 has now been rerun as documented below; ML training/calibration/test scoring were not rerun. The former 26-test Stage 3 report is superseded by the current outputs.

The complete raw-data preprocessing chain was not rerun. The original INMET ZIP archives remain deferred; this run uses existing processed inputs. No fresh-environment installation was performed.

## Stage 4 revision and execution ? 2026-11-14

- Renamed the existing fitted delivery specifications to descriptive model names. Retained all delivery controls and supplementary diagnostics; the four delivery focal factors correspond to RQ1?RQ4.
- Executed the full revised Stage 4 notebook successfully, including the retrospective low-review regression for RQ5. Existing delivery contrast estimates reproduce the previous committed CSV within tolerance (`rtol=1e-7`, `atol=1e-10`).
- The main reporting family uses the full transformed delivery model and review model with seven-day clusters. Calendar-adjusted and fourteen-day variants are supplementary; model selection is not based on significance. Five primary Stage 4 p-values receive their own Holm correction, independently checked with the step-down formula.
- Review regression uses 56,123 complete-case training orders with selected valid reviews, including 7,319 low-review events. The review rule matches Stage 3. Coverage and exclusions are exported by delivery label.
- The first review fit exposed instability in a rare state coefficient. Review-state levels with fewer than 100 retained orders were pooled by cohort size, then refitted. This exploratory stabilisation is documented; delivery models are unchanged. All four final review fits converged without warnings. Some cluster covariance matrices are rank deficient; focal contrast variances are finite and positive, and no full-model joint Wald claim is made.
- Checked review design ranks, fitted probabilities, seven/fourteen-day inference degrees of freedom, coefficient agreement between conventional and robust fits, independent Holm, CSV numerical reloads and PNG signatures. The cleaned review input hash was unchanged; the existing delivery-data SHA256 check also passed.
- Main Stage 4 Holm results: RQ1, RQ3, RQ4 and RQ5 reject their contrast nulls; RQ2 does not. Calendar-adjusted rainfall has a pointwise CI including 1, so its association is sensitive to temporal adjustment. These are observed results, not pass conditions.
- Rebuilt the Stage 4 findings directly from fitted results and separated primary from supplementary tables. All notebook schemas and Python cells were checked after the revision. ML results on the summary slide are existing saved baseline results, not new fits.
