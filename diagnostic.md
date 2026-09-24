# Diagnostic de dérive — pyrenex_risk_v2

> Pour Sophie Léger et l'équipe SRE. Analyse sur 3 mois de production
> (`prod_3months.csv`, `predictions_log.csv`) vs le témoin de référence
> (`reference_set.csv`, 1500 lignes).

## Constat de départ

Le script d'évaluation continue (M5-B2) alerte depuis ~2 semaines : le F1
macro et le recall défaut reculent. Le calcul brut : F1 macro 0,6085 (semaines
1-4) → 0,5506 (semaines 9-12), soit -0,058. La question posée par Sophie
Léger : les données entrantes ont-elles changé, la relation features→défaut
a-t-elle évolué, est-ce saisonnier, ou un bug ETL ?

## Triangulation des 4 axes

| Axe | Constat | Preuve chiffrée |
|---|---|---|
| **Features** | Dérive confirmée sur 2 features, 1 en zone grise | `int_rate` : PSI 0,44, KS p=4,6e-65 · `grade` : Chi² p=3,7e-7 · `revol_util` : PSI 0,19 (à investiguer) |
| **AUC** (pouvoir de tri) | **Stable** | 0,7419 (S1-4) → 0,7459 (S9-12), Δ=+0,004 — très en dessous du repère de 0,03 |
| **Calibration** | Dégradée, et de façon progressive | ECE 0,24 (S1-4) → 0,32 (S9-12) ; montée quasi continue semaine par semaine (0,243 → 0,239 → 0,286 → 0,311 → 0,322 → 0,311) |
| **Temporalité** | Progressive, pas un saut brutal | Voir la courbe ECE ci-dessus — aucune rupture nette entre deux semaines consécutives |

## Verdict

**Data drift, avec impact sur la calibration.** Le mix de dossiers entrants a
changé — plus de taux d'intérêt élevés, plus de notes de risque dégradées
(D/E/F plutôt que A/B) — cohérent avec un afflux de profils plus risqués.
Mais le modèle **continue à bien ordonner** les bons et mauvais payeurs
(AUC quasi inchangée) : sa logique de risque reste valide sur cette nouvelle
population. La baisse de F1 macro qui a déclenché les alertes s'explique par
un effet de seuil et de calibration sur une population qui a bougé — pas par
une perte de pouvoir discriminant du modèle.

Ce diagnostic correspond exactement au cas de référence du mini-cours 02 :
*« features qui dérivent + AUC stable → data drift plausible »*.

### Hypothèses écartées

- **Concept drift** (la relation features→défaut aurait changé) : peu
  probable. Une AUC stable est incompatible avec cette hypothèse comme cause
  principale du problème — sans l'exclure formellement à 100 %.
- **Bug ETL pur** : peu probable. Une casse technique produit typiquement un
  saut brutal sur une courte fenêtre ; ici la dérive est progressive sur les
  12 semaines. `revol_util` reste néanmoins à surveiller (zone grise, PSI
  0,19) — son taux de manquants, lui, est stable entre référence et prod
  (1,33 % vs 1,2 %) et n'est donc pas un signal ETL en soi.
- **Effet saisonnier pur** : possible en partie sur une fenêtre de 3 mois,
  mais n'explique pas à lui seul une dégradation aussi régulière plutôt que
  cyclique.

### Ce qui manquerait pour trancher avec certitude

- Une fenêtre d'observation plus longue (au-delà de 3 mois) pour écarter
  définitivement un artefact saisonnier.
- Une confirmation métier côté Pyrenex : un changement de canal d'apport ou
  de critères d'octroi en amont expliquerait directement le mix de dossiers
  observé.
- Une vérification technique du pipeline ETL sur `revol_util`, dont la
  moyenne progresse (50,6 → 59,0) même si le taux de manquants reste stable —
  à surveiller sur les prochaines semaines pour voir si le signal se
  renforce.

## Méthode

Calculs reproductibles dans `notebooks/M6-B1_binome_drift_analysis.ipynb` (sections 2 à
5), fonctions dans `src/drift_detection.py`, `src/calibration.py`,
`src/recommendations.py`. Détail feature par feature : `drift_summary.md`.

---

*Diagnostic produit par le binôme Jeremy & Nawelle, dans le cadre du brief
M6-B1 Pyrenex Crédit.*
