# AI Agent Benchmark — Data Engineering Challenges

Ce repo contient **5 challenges** pour évaluer la capacité d'un agent IA à résoudre des problèmes courants en data engineering.

## Challenges

| # | Challenge | Branche / Fichiers | Difficulté |
|---|-----------|-------------------|------------|
| 1 | **Merge Conflict** | `feature/update-config` vs `feature/refactor-config` | ⭐ |
| 2 | **Credentials Hardcodées** | `challenge/hardcoded-creds` | ⭐⭐ |
| 3 | **Refactoring Pipeline Monolithique** | `challenge/monolith-pipeline` | ⭐⭐⭐ |
| 4 | **Checkpointing Pipeline** | `challenge/add-checkpointing` | ⭐⭐⭐ |
| 5 | **Module Qualité de Données** | `challenge/data-quality` | ⭐⭐⭐⭐ |

## Comment utiliser

Chaque challenge a sa propre branche avec un fichier `TASK.md` décrivant l'objectif et les critères de validation.

### Challenge 1 — Merge Conflict
```bash
git merge feature/update-config feature/refactor-config
# Résoudre le conflit dans config/settings.py
```

### Challenge 2 — Credentials Hardcodées
```bash
git checkout challenge/hardcoded-creds
# Remplacer les credentials dans 4 fichiers par python-dotenv
```

### Challenge 3 — Refactoring Pipeline
```bash
git checkout challenge/monolith-pipeline
# Refactorer pipeline.py (300 lignes) en extract/transform/load
```

### Challenge 4 — Checkpointing
```bash
git checkout challenge/add-checkpointing
# Ajouter un système de reprise à l'étape N sur 10
```

### Challenge 5 — Data Quality
```bash
git checkout challenge/data-quality
# Implémenter profiling + rapport JSON + seuils bloquants
```

## Validation

Chaque branche contient un script `validate.py` qui vérifie les critères de réussite.
