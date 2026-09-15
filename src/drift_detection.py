"""Détection de dérive — PSI, KS, Chi² (SQUELETTE À COMPLÉTER).

Trois méthodes complémentaires. Mini-cours : `01_PSI_KS_Chi2_essentiel.md`.
N'inventez pas vos métriques : PSI (formule ci-dessous), KS et Chi² sont dans
scipy.stats.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, ks_2samp

PSI_STABLE = 0.10
PSI_DRIFT = 0.25


def population_stability_index(reference: pd.Series, current: pd.Series, n_bins: int = 10) -> float:
    """PSI entre référence et courant.

    PSI = Σ (p_cur - p_ref) * ln(p_cur / p_ref), bornes des bins = quantiles de
    la référence. ⚠️ pensez au lissage anti-zéro (sinon ln(0) / division par 0).
    """
    eps = 1e-6
    ref = reference.dropna()
    cur = current.dropna()

    # bins issus de la RÉFÉRENCE (sinon PSI non comparable), bords extrêmes
    # ouverts pour capturer toute valeur de `cur` hors de l'étendue de `ref`.
    edges = np.unique(np.quantile(ref, np.linspace(0, 1, n_bins + 1)))
    edges[0], edges[-1] = -np.inf, np.inf

    p_ref = np.histogram(ref, edges)[0] / len(ref)
    p_cur = np.histogram(cur, edges)[0] / len(cur)

    # 1) lissage anti-zéro (sinon ln(0) / division par 0 sur un bin vide)
    p_ref, p_cur = p_ref + eps, p_cur + eps
    # 2) renormalisation : on doit comparer deux distributions qui somment à 1
    p_ref, p_cur = p_ref / p_ref.sum(), p_cur / p_cur.sum()

    return float(np.sum((p_cur - p_ref) * np.log(p_cur / p_ref)))


def psi_verdict(psi: float) -> str:
    """Traduit un PSI en verdict (stable / suspect / dérive)."""
    if psi < PSI_STABLE:
        return "stable"
    if psi > PSI_DRIFT:
        return "dérive"
    return "suspect"


def ks_pvalue(reference: pd.Series, current: pd.Series) -> float:
    """p-value du test de Kolmogorov-Smirnov (2 échantillons)."""
    return float(ks_2samp(reference.dropna(), current.dropna()).pvalue)


def chi2_pvalue(reference: pd.Series, current: pd.Series) -> float:
    """p-value du Chi² sur les fréquences de modalités (aligner les modalités)."""
    categories = sorted(set(reference.dropna().unique()) | set(current.dropna().unique()))
    ref_counts = reference.value_counts().reindex(categories, fill_value=0)
    cur_counts = current.value_counts().reindex(categories, fill_value=0)
    # lissage +1 : évite les cases à effectif nul (table de contingence non
    # exploitable par chi2_contingency sinon).
    table = np.array([ref_counts.to_numpy(), cur_counts.to_numpy()]) + 1
    return float(chi2_contingency(table)[1])


def drift_report(
    reference: pd.DataFrame, current: pd.DataFrame,
    numeric_cols: list[str], categorical_cols: list[str],
) -> pd.DataFrame:
    """Tableau de synthèse : feature / type / psi / ks_pvalue / chi2_pvalue / verdict."""
    rows = []
    for col in numeric_cols:
        psi = population_stability_index(reference[col], current[col])
        rows.append(
            {
                "feature": col,
                "type": "numérique",
                "psi": psi,
                "ks_pvalue": ks_pvalue(reference[col], current[col]),
                "chi2_pvalue": np.nan,
                "verdict": psi_verdict(psi),
            }
        )
    for col in categorical_cols:
        p = chi2_pvalue(reference[col], current[col])
        rows.append(
            {
                "feature": col,
                "type": "catégorielle",
                "psi": np.nan,
                "ks_pvalue": np.nan,
                "chi2_pvalue": p,
                "verdict": "dérive" if p < 0.05 else "stable",
            }
        )

    report = pd.DataFrame(rows)
    severity_rank = {"dérive": 2, "suspect": 1, "stable": 0}
    report["_severity"] = report["verdict"].map(severity_rank)
    report["_amplitude"] = report["psi"].fillna(1 - report["chi2_pvalue"])
    report = report.sort_values(
        ["_severity", "_amplitude"], ascending=[False, False]
    ).drop(columns=["_severity", "_amplitude"]).reset_index(drop=True)
    return report
