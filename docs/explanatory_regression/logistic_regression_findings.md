# Adjusted delivery associations

Four focal contrasts; full transformed model with seven-day clusters. Basic model, calendar adjustment and fourteen-day clusters are supplementary. Reviews and cancellation are descriptive only. No balancing or regularization is used. All CIs are pointwise; Holm covers four focal p-values. Scope and functional forms follow prior inspection, so inference is exploratory.

| RQ | Contrast | OR | Pointwise 95% CI | Holm p |
|---|---|---:|---|---:|
| RQ1 | 200 vs 100 km | 1.1925 | [1.1008, 1.2919] | 0.000127536 |
| RQ2 | 20 vs 10 BRL | 1.0715 | [0.9701, 1.1834] | 0.170071 |
| RQ3 | Holiday vs non-holiday | 0.5928 | [0.4077, 0.8619] | 0.0138382 |
| RQ4 | 5 vs 0 mm rainfall index | 1.2895 | [1.1685, 1.4231] | 1.06011e-05 |

The common complete-case training sample has 56,553 orders, including 3,649 Late; 896 training orders are excluded for missing main predictors. Models adjust for state, items, sellers, weekday, delivery estimate, prices, products, holidays and pre-purchase rain. Selection, residual dependence and model-form assumptions limit interpretation. ORs are not risk ratios or causal effects. Rainfall attenuates after calendar adjustment; its seven-day sensitivity CI includes 1. Some clustered covariance matrices are rank deficient; no full-model joint Wald test is reported. Full control contrasts, VIF, convergence, residuals, influence and covariance diagnostics remain in supplementary outputs. Stage 3 uses a different sample and estimand; Stage 5 evaluates prediction separately.
