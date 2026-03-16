# Challenge 3: Refactoring Pipeline Monolithique

## Objectif
Refactorer `src/pipeline.py` (~300 lignes, une seule fonction) en modules séparés avec logging entre chaque étape.

## Architecture cible
```
src/
  pipeline/
    __init__.py          # Orchestrateur principal
    extract.py           # Steps 1-3: découverte, parsing CSV, parsing JSON
    transform.py         # Steps 4-8: merge, dedup, clean, validate, enrich
    load.py              # Steps 9-10: aggregation, écriture fichiers
```

## Critères de validation
1. `src/pipeline.py` original est remplacé par le package `src/pipeline/`
2. Chaque module (extract, transform, load) est autonome et testable
3. Logging entre chaque étape avec timing (durée de chaque étape)
4. L'orchestrateur dans `__init__.py` appelle les étapes dans l'ordre
5. Le comportement final est identique (mêmes fichiers de sortie)
6. Chaque fonction a une signature claire avec des types documentés
7. Pas de code dupliqué entre modules
