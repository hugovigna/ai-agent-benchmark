# Challenge 5: Module de Qualité de Données

## Objectif
Implémenter un module complet de qualité de données qui s'intègre au pipeline existant.

## Fonctionnalités requises

### 1. Profiling automatique
Pour chaque colonne/champ du dataset, calculer :
- Nombre et pourcentage de valeurs nulles
- Nombre de valeurs uniques (cardinality)
- Distribution des valeurs (min, max, mean, median, stddev pour les numériques)
- Top 10 des valeurs les plus fréquentes
- Détection de type (numérique, string, date, booléen)
- Détection d'anomalies (valeurs hors 3 écarts-types)

### 2. Rapport JSON
Générer un rapport structuré au format JSON contenant :
- Métadonnées (timestamp, nombre de records, source)
- Profiling par colonne
- Liste des anomalies détectées
- Score de qualité global (0-100)

### 3. Seuils configurables (Quality Gates)
- Fichier de configuration YAML ou JSON définissant les seuils
- Exemples de seuils :
  - `max_null_percentage`: pourcentage max de nulls par colonne (défaut: 10%)
  - `min_completeness`: complétude minimale du dataset (défaut: 90%)
  - `max_duplicate_percentage`: pourcentage max de doublons (défaut: 5%)
  - `anomaly_threshold`: seuil de détection d'anomalies en écarts-types (défaut: 3)
- Si un seuil est dépassé, le pipeline est **bloqué** avec un message d'erreur clair

## Architecture cible
```
src/
  data_quality/
    __init__.py
    profiler.py          # Profiling automatique des données
    report.py            # Génération du rapport JSON
    quality_gate.py      # Vérification des seuils
    config.py            # Chargement de la configuration
config/
  quality_thresholds.json  # Configuration des seuils
```

## Critères de validation
1. Le module `src/data_quality/` existe avec les 4 fichiers
2. Le profiler calcule au minimum : nulls, cardinality, distribution stats
3. Le rapport JSON est généré avec la structure attendue
4. Les quality gates bloquent le pipeline si les seuils sont dépassés
5. La configuration des seuils est externalisée (pas hardcodée)
6. Le module peut être appelé standalone ou intégré au pipeline
7. Tout le code est syntaxiquement valide
