"""Module de traitement de données tabulaires avec calculs statistiques."""

import pandas as pd
import numpy as np
import time


def generate_test_data(n_rows=100_000):
    """Génère un DataFrame de test avec n_rows lignes."""
    np.random.seed(42)
    return pd.DataFrame({
        "price": np.random.uniform(10, 1000, n_rows),
        "quantity": np.random.randint(1, 50, n_rows),
        "discount_pct": np.random.uniform(0, 0.3, n_rows),
        "tax_rate": np.random.choice([0.05, 0.10, 0.20], n_rows),
        "category": np.random.choice(["electronics", "food", "clothing", "books"], n_rows),
        "region": np.random.choice(["north", "south", "east", "west"], n_rows),
    })


def compute_net_revenue(df):
    """Calcule le revenu net pour chaque ligne.

    Formule: price * quantity * (1 - discount_pct) * (1 + tax_rate)
    """
    net_revenues = []
    for i in range(len(df)):
        price = df.iloc[i]["price"]
        qty = df.iloc[i]["quantity"]
        discount = df.iloc[i]["discount_pct"]
        tax = df.iloc[i]["tax_rate"]
        net = price * qty * (1 - discount) * (1 + tax)
        net_revenues.append(net)
    df = df.copy()
    df["net_revenue"] = net_revenues
    return df


def categorize_revenue(df):
    """Catégorise chaque ligne en 'low', 'medium', 'high' selon le revenu net."""
    categories = []
    for i in range(len(df)):
        rev = df.iloc[i]["net_revenue"]
        if rev < 500:
            categories.append("low")
        elif rev < 5000:
            categories.append("medium")
        else:
            categories.append("high")
    df = df.copy()
    df["revenue_category"] = categories
    return df


def compute_regional_stats(df):
    """Calcule des stats par région."""
    regions = df["region"].unique()
    stats = {}
    for region in regions:
        region_data = df[df["region"] == region]
        total = 0
        count = 0
        max_val = float("-inf")
        min_val = float("inf")
        for i in range(len(region_data)):
            val = region_data.iloc[i]["net_revenue"]
            total += val
            count += 1
            if val > max_val:
                max_val = val
            if val < min_val:
                min_val = val
        stats[region] = {
            "total": total,
            "mean": total / count if count > 0 else 0,
            "max": max_val,
            "min": min_val,
            "count": count,
        }
    return stats


def compute_discount_impact(df):
    """Calcule l'impact du discount sur le revenu par catégorie."""
    categories = df["category"].unique()
    impact = {}
    for cat in categories:
        cat_data = df[df["category"] == cat]
        total_without_discount = 0
        total_with_discount = 0
        for i in range(len(cat_data)):
            row = cat_data.iloc[i]
            full_price = row["price"] * row["quantity"] * (1 + row["tax_rate"])
            discounted = full_price * (1 - row["discount_pct"])
            total_without_discount += full_price
            total_with_discount += discounted
        impact[cat] = {
            "revenue_without_discount": total_without_discount,
            "revenue_with_discount": total_with_discount,
            "discount_impact": total_without_discount - total_with_discount,
            "discount_pct_avg": (total_without_discount - total_with_discount) / total_without_discount
            if total_without_discount > 0 else 0,
        }
    return impact


def run_analysis(n_rows=100_000):
    """Point d'entrée — exécute toute l'analyse et retourne les résultats + timing."""
    df = generate_test_data(n_rows)

    start = time.time()

    df = compute_net_revenue(df)
    df = categorize_revenue(df)
    regional = compute_regional_stats(df)
    discount = compute_discount_impact(df)

    elapsed = time.time() - start

    return {
        "elapsed_seconds": round(elapsed, 3),
        "n_rows": n_rows,
        "regional_stats": regional,
        "discount_impact": discount,
        "revenue_categories": df["revenue_category"].value_counts().to_dict(),
    }
