# Note de recommandation — Dérive `pyrenex_risk_v2`

**Pour :** Sophie Léger (Lead Data, Pyrenex)
**De :** FastIA — Jeremy & Nawelle

## Constat (chiffré)

Trois mois après la mise en production, le F1 macro recule de **0,608 à 0,551**
(-9 %) entre les 4 premières et les 4 dernières semaines — c'est ce qui a
déclenché vos alertes. Deux features d'entrée ont significativement dérivé :
le taux d'intérêt des dossiers (`int_rate`, PSI 0,44, très au-dessus du seuil
de dérive forte de 0,25) et la note de risque (`grade`, test statistique
p = 3,7×10⁻⁷). Une troisième, le taux d'utilisation de crédit renouvelable
(`revol_util`), est en zone à surveiller (PSI 0,19).

## Diagnostic

**Dérive des données d'entrée (« data drift »), pas de la logique du modèle.**
Le mix de dossiers reçus a changé — plus de taux élevés, plus de notes de
risque dégradées — cohérent avec un afflux de profils plus risqués. Mais le
modèle continue de **classer aussi bien** les bons et mauvais payeurs :
l'AUC est quasi identique sur la période (0,742 → 0,746, écart de 0,004,
largement dans la marge de bruit normale). Ce qui se dégrade, c'est la
fiabilité des probabilités annoncées : l'écart entre le risque annoncé et le
risque réellement observé (ECE) est passé de 0,24 à 0,32, et ce de façon
progressive semaine après semaine — pas un décrochage brutal qui évoquerait
un bug technique.

Un changement de la logique de risque du modèle (« concept drift ») est peu
probable : il serait cohérent avec une AUC qui se dégrade, ce qui n'est pas
le cas ici. Il serait à réexaminer si l'AUC se mettait à décrocher.

## Recommandation

**Recalibrer les probabilités du modèle sur les 4 dernières semaines de
données, sous 2 semaines.** Concrètement : ajuster la conversion
score → probabilité (régression logistique ou isotonique sur les dossiers
récents dont l'issue est connue), sans toucher au modèle lui-même ni à son
entraînement.

**Alternative écartée : un réentraînement complet.** C'est la réponse par
défaut à un data drift, mais elle n'est pas justifiée ici : l'AUC stable
(écart de 0,004, sous le bruit de mesure) montre que le pouvoir de tri du
modèle est intact — un réentraînement referait tout le pipeline (features,
hyperparamètres, validation) pour ne corriger, au fond, que le même problème
de calibration qu'un recalibrage cible directement, à un dixième du coût.

## Coût estimé

- **Recalibrage (retenu)** : ~2 jours-homme (extraction des dossiers
  récents avec issue connue, ajustement de la fonction de correction,
  validation croisée, déploiement). Risque prod faible — le modèle et son
  seuil de décision ne changent pas, seule la probabilité affichée est
  corrigée.
- **Réentraînement complet (écarté)** : ~8 jours-homme (pipeline de données,
  ré-entraînement, revalidation complète, déploiement) pour un gain attendu
  nul sur le pouvoir de tri, déjà intact.
- **Fenêtre d'intervention** : sous 2 semaines. La dégradation est
  progressive (pas de rupture), mais elle continue de monter — chaque
  semaine d'attente ajoute du décalage entre probabilité affichée et risque
  réel.

## Décision suggérée

> Lancer le recalibrage des probabilités sur les données des 4 dernières
> semaines, sous 2 semaines, sans réentraîner le modèle ; revoir l'AUC et
> `revol_util` au prochain point de suivi pour confirmer qu'aucun signal de
> concept drift n'apparaît entre-temps.

---

*Note produite par le binôme Jeremy & Nawelle, dans le cadre du brief M6-B1
Pyrenex Crédit. Détail des calculs : `diagnostic.md`, `drift_summary.md`,
`notebooks/M6-B1_binome_drift_analysis.ipynb`.*
