# Challenge 9 — SQL Queries

## Contexte

Tu disposes d'une base de données SQLite `data/sql/shop.db` représentant un e-commerce fictif.

### Schéma

```
categories  (id, name)
products    (id, name, category_id, price)
customers   (id, name, email, region, created_at)
orders      (id, customer_id, ordered_at, status)   -- status: completed | cancelled | pending
order_items (id, order_id, product_id, quantity, unit_price)
```

## Objectif

Écrire **9 requêtes SQL** dans le dossier `queries/`, une par fichier.  
Chaque requête doit retourner exactement les colonnes et l'ordre indiqués.

---

## Tâches

### A1 — JOIN multi-tables (`queries/A1_join.sql`)

Retourne toutes les lignes de commande avec :
- `order_id`, `customer_name`, `product_name`, `quantity`, `unit_price`, `line_total`

`line_total` = `quantity * unit_price` arrondi à 2 décimales.  
Ordonné par `order_id ASC`, puis `product_name ASC`.  
Inclure tous les statuts de commande.

---

### A2 — Agrégation par région (`queries/A2_aggregation.sql`)

Chiffre d'affaires (`ca`) par `region` pour les commandes **completed** entre le **2024-07-01** et le **2024-12-31** inclus.  
`ca` = somme de `quantity * unit_price` arrondie à 2 décimales.  
Ordonné par `ca DESC`.

Colonnes attendues : `region`, `ca`

---

### A6 — Déduplication clients (`queries/A6_dedup.sql`)

La table `customers` contient des doublons (même `name`).  
Retourne la liste dédupliquée en gardant le client avec le **plus petit `id`** pour chaque nom.

Colonnes attendues : `id`, `name`, `email`, `region`, `created_at`  
Ordonné par `id ASC`.

---

### B1 — Text-to-SQL : commandes sans décembre (`queries/B1_no_december.sql`)

> "Donne-moi les clients qui ont passé plus de 3 commandes **completed** mais jamais en décembre."

Colonnes attendues : `id`, `name`, `nb_orders`  
Ordonné par `nb_orders DESC`, puis `id ASC`.

---

### B2 — Text-to-SQL : produits fréquemment achetés ensemble (`queries/B2_bought_together.sql`)

> "Trouve les paires de produits le plus souvent achetés dans la même commande."

Colonnes attendues : `product_a`, `product_b`, `co_occurrences`  
Contrainte : `product_a < product_b` (ordre alphabétique pour éviter les doublons).  
Ordonné par `co_occurrences DESC`.  
Retourner toutes les paires (pas de LIMIT).

---

### B3 — Text-to-SQL : clients perdus (`queries/B3_churned.sql`)

> "Clients ayant passé au moins une commande **completed** en 2023 mais aucune commande **completed** en 2024."

Colonnes attendues : `id`, `name`  
Ordonné par `id ASC`.

---

### B4 — Text-to-SQL : top 3 produits par catégorie (`queries/B4_top3_by_category.sql`)

> "Top 3 produits par catégorie selon le chiffre d'affaires total."

CA = somme de `quantity * unit_price` arrondie à 2 décimales.  
Colonnes attendues : `category`, `product`, `revenue`, `rnk`  
`rnk` = rang dans la catégorie (1 = meilleur CA).  
Ordonné par `category ASC`, puis `rnk ASC`.

---

### B5 — Text-to-SQL : taux de rétention mensuel (`queries/B5_retention.sql`)

> "Pour chaque mois, combien de clients actifs (commande **completed**) sont aussi actifs le mois suivant ?"

Colonnes attendues : `month` (format `YYYY-MM`), `active`, `retained`, `retention_pct`  
`retention_pct` = `100.0 * retained / active` arrondi à 1 décimale.  
Ordonné par `month ASC`.

---

### C1 — Emails malformés (`queries/C1_bad_emails.sql`)

Retourne les clients dont l'email est malformé, c'est-à-dire au moins l'une des conditions suivantes :
- contient des majuscules
- contient des espaces en début ou fin
- contient `@@`
- ne contient pas exactement un `@` suivi d'un `.`

Colonnes attendues : `id`, `name`, `email`  
Ordonné par `id ASC`.

---

### C2 — Anomalies de montant (`queries/C2_anomalies.sql`)

Détecte les lignes de `order_items` dont `unit_price` est supérieur à **moyenne + 3 × écart-type** calculés sur l'ensemble de la table.

Colonnes attendues : `id`, `order_id`, `product_id`, `unit_price`  
Ordonné par `unit_price DESC`.

---

### C3 — Intégrité de la base (`queries/C3_integrity.sql`)

Produit un rapport d'intégrité en une seule requête avec les colonnes `issue` et `count` :

| issue | count |
|---|---|
| orphan_order_items | N |
| duplicate_customers | N |
| null_emails | N |

- `orphan_order_items` : lignes de `order_items` dont l'`order_id` n'existe pas dans `orders`
- `duplicate_customers` : noms de clients qui apparaissent plus d'une fois dans `customers`
- `null_emails` : clients sans email

Ordonné par `issue ASC`.

---

## Structure attendue

```
queries/
  A1_join.sql
  A2_aggregation.sql
  A6_dedup.sql
  B1_no_december.sql
  B2_bought_together.sql
  B3_churned.sql
  B4_top3_by_category.sql
  B5_retention.sql
  C1_bad_emails.sql
  C2_anomalies.sql
  C3_integrity.sql
```

## Critères de validation

- Chaque fichier `.sql` existe dans `queries/`
- Chaque requête s'exécute sans erreur sur `data/sql/shop.db`
- Les résultats correspondent aux valeurs attendues (tolérance ±0.05 sur les montants)
