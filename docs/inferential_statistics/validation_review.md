# Code and statistical validation

Validation date: 2026-11-11. Environment: Windows, Python 3.14, root `requirements.txt` installed in the existing `.venv-boosting` environment. Dependency validation: `pip check` passed. Installed direct dependency versions are recorded in `outputs/tables/validation/project_environment.json`.

## Changes

- Fixed document paths in dataset construction, Stage 3 reporting/audit and Stage 4 verification, including duplicated `docs/docs` and the moved Stage 3 notebook path.
- Report destinations create their parent directories before writing.
- Removed the obsolete report-patching cell. The generating cell now handles p-value underflow and test sidedness directly, reports computed significance counts, and does not rank effects across incompatible units.
- Replaced the requirement that all 26 tests be significant with recomputation of Holm correction, checks of rejection flags, sample accounting, confidence interval order and weather/primary-table agreement. Failed checks now raise an assertion.
- Restricted review-file discovery to `data/` rather than scanning virtual environments.
- Consolidated installation into the root `requirements.txt`. The previous boosting package snapshot is retained as reference documentation only.

## Executed checks

- All 17 notebooks passed Python syntax validation.
- Stage 3: every code cell executed in order, all 26 primary tests recomputed, all 22 final audit checks passed, no predefined report review flags.
- Stage 4: every code cell executed in order; model fitting, saved-table reloads, PNG signatures and source dataset SHA256 checks passed.
- Independently recomputed Holm adjusted p-values from the sorted step-down formula; matched saved results.
- An in-memory counterfactual with non-significant raw p-values and consistent adjusted p-values passed the data audit. A deliberately altered adjusted p-value was detected.
- Per-variable analysis sample sizes were checked against the source dataset; review and cancellation use separately constructed cohorts.
- Recomputed Stage 3 tables, Stage 4 sample summary and adjusted odds ratios reproduced repository results within numerical tolerance (`rtol=1e-7`, `atol=1e-10`).

## Results and environment sensitivity

The current data still yield 26 of 26 significant primary tests after Holm correction. This is an observed result, not a success condition in the code.

The Stage 4 diagnostics differ from the earlier environment in small floating-point quantities and these metadata/diagnostic entries:

- Two categorical input dtypes are reported as `object` rather than `str`.
- Distinct parsed destination rainfall values: 3,955 rather than 3,958.
- Numerical covariance rank for the 14-day-block M0 calendar-adjusted fit: 36 rather than 35.

These differences are retained in the newly generated diagnostics. Source dataset bytes are unchanged and the exported adjusted odds ratios reproduce the previous table within tolerance. Numerical rank is tolerance-sensitive; this check does not establish that all inferential assumptions hold.

## Scope

Statistical checks validate computation and consistency, not causality, independence or absence of selection bias. The full raw-data preprocessing chain was not rerun; the three original INMET ZIP archives are still to be supplied later. Predictive ML training and B/Test scoring were not rerun.
