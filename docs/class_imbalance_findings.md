# Class Imbalance Findings (ENG) (Stage 2 · TASK 03)

**Owner:** Phong · **Source:** `data/processed/research_data.csv` (99,441 rows, 34 columns; 1 row = 1 order) · **Notebook:** `notebooks/05_class_imbalance_analysis.ipynb` · Figure: `imb01_class_distribution.png`

> Figures are computed from `research_data.csv`; charts are generated when the notebook is run (saved in `outputs/figures/`, tables in `outputs/tables/`).
> Related TASK 02 report: `eda_findings.md` (monthly prevalence in EDA03).

## 0. Sample scope

| Item | Orders | % of total |
|---|---:|---:|
| All orders | 99,441 | 100.00 |
| **Orders with a valid `is_late` label (analysis sample)** | **96,470** | 97.01 |
| – Late (`is_late = 1`) | 6,534 | 6.57 |
| – Not Late (`is_late = 0`) | 89,936 | 90.44 |
| Orders without a label (excluded; not treated as "not late") | 2,971 | 2.99 |


## 1. Class distribution

| Class | Orders | % (of 96,470 labelled orders) |
|---|---:|---:|
| Not Late (0) – majority | 89,936 | 93.23 |
| Late (1) – minority | 6,534 | 6.77 |

- **Imbalance ratio = 89,936 / 6,534 ≈ 13.76 : 1** (minority / majority ≈ 0.0727).
- Prevalence of Late π = 6.77%. No severity label (mild/moderate/severe) is assigned because no criterion or convention is cited; the ratio is reported directly.
- Prevalence is **not stable over time** (from ~1.2% in 2018-06 to ~19.0% in 2018-03, see EDA03).

## 2. Accuracy paradox (from class counts, no model trained)

Constant classifier "always predict Not Late": TN = 89,936, FN = 6,534, TP = FP = 0.

| Metric | Value |
|---|---:|
| Accuracy | **93.23%** |
| Recall (Late) | 0% |
| Precision (Late) | undefined (0/0) |
| F1 (Late) | 0 |
| ROC-AUC (no discrimination) | 0.5 |
| Average Precision (constant scorer) | π ≈ 0.068 (prevalence of the set under evaluation) |

**Illustration of Precision under different TPR/FPR scenarios** (pure formula `Precision = TPR·π / (TPR·π + FPR·(1−π))`; both TPR and FPR change between rows; **not model results**). The accompanying chart (`imb02_illustrative_precision.png`) is titled *Illustrative Precision at Assumed Recall and FPR Levels* – a mathematical illustration, not an empirical PR curve; ROC and PR are not drawn on a shared axis:

| Recall | FPR | Accuracy | Precision (Late) | F1 (Late) |
|---:|---:|---:|---:|---:|
| 0.50 | 0.10 | 87.3% | 26.6% | 0.348 |
| 0.70 | 0.20 | 79.3% | 20.3% | 0.314 |
| 0.80 | 0.20 | 80.0% | 22.5% | 0.351 |
| 0.90 | 0.30 | 71.4% | 17.9% | 0.299 |

→ A classifier that catches 80% of late orders still has lower Accuracy than the constant classifier (80% < 93.2%) and Precision of only ~22%: Accuracy does not reflect quality, and Precision is pulled down strongly by the low prevalence.

## 3. Effect on metrics & recommendation

| Metric | Effect when Late ≈ 6.8% | Role |
|---|---|---|
| Accuracy | Dominated by the majority class; 93.23% majority-class baseline | Reference only, not the main metric |
| Precision (Late) | Share of correct alerts among flagged orders; sensitive to low prevalence. Converting to cost needs business assumptions | Shows how many alerts are right vs wrong |
| Recall (Late) | Not inflated by the majority class | Measures missed late orders – goal of early prediction |
| F1 (Late) | Balances Precision/Recall of Late; = 0 for the constant classifier | Summary at one threshold |
| **ROC-AUC** | Ranking quality over all thresholds; a high ROC-AUC can still come with low Precision and many false alerts, so AP should also be reported | **Recommended** – compare models |
| **Average Precision (AP)** | Focuses on Late; reference level = prevalence of the evaluation set; AP is not the same as the trapezoidal area under the PR curve | **Recommended** – main metric for Late, with the Precision–Recall curve |

**Baseline AP:** the AP of a *constant* scorer equals the prevalence; a single random ranking does not necessarily give an AP exactly equal to it. The baseline must follow the Late share of the **evaluation set itself** (≈ 0.068 is true only for the full labelled sample, not a fixed value for every set). The ROC-AUC reference is 0.5.

**Recommendation:** main metric **Average Precision (AP)** (plus ROC-AUC); report Precision / Recall / F1 of the Late class at a threshold chosen on validation according to the objective and cost, together with the confusion matrix.

**Limitations of Accuracy as the main metric:** (1) dominated by the majority class; (2) does not distinguish the two error types, and the cost of each needs business assumptions; (3) depends on the threshold – choose it on validation instead of by default; (4) the 93.23% majority-class baseline makes improvements look tiny; (5) prevalence changes over time, so Accuracy is not directly comparable across periods.

**Evaluation design (provisional, to be finalised during ML design):** since the goal is to predict future orders, the provisional design is a time-based split (train → validation → test); thresholds chosen on validation; the test set is not rebalanced.

*Not done in this task:* SMOTE, resampling, class weighting, model training.

---

## Data limitations & caveats
1. The sample contains only **delivered** orders with valid dates → possible selection (survivorship) bias, especially in the last months.
2. Prevalence is computed over the pooled 2016–2018 sample; it varies strongly by month (see EDA03 in the TASK 02 report), so the single 13.76 : 1 ratio does not describe every period.
3. The scenario table and chart in section 2 are mathematical illustrations under assumed Recall/FPR, not model results.
