"""Logique de recommandation de remédiation (SQUELETTE À COMPLÉTER).

La remédiation doit être **proportionnée** au diagnostic : réentraîner coûte
cher, on ne le propose que quand ça vaut le coup. Mini-cours :
`02_Data_drift_vs_concept_drift_essentiel.md` (matrice features × AUC).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DriftDiagnosis:
    """Synthèse du diagnostic pour décider de la remédiation."""

    n_features_drift: int  # nb de features en "dérive" (PSI > 0.25)
    auc_stable: bool  # le pouvoir discriminant tient-il ?
    calibration_degraded: bool  # la confiance a-t-elle dérivé ?
    f1_drop: float  # baisse de F1 macro (early → late)


def diagnose_drift_type(d: DriftDiagnosis) -> str:
    """Oriente vers "data drift" / "concept drift" / "mixte".

    ⚠️ Heuristique d'orientation, pas une preuve : elle formalise la matrice
    du mini-cours 02 (features × AUC) pour produire une hypothèse principale.
    Le verdict final se construit en croisant features, AUC, calibration et
    temporalité — et doit énoncer ce qui manquerait pour trancher.
    """
    features_drift = d.n_features_drift > 0

    if features_drift and d.auc_stable:
        # Les entrées ont bougé, mais le modèle ordonne toujours aussi bien
        # les bons et mauvais payeurs : la logique de risque tient.
        return "data drift"
    if not features_drift and not d.auc_stable:
        # Rien ne bouge côté features, pourtant le pouvoir de tri se
        # dégrade : signal fort d'un changement de la relation X → Y.
        return "concept drift"
    return "mixte"


def recommend(d: DriftDiagnosis) -> dict[str, str]:
    """Recommande une action proportionnée au diagnostic.

    Returns:
        dict avec les clés : action / justification / urgence / drift_type.
    """
    drift_type = diagnose_drift_type(d)

    if drift_type == "data drift":
        if d.calibration_degraded:
            return {
                "drift_type": drift_type,
                "action": "Recalibrer les probabilités sur un échantillon récent (sans réentraîner le modèle)",
                "urgence": "modérée",
                "justification": (
                    f"{d.n_features_drift} feature(s) en dérive confirmée et AUC stable "
                    "(pouvoir de tri intact) : le modèle discrimine toujours aussi bien "
                    "sur ce nouveau mix de dossiers, mais ses probabilités sont de moins "
                    "en moins fiables (calibration dégradée). Recalibrer coûte bien moins "
                    "cher qu'un réentraînement complet et cible directement le symptôme observé."
                ),
            }
        return {
            "drift_type": drift_type,
            "action": "Surveiller — aucune action corrective immédiate",
            "urgence": "faible",
            "justification": (
                f"{d.n_features_drift} feature(s) en dérive mais AUC stable et calibration "
                "intacte : le modèle reste fiable sur la population actuelle. Un "
                "réentraînement ne se justifie pas tant qu'aucun symptôme de performance "
                "n'apparaît."
            ),
        }

    if drift_type == "concept drift":
        return {
            "drift_type": drift_type,
            "action": "Réentraîner en urgence et investiguer la cause du changement de relation X → Y",
            "urgence": "haute",
            "justification": (
                "Les features sont stables mais l'AUC se dégrade : le lien entre les "
                "caractéristiques des dossiers et le risque réel de défaut a changé. "
                "Recalibrer ne suffirait pas — le modèle apprend une relation qui n'est "
                "plus vraie."
            ),
        }

    # mixte : features en dérive ET AUC qui se dégrade
    return {
        "drift_type": drift_type,
        "action": "Réentraîner sur données récentes et investiguer si un concept drift s'ajoute au data drift",
        "urgence": "haute",
        "justification": (
            f"{d.n_features_drift} feature(s) en dérive ET AUC en baisse (Δ F1 macro "
            f"{d.f1_drop:.2f}) : la dérive des entrées s'accompagne d'une vraie perte de "
            "pouvoir discriminant, pas seulement d'un effet de calibration. Un simple "
            "recalage ne suffira probablement pas."
        ),
    }
