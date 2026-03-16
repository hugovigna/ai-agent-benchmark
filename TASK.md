# Challenge 4: Système de Checkpointing

## Objectif
Ajouter un système de checkpointing à `src/long_pipeline.py` pour qu'un pipeline qui plante à l'étape 7/10 puisse reprendre à l'étape 7 au lieu de tout recommencer.

## Comportement attendu
```python
# Premier run : plante à l'étape 7
run_long_pipeline()  # -> crash at step 7

# Deuxième run : reprend à l'étape 7 automatiquement
run_long_pipeline()  # -> resumes from step 7, skips 1-6
```

## Spécifications techniques
1. **Persistance** : Le contexte (state) de chaque étape complétée est sauvegardé sur disque (JSON)
2. **Reprise automatique** : Au démarrage, le pipeline détecte un checkpoint existant et reprend
3. **Nettoyage** : Après un run réussi, les checkpoints sont supprimés
4. **Identification** : Chaque run a un ID unique, les checkpoints sont liés à cet ID
5. **CLI** : Option pour forcer un restart complet (ignorer les checkpoints)

## Critères de validation
1. Un module/classe de checkpointing existe
2. Les checkpoints sont sauvegardés après chaque étape
3. Le pipeline reprend correctement à la dernière étape réussie
4. Les checkpoints sont nettoyés après succès
5. Un flag `--force-restart` ou paramètre `force_restart=True` existe
6. Le context/state est correctement sérialisé et désérialisé
7. Le code est syntaxiquement valide
