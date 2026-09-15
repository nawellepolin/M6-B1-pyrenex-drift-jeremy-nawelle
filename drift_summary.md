# Synthèse de dérive — `reference_set.csv` vs `prod_3months.csv`

Repères PSI : < 0.10 signal faible · 0.10-0.25 à investiguer · > 0.25 signal fort.

| Feature | Type | PSI | p-value (KS/Chi²) | Verdict | Interprétation |
|---|---|---:|---:|---|---|
| `grade` | catégorielle | — | 3.7e-07 | dérive | Chi² très significatif (p = 3,7e-7) : la redistribution vers des notes plus risquées (moins de A/B, plus de D/E/F) vue à l'œil en section 1 est confirmée statistiquement. |
| `int_rate` | numérique | 0.444 | 4.6e-65 | dérive | PSI 0,44 très au-dessus du seuil de dérive forte (0,25), KS quasi nul (4,6e-65) : signal net et concordant sur les deux méthodes. Cohérent avec la redistribution de `grade` (le taux dépend de la note) — probablement le même phénomène de fond, pas deux dérives indépendantes. |
| `revol_util` | numérique | 0.187 | 3.8e-20 | suspect | PSI 0,19, dans la zone à investiguer (0,10-0,25), pas encore une dérive forte. KS très significatif (3,8e-20) : l'écart est réel mais d'ampleur modérée. À surveiller, sans alerte immédiate. |
| `purpose` | catégorielle | — | 0.2 | stable | Chi² non significatif (p = 0,20) : répartition des motifs stable. |
| `term` | catégorielle | — | 0.32 | stable | Chi² non significatif (p = 0,32) : répartition des durées stable. |
| `emp_length` | catégorielle | — | 0.49 | stable | Chi² non significatif (p = 0,49) : répartition stable. |
| `verification_status` | catégorielle | — | 0.59 | stable | Chi² non significatif (p = 0,59) : répartition stable. |
| `home_ownership` | catégorielle | — | 0.63 | stable | Chi² non significatif (p = 0,63) : répartition stable. |
| `annual_inc` | numérique | 0.067 | 2.3e-09 | stable | PSI 0,067 (stable) mais KS très significatif (2,3e-9) : cas d'école du mini-cours — sur 1500 vs 3000 lignes, KS détecte un écart réel mais de faible ampleur. On retient le PSI pour juger l'importance : verdict stable, la baisse de revenu moyen ne suffit pas à elle seule à justifier une alerte. |
| `installment` | numérique | 0.015 | 0.66 | stable | PSI et KS tous deux non significatifs : aucun signal. |
| `dti` | numérique | 0.011 | 0.11 | stable | PSI et KS tous deux non significatifs : aucun signal. |
| `fico_range_low` | numérique | 0.007 | 0.49 | stable | PSI et KS tous deux non significatifs : aucun signal. |
| `loan_amnt` | numérique | 0.003 | 0.99 | stable | PSI et KS tous deux non significatifs : aucun signal. |
| `delinq_2yrs` | numérique | 0.002 | 0.89 | stable | PSI et KS tous deux non significatifs : aucun signal. |
