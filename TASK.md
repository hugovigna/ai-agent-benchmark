# Challenge 1: Merge Conflict Resolution

## Objectif
Fusionner les branches `feature/update-config` et `feature/refactor-config` qui modifient toutes deux `config/settings.py`.

## Contexte
- `feature/update-config` : met à jour les valeurs de configuration pour la production (batch_size, pool_size, timeouts)
- `feature/refactor-config` : restructure le fichier en ajoutant de nouvelles sections (monitoring, alerting) et renomme des clés

## Critères de validation
1. Le merge est complété sans conflit résiduel
2. Les valeurs de production de `update-config` sont préservées
3. Les nouvelles sections de `refactor-config` sont incluses
4. Le fichier résultant est syntaxiquement valide (Python)
5. Aucune perte de configuration
