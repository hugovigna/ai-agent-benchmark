<!-- =============================================================================
  TASK.md — Consignes pour le Challenge 1
  Ce fichier est lu par l'agent IA avant de commencer le challenge.
  Il décrit ce qu'il doit faire et comment on vérifie qu'il a réussi.
============================================================================= -->

# Challenge 1: Merge Conflict Resolution

## Objectif
<!-- L'agent doit fusionner (merge) deux branches Git qui modifient le même fichier.
     C'est un scénario ultra-courant en équipe : deux développeurs travaillent
     sur le même fichier en parallèle, et Git ne sait pas comment combiner. -->
Fusionner les branches `feature/update-config` et `feature/refactor-config` qui modifient toutes deux `config/settings.py`.

## Contexte
<!-- DÉTAIL DU CONFLIT :
     Branche 1 (update-config) a changé les VALEURS :
       - host: localhost → prod-db.company.internal
       - batch_size: 1000 → 5000
       - timeout: 300 → 600
       - Ajouté: pool_size, max_overflow, enable_profiling

     Branche 2 (refactor-config) a changé la STRUCTURE :
       - Ajouté des commentaires "# -- Section --"
       - Renommé "name" → "database_name", "timeout" → "timeout_seconds"
       - Ajouté: connection_timeout, parallel_workers, retention_days
       - Ajouté 2 nouvelles sections : MONITORING et ALERTING

     Les deux touchent les mêmes lignes (DATABASE, PIPELINE) → CONFLIT
     L'agent doit comprendre l'intention de chaque branche et combiner les deux :
       - Garder les valeurs de prod (branche 1)
       - Garder la structure et les nouvelles sections (branche 2) -->
- `feature/update-config` : met à jour les valeurs de configuration pour la production (batch_size, pool_size, timeouts)
- `feature/refactor-config` : restructure le fichier en ajoutant de nouvelles sections (monitoring, alerting) et renomme des clés

## Critères de validation
<!-- Pas de script de validation automatique pour ce challenge car
     la "bonne" résolution dépend du jugement. On vérifie manuellement. -->
1. Le merge est complété sans conflit résiduel
2. Les valeurs de production de `update-config` sont préservées
3. Les nouvelles sections de `refactor-config` sont incluses
4. Le fichier résultant est syntaxiquement valide (Python)
5. Aucune perte de configuration
