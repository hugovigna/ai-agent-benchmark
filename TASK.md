# Challenge 6 : Rétrodocumentation d'une branche entière

## Objectif

Ajouter une documentation complète à **tous** les fichiers Python du dossier `src/`,
en suivant **strictement** le template défini dans `DOCSTRING_TEMPLATE.md`.

Le code fonctionne correctement mais n'a aucune documentation : pas de docstrings
de module, pas de docstrings de classe, pas de docstrings de fonction.

## Fichiers à documenter

- `src/data_loader.py` — Chargement et validation de données
- `src/transformer.py` — Transformations et agrégations de DataFrames
- `src/exporter.py` — Export de données en CSV, JSON, Parquet
- `src/pipeline_runner.py` — Orchestration de pipeline par étapes

## Critères de validation (stricte)

1. **En-tête de module** : chaque fichier `.py` (hors `__init__.py`) a un docstring de module
2. **Docstring de classe** : chaque classe a un docstring contenant une section `Attributes:`
3. **Docstring de fonction/méthode** : chaque fonction et méthode a un docstring contenant :
   - Une section `Args:` avec le **type** de chaque paramètre (entre parenthèses)
   - Une section `Returns:` avec le **type** retourné
   - Une section `Raises:` si la fonction lève des exceptions
4. **`__init__`** : les méthodes `__init__` ont un docstring avec `Args:`
5. **Syntaxe Python valide** : aucune erreur de syntaxe introduite
6. **Code inchangé** : seuls des docstrings sont ajoutés, le code exécutable ne change pas

## Template

Voir `DOCSTRING_TEMPLATE.md` pour le format exact à respecter.

## Validation

```bash
python3 validate_challenge6.py
```
