# Challenge 7 : Mapping d'une branche entière

## Objectif

Produire un fichier `MAPPING.md` qui cartographie **exhaustivement** la codebase :
tous les modules, classes, fonctions, leurs relations et dépendances.

## Structure attendue du MAPPING.md

Le fichier doit contenir **exactement** les sections suivantes, dans cet ordre :

### 1. `## Modules`
Un tableau listant **chaque fichier `.py`** (hors `__init__.py`) avec :
- Chemin du fichier
- Description en une ligne
- Dépendances internes (imports depuis le projet)

### 2. `## Classes`
Un tableau listant **chaque classe** avec :
- Nom de la classe
- Module (fichier) où elle est définie
- Méthodes publiques (liste)
- Description en une ligne

### 3. `## Fonctions`
Un tableau listant **chaque fonction standalone** (hors méthodes de classe) avec :
- Nom de la fonction
- Module (fichier) où elle est définie
- Paramètres (avec types si disponibles)
- Type de retour

### 4. `## Dépendances`
Un graphe textuel ou une liste montrant les imports **internes** entre modules :
- Quels modules importent quoi depuis quels autres modules
- Format : `module_a -> module_b` (un par ligne)

### 5. `## Point d'entrée`
Identifier la/les fonction(s) ou classe(s) qui servent de point d'entrée principal
du pipeline.

## Fichiers à analyser

```
config/settings.py
src/models.py
src/ingestion.py
src/transform.py
src/export.py
src/orchestrator.py
```

## Validation

```bash
python3 validate_challenge7.py
```

## Critères stricts

1. Le fichier `MAPPING.md` existe à la racine
2. Les 5 sections obligatoires sont présentes
3. **Tous** les modules sont listés (6 fichiers)
4. **Toutes** les classes sont listées (8 classes)
5. **Toutes** les fonctions standalone sont listées (10 fonctions)
6. **Toutes** les dépendances internes sont documentées
7. Au moins un point d'entrée est identifié
