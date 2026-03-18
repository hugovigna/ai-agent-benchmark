# Challenge 8 : Debugging

## Objectif

Les 4 fichiers Python dans `src/` contiennent des bugs. Le code ne fonctionne pas correctement.
Trouvez et corrigez tous les bugs pour que chaque module passe la validation.

## Fichiers à débugger

| Fichier | Point d'entrée | Critère de succès |
|---------|---------------|-------------------|
| `src/bug_type_error.py` | `run_analysis()` | Retourne un dict avec `big_sales` (liste de float > 200), `summary` (liste de dicts), `top_category` (string "A", "B" ou "C") |
| `src/bug_infinite_loop.py` | `run_all_tasks()` | Termine en **< 5 secondes**, retourne un dict avec les résultats de 3 tâches |
| `src/bug_wrong_path.py` | `process_files()` | Retourne un dict avec `status: "ok"`, charge correctement les 3 fichiers de `data/` |
| `src/bug_slow_code.py` | `run_analysis(100_000)` | Produit des résultats numériquement corrects en **< 2 secondes** |

## Données

Les fichiers de données sont dans le dossier `data/`.

## Validation

```bash
python3 validate_challenge8.py
```

## Règles

- Corriger les bugs **sans changer la logique métier** (mêmes résultats)
- Les signatures de fonctions publiques doivent rester identiques
- Le point d'entrée de chaque module doit fonctionner correctement
