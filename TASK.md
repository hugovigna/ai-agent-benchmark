<!-- =============================================================================
  TASK.md — Consignes pour le Challenge 3
============================================================================= -->

# Challenge 3: Refactoring Pipeline Monolithique

<!-- POURQUOI C'EST UN PROBLÈME :
     src/pipeline.py fait ~300 lignes dans UNE SEULE FONCTION run_pipeline().
     C'est ce qu'on appelle un "God Function" ou "monolith" :
     - Impossible à tester unitairement (on ne peut pas tester juste l'extraction)
     - Difficile à maintenir (un changement dans le nettoyage peut casser l'écriture)
     - Illisible pour un nouveau développeur
     - Pas de réutilisation possible (si on veut juste la partie extract ailleurs)

     LE PATTERN ETL :
     ETL = Extract-Transform-Load, le pattern standard en data engineering :
       Extract   = lire les données depuis les sources
       Transform = nettoyer, valider, enrichir les données
       Load      = écrire les résultats (fichiers, base de données)
     Chaque phase dans son propre module = clean architecture. -->

## Objectif
Refactorer `src/pipeline.py` (~300 lignes, une seule fonction) en modules séparés avec logging entre chaque étape.

## Architecture cible
<!-- L'agent doit :
     1. Supprimer src/pipeline.py (le fichier monolithique)
     2. Créer src/pipeline/ (un package Python = dossier avec __init__.py)
     3. Découper le code dans 3 modules + 1 orchestrateur

     __init__.py = Le "chef d'orchestre" qui appelle extract → transform → load
     extract.py  = Steps 1-3 du pipeline original (découvrir et lire les fichiers)
     transform.py = Steps 4-8 (merge, dedup, clean, validate, enrich)
     load.py     = Steps 9-10 (calcul des stats et écriture des fichiers) -->
```
src/
  pipeline/
    __init__.py          # Orchestrateur principal
    extract.py           # Steps 1-3: découverte, parsing CSV, parsing JSON
    transform.py         # Steps 4-8: merge, dedup, clean, validate, enrich
    load.py              # Steps 9-10: aggregation, écriture fichiers
```

## Critères de validation
<!-- Ces critères correspondent aux vérifications de validate_challenge3.py -->
1. `src/pipeline.py` original est remplacé par le package `src/pipeline/`
2. Chaque module (extract, transform, load) est autonome et testable
3. Logging entre chaque étape avec timing (durée de chaque étape)
4. L'orchestrateur dans `__init__.py` appelle les étapes dans l'ordre
5. Le comportement final est identique (mêmes fichiers de sortie)
6. Chaque fonction a une signature claire avec des types documentés
7. Pas de code dupliqué entre modules
