<!-- =============================================================================
  TASK.md — Consignes pour le Challenge 5 (le plus difficile)
============================================================================= -->

# Challenge 5: Module de Qualité de Données

<!-- POURQUOI C'EST IMPORTANT :
     "Garbage In, Garbage Out" — si les données en entrée sont pourries,
     les résultats du pipeline seront pourris aussi.

     Actuellement, le pipeline traite TOUT sans vérifier la qualité.
     Si un fichier source contient 90% de valeurs nulles, le pipeline
     va quand même générer un rapport basé sur 10% des données — trompeur.

     UN MODULE DE DATA QUALITY permet de :
     1. PROFILER : comprendre à quoi ressemblent les données (stats, distributions)
     2. DÉTECTER : repérer les anomalies et problèmes automatiquement
     3. BLOQUER : empêcher le pipeline de tourner si la qualité est trop basse

     C'EST LE CHALLENGE LE PLUS DUR car l'agent doit créer un module
     entier from scratch, pas juste modifier du code existant. -->

## Objectif
Implémenter un module complet de qualité de données qui s'intègre au pipeline existant.

## Fonctionnalités requises

### 1. Profiling automatique
<!-- LE PROFILING = regarder chaque colonne du dataset et calculer des stats.
     C'est comme un "bilan de santé" des données.
     Exemples concrets avec notre fichier sample_data.csv :
       - colonne "value" : 2 nulls sur 10 = 20% de nulls
       - colonne "value" : min=12.9, max=445.0, moyenne=118.3
       - colonne "category" : 3 valeurs uniques (A, B, C)
       - colonne "region" : top valeurs = EU(4), US(4), APAC(2) -->
Pour chaque colonne/champ du dataset, calculer :
- Nombre et pourcentage de valeurs nulles
- Nombre de valeurs uniques (cardinality)
- Distribution des valeurs (min, max, mean, median, stddev pour les numériques)
- Top 10 des valeurs les plus fréquentes
- Détection de type (numérique, string, date, booléen)
- Détection d'anomalies (valeurs hors 3 écarts-types)

### 2. Rapport JSON
<!-- Le rapport est un fichier JSON structuré qui résume tout le profiling.
     Il doit être lisible par un humain ET parseable par un programme.
     Le "score de qualité" (0-100) donne une idée rapide : 95 = très bon, 40 = problème. -->
Générer un rapport structuré au format JSON contenant :
- Métadonnées (timestamp, nombre de records, source)
- Profiling par colonne
- Liste des anomalies détectées
- Score de qualité global (0-100)

### 3. Seuils configurables (Quality Gates)
<!-- UN QUALITY GATE = un seuil qui bloque le pipeline si dépassé.
     C'est comme un garde-fou : si les données sont trop mauvaises,
     mieux vaut NE PAS traiter que de produire des résultats faux.

     Exemples :
     - max_null_percentage: 10% → si une colonne a >10% de nulls, on bloque
     - min_completeness: 90% → si <90% des champs sont remplis, on bloque
     - max_duplicate_percentage: 5% → si >5% de doublons, on bloque

     Les seuils sont dans un fichier de config (pas dans le code)
     pour que l'équipe data puisse les ajuster sans toucher au code. -->
- Fichier de configuration YAML ou JSON définissant les seuils
- Exemples de seuils :
  - `max_null_percentage`: pourcentage max de nulls par colonne (défaut: 10%)
  - `min_completeness`: complétude minimale du dataset (défaut: 90%)
  - `max_duplicate_percentage`: pourcentage max de doublons (défaut: 5%)
  - `anomaly_threshold`: seuil de détection d'anomalies en écarts-types (défaut: 3)
- Si un seuil est dépassé, le pipeline est **bloqué** avec un message d'erreur clair

## Architecture cible
<!-- 4 fichiers à créer + 1 fichier de config :
     profiler.py     = les calculs statistiques (le coeur mathématique)
     report.py       = mise en forme du profiling en JSON structuré
     quality_gate.py = comparaison profiling vs seuils → pass/fail
     config.py       = lecture du fichier de config des seuils
     quality_thresholds.json = le fichier de config avec les seuils -->
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
<!-- Ces critères correspondent aux checks de validate_challenge5.py -->
1. Le module `src/data_quality/` existe avec les 4 fichiers
2. Le profiler calcule au minimum : nulls, cardinality, distribution stats
3. Le rapport JSON est généré avec la structure attendue
4. Les quality gates bloquent le pipeline si les seuils sont dépassés
5. La configuration des seuils est externalisée (pas hardcodée)
6. Le module peut être appelé standalone ou intégré au pipeline
7. Tout le code est syntaxiquement valide
