# Challenge 8 : Debugging — 4 bugs à corriger

## Objectif

Corriger les 4 fichiers bugués dans `src/`. Chaque fichier contient un type de bug différent.
Le code doit **fonctionner correctement** après correction et **produire les résultats attendus**.

## Bug 1 — Erreur de type (`src/bug_type_error.py`)

Le module mélange `list`, `np.array` et `pd.Series` de façon incorrecte.
- `compute_unit_prices()` : division d'une list par un np.array
- `filter_above_threshold()` : indexation d'une list par un masque booléen numpy
- `build_summary_dataframe()` : mélange de types dans les colonnes
- `get_top_category()` : confusion entre index entier et valeur de catégorie

**Test** : `run_analysis()` doit retourner un dict avec :
- `big_sales` : liste de float > 200
- `summary` : liste de dicts avec les clés `categories`, `total_amount`, `avg_unit_price`, `count`
- `top_category` : une string parmi "A", "B", "C"

## Bug 2 — Boucle infinie (`src/bug_infinite_loop.py`)

Le module contient 3 fonctions avec des boucles qui ne terminent jamais :
- `fetch_with_retry()` : compteur jamais incrémenté
- `find_convergence()` : condition de sortie impossible + pas qui grandit
- `process_queue()` : éléments remis en queue sans limite

**Test** : `run_all_tasks()` doit terminer en **moins de 5 secondes** et retourner un dict.

## Bug 3 — Chemins de fichiers incorrects (`src/bug_wrong_path.py`)

Le module pointe vers des fichiers avec des noms erronés :
- `load_config()` : typo dans le nom de fichier
- `load_reference_data()` : mauvaise extension (.csv vs .tsv)
- `load_mapping_table()` : nom au pluriel au lieu du singulier
- `save_results()` : extension manquante

Les fichiers de données corrects sont dans `data/` :
- `data/config.json`
- `data/reference.tsv`
- `data/mapping.json`

**Test** : `process_files()` doit retourner un dict avec `status: "ok"`.

## Bug 4 — Code lent à vectoriser (`src/bug_slow_code.py`)

Le module utilise des boucles Python ligne par ligne au lieu d'opérations vectorisées.
- `compute_net_revenue()` : boucle au lieu de multiplication vectorielle
- `categorize_revenue()` : boucle if/elif au lieu de `pd.cut` ou `np.select`
- `compute_regional_stats()` : boucle au lieu de `groupby`
- `compute_discount_impact()` : double boucle au lieu de `groupby` + vectorisation

**Test** : `run_analysis(100_000)` doit :
- Produire les mêmes résultats numériques (à 0.01 près)
- Tourner en **moins de 2 secondes**

## Validation

```bash
python3 validate_challenge8.py
```

## Règles

- Corriger les bugs **sans changer la logique métier** (mêmes résultats)
- Les signatures de fonctions publiques doivent rester identiques
- Le point d'entrée de chaque module doit fonctionner correctement
