# Template de Documentation — Convention Obligatoire

## En-tête de fichier (module docstring)

Chaque fichier `.py` (sauf `__init__.py`) doit commencer par un docstring de module :

```python
"""
<Titre du module> — <description courte en une ligne>.

Description détaillée du rôle de ce module dans le projet,
de ses responsabilités et de ses dépendances principales.

Auteur : <nom>
Date : <date>
"""
```

## Docstring de classe

```python
class MaClasse:
    """<Description courte de la classe en une ligne>.

    <Description détaillée du rôle de la classe,
    de son contexte d'utilisation et de ses invariants.>

    Attributes:
        attr1 (type): Description de l'attribut.
        attr2 (type): Description de l'attribut.
    """
```

## Docstring de fonction / méthode

```python
def ma_fonction(param1, param2):
    """<Description courte de ce que fait la fonction en une ligne>.

    <Description détaillée de la logique : algorithme utilisé,
    cas limites gérés, effets de bord éventuels.>

    Args:
        param1 (type): Description du paramètre.
        param2 (type): Description du paramètre.

    Returns:
        type: Description de ce qui est retourné.

    Raises:
        ExceptionType: Quand cette exception est levée.
    """
```

## Règles strictes

1. **Toute** fonction et méthode publique doit avoir un docstring
2. **Toute** classe doit avoir un docstring avec une section `Attributes:`
3. **Tout** fichier `.py` (hors `__init__.py`) doit avoir un docstring de module
4. Les sections `Args:` et `Returns:` sont **obligatoires** pour chaque fonction
5. Chaque paramètre dans `Args:` doit indiquer son **type** entre parenthèses
6. La section `Returns:` doit indiquer le **type** retourné
7. Si la fonction lève des exceptions, la section `Raises:` est obligatoire
8. Les méthodes `__init__` doivent aussi avoir un docstring avec `Args:`
