# AI Agent Benchmark — Data Engineering Challenges

<!--
  BUT DU REPO :
  Ce repo sert de "banc d'essai" (benchmark) pour mesurer la performance
  d'un agent IA (ex: Claude Code, Copilot, Cursor...) sur des tâches
  réalistes de data engineering.

  PRINCIPE :
  - La branche `main` contient le code de base (un projet de pipeline de données)
  - Chaque challenge vit dans sa propre branche Git
  - Chaque branche contient un TASK.md (les consignes pour l'agent)
  - Les scripts validate_challengeN.py vivent dans main (pas dans les branches challenge)
  - On demande à l'agent IA de résoudre le challenge, puis on lance le validateur depuis main

  STRUCTURE DU REPO (branche main) :
  ├── config/settings.py        <- Configuration du pipeline (sera modifié par le challenge 1)
  ├── src/
  │   ├── db_connector.py       <- Connexion PostgreSQL (credentials hardcodées = challenge 2)
  │   ├── api_client.py         <- Client API externe (credentials hardcodées = challenge 2)
  │   ├── cloud_storage.py      <- Upload/download S3 (credentials hardcodées = challenge 2)
  │   ├── notification.py       <- Alertes Slack/email (credentials hardcodées = challenge 2)
  │   ├── pipeline.py           <- Pipeline monolithique 271 lignes (= challenge 3)
  │   └── long_pipeline.py      <- Pipeline 10 étapes sans checkpoint (= challenge 4)
  ├── data/raw/                 <- Données d'exemple CSV + JSON (utilisées par les pipelines)
  ├── run_benchmark.sh          <- Script pour lancer les challenges automatiquement
  └── requirements.txt          <- Dépendances Python du projet
-->

Ce repo contient **8 challenges** pour évaluer la capacité d'un agent IA à résoudre des problèmes courants en data engineering.

## Challenges

<!--
  TABLEAU RÉCAPITULATIF :
  Chaque ligne = 1 challenge isolé sur sa propre branche Git.
  La difficulté monte progressivement :
  - ⭐     = tâche simple (résolution de conflit)
  - ⭐⭐⭐⭐ = tâche complexe (créer un module entier from scratch)
-->

| # | Challenge | Branche / Fichiers | Difficulté |
|---|-----------|-------------------|------------|
| 1 | **Merge Conflict** | `feature/update-config` vs `feature/refactor-config` | ⭐ |
| 2 | **Credentials Hardcodées** | `challenge/hardcoded-creds` | ⭐⭐ |
| 3 | **Refactoring Pipeline Monolithique** | `challenge/monolith-pipeline` | ⭐⭐⭐ |
| 4 | **Checkpointing Pipeline** | `challenge/add-checkpointing` | ⭐⭐⭐ |
| 5 | **Module Qualité de Données** | `challenge/data-quality` | ⭐⭐⭐⭐ |
| 6 | **Rétrodocumentation** | `challenge/retrodoc` | ⭐⭐ |
| 7 | **Mapping Codebase** | `challenge/mapping` | ⭐⭐ |
| 8 | **Debugging (4 bugs)** | `challenge/debugging` | ⭐⭐⭐ |

## Comment utiliser

<!--
  WORKFLOW POUR TESTER UN AGENT :
  1. Cloner ce repo
  2. Checkout la branche du challenge voulu
  3. Lire le TASK.md pour comprendre les consignes
  4. Laisser l'agent IA travailler
  5. Lancer validate_challengeN.py pour vérifier le résultat
  Ou bien utiliser run_benchmark.sh qui automatise tout ça.
-->

Chaque challenge a sa propre branche avec un fichier `TASK.md` décrivant l'objectif et les critères de validation.

### Challenge 1 — Merge Conflict
<!--
  SCÉNARIO : Deux développeurs ont modifié le même fichier (config/settings.py)
  en parallèle. L'un a changé les valeurs, l'autre a restructuré le fichier.
  Le merge crée un conflit que l'agent doit résoudre intelligemment.
-->
```bash
git merge feature/update-config feature/refactor-config
# Résoudre le conflit dans config/settings.py
```

### Challenge 2 — Credentials Hardcodées
<!--
  SCÉNARIO : Un développeur junior a écrit du code fonctionnel mais avec
  des mots de passe, clés API et tokens écrits en dur dans le code.
  L'agent doit les extraire dans un fichier .env et utiliser python-dotenv.
-->
```bash
git checkout challenge/hardcoded-creds
# Remplacer les credentials dans 4 fichiers par python-dotenv
```

### Challenge 3 — Refactoring Pipeline
<!--
  SCÉNARIO : Le pipeline a grossi organiquement — tout est dans une seule
  fonction de 271 lignes. L'agent doit le découper en 3 modules propres
  (extract, transform, load) avec un orchestrateur.
-->
```bash
git checkout challenge/monolith-pipeline
# Refactorer pipeline.py (300 lignes) en extract/transform/load
```

### Challenge 4 — Checkpointing
<!--
  SCÉNARIO : Le pipeline en 10 étapes prend du temps. Si ça plante à
  l'étape 7, tout recommence à zéro. L'agent doit ajouter un système
  de sauvegarde d'état après chaque étape pour pouvoir reprendre.
-->
```bash
git checkout challenge/add-checkpointing
# Ajouter un système de reprise à l'étape N sur 10
```

### Challenge 5 — Data Quality
<!--
  SCÉNARIO : Le pipeline traite des données sans aucune vérification
  de qualité. L'agent doit créer un module complet : profiling statistique,
  rapport JSON, et seuils qui bloquent le pipeline si la qualité est trop basse.
-->
```bash
git checkout challenge/data-quality
# Implémenter profiling + rapport JSON + seuils bloquants
```

### Challenge 6 — Rétrodocumentation
<!--
  SCÉNARIO : Le code fonctionne mais n'a aucune documentation.
  L'agent doit ajouter des docstrings à toutes les fonctions, classes
  et modules en suivant un template strict (Args, Returns, Raises).
-->
```bash
git checkout challenge/retrodoc
# Documenter 4 fichiers Python selon le template DOCSTRING_TEMPLATE.md
```

### Challenge 7 — Mapping Codebase
<!--
  SCÉNARIO : L'agent doit produire un fichier MAPPING.md qui cartographie
  exhaustivement la codebase : modules, classes, fonctions, dépendances
  internes et points d'entrée.
-->
```bash
git checkout challenge/mapping
# Produire un MAPPING.md complet de la codebase (6 modules, 7 classes, 11 fonctions)
```

### Challenge 8 — Debugging (4 bugs)
<!--
  SCÉNARIO : 4 fichiers contiennent chacun un type de bug différent :
  erreur de type (list/array/Series), boucle infinie, chemins de fichiers
  incorrects, et code lent à vectoriser. L'agent doit tous les corriger.
-->
```bash
git checkout challenge/debugging
# Corriger 4 types de bugs : type errors, boucles infinies, mauvais chemins, code lent
```

## Validation

<!--
  COMMENT MARCHE LA VALIDATION :
  Les scripts validate_challengeN.py utilisent l'AST Python (Abstract Syntax Tree)
  pour analyser le code sans l'exécuter. Ils vérifient :
  - La structure des fichiers (est-ce que les bons fichiers existent ?)
  - Le contenu du code (est-ce qu'il y a les bonnes fonctions ?)
  - L'absence de problèmes (est-ce que les credentials ont disparu ?)
  - La validité syntaxique (est-ce que le Python est correct ?)
  Retourne exit code 0 = PASS, 1 = FAIL
-->

Les scripts `validate_challengeN.py` sont dans la branche `main` et vérifient les critères de réussite de la branche active.
