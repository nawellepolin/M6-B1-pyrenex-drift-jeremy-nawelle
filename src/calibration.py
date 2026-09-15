"""Calibration en exploitation (SQUELETTE À COMPLÉTER).

Le modèle annonce une proba : observe-t-on le bon taux réel ?
Mini-cours : `03_Calibration_modele_essentiel.md`. ⚠️ Calibration =
**exploitation** (≠ seuils de rejet de conception, vus en M7-M8).
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def reliability_table(proba: pd.Series, true_label: pd.Series, n_bins: int = 10) -> pd.DataFrame:
    """Table du reliability diagram : bin / n / confiance_moyenne / taux_observe / ecart."""
    df = pd.DataFrame({"proba": np.asarray(proba), "true_label": np.asarray(true_label)})
    df["bin"] = pd.cut(df["proba"], np.linspace(0, 1, n_bins + 1), include_lowest=True)

    table = df.groupby("bin", observed=True).agg(
        n=("true_label", "size"),
        confiance_moyenne=("proba", "mean"),
        taux_observe=("true_label", "mean"),
    )
    table["ecart"] = table["confiance_moyenne"] - table["taux_observe"]
    return table.reset_index()


def expected_calibration_error(proba: pd.Series, true_label: pd.Series, n_bins: int = 10) -> float:
    """ECE = Σ (n_bin/N) * |confiance - taux observé|. 0 = parfaitement calibré."""
    table = reliability_table(proba, true_label, n_bins=n_bins)
    weights = table["n"] / table["n"].sum()
    return float((weights * table["ecart"].abs()).sum())
