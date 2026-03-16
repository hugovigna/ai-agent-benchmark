<!-- =============================================================================
  TASK.md — Consignes pour le Challenge 4
============================================================================= -->

# Challenge 4: Systeme de Checkpointing

<!-- POURQUOI C'EST UN PROBLÈME :
     Le pipeline en 10 étapes (src/long_pipeline.py) n'a aucune mémoire.
     Si l'étape 7 plante (ex: timeout API, erreur réseau, crash mémoire),
     le prochain lancement recommence TOUT depuis l'étape 1.

     En production, un pipeline peut prendre 30 min à 2h.
     Recommencer à zéro chaque fois = gaspillage de temps et de compute.

     ANALOGIE : C'est comme un jeu vidéo sans sauvegarde.
     Game over au boss final ? Retour au tout début du jeu.

     LE CHECKPOINTING :
     Après chaque étape réussie, on sauvegarde l'état (le "context" dict)
     sur le disque en JSON. Au prochain lancement, on vérifie s'il existe
     un checkpoint → si oui, on reprend juste après la dernière étape réussie.
     Après un run complet réussi, on supprime les checkpoints (nettoyage). -->

## Objectif
Ajouter un systeme de checkpointing à `src/long_pipeline.py` pour qu'un pipeline qui plante à l'étape 7/10 puisse reprendre à l'étape 7 au lieu de tout recommencer.

## Comportement attendu
<!-- Séquence typique d'utilisation :
     Run 1 : étapes 1→2→3→4→5→6→7 CRASH! (chaque étape sauvegarde un checkpoint)
     Run 2 : détecte checkpoint à l'étape 6, saute 1-6, reprend à 7→8→9→10 OK
     Run 2 terminé : supprime tous les checkpoints (nettoyage) -->
```python
# Premier run : plante à l'étape 7
run_long_pipeline()  # -> crash at step 7

# Deuxième run : reprend à l'étape 7 automatiquement
run_long_pipeline()  # -> resumes from step 7, skips 1-6
```

## Spécifications techniques
<!-- Détail de ce que l'agent doit implémenter :
     1. Persistance = json.dump() du context dict dans un fichier
     2. Reprise = json.load() du dernier checkpoint + skip des étapes faites
     3. Nettoyage = os.remove() des fichiers checkpoint après succès
     4. Identification = chaque pipeline run a un ID (pour pas mélanger)
     5. Force restart = paramètre pour ignorer les checkpoints existants -->
1. **Persistance** : Le contexte (state) de chaque étape complétée est sauvegardé sur disque (JSON)
2. **Reprise automatique** : Au démarrage, le pipeline détecte un checkpoint existant et reprend
3. **Nettoyage** : Après un run réussi, les checkpoints sont supprimés
4. **Identification** : Chaque run a un ID unique, les checkpoints sont liés à cet ID
5. **CLI** : Option pour forcer un restart complet (ignorer les checkpoints)

## Critères de validation
<!-- Ces critères correspondent aux vérifications de validate_challenge4.py -->
1. Un module/classe de checkpointing existe
2. Les checkpoints sont sauvegardés après chaque étape
3. Le pipeline reprend correctement à la dernière étape réussie
4. Les checkpoints sont nettoyés après succès
5. Un flag `--force-restart` ou paramètre `force_restart=True` existe
6. Le context/state est correctement sérialisé et désérialisé
7. Le code est syntaxiquement valide
