"""Module de statistiques sur des données de ventes."""

import numpy as np
import pandas as pd


def load_sales_data():
    """Simule le chargement de données de ventes."""
    return {
        "amounts": [120.5, 340.0, 89.99, 210.0, 55.5, 430.0, 175.0, 90.0, 310.0, 260.0],
        "quantities": [2, 5, 1, 3, 1, 7, 2, 1, 4, 3],
        "categories": ["A", "B", "A", "C", "B", "A", "C", "B", "A", "C"],
    }


def compute_unit_prices(amounts, quantities):
    """Calcule le prix unitaire = montant / quantité."""
    prices = amounts / quantities
    return prices


def filter_above_threshold(values, threshold):
    """Filtre les valeurs au-dessus d'un seuil."""
    mask = np.array(values) > threshold
    filtered = values[mask]
    return filtered


def build_summary_dataframe(data):
    """Construit un DataFrame résumé par catégorie."""
    df = pd.DataFrame(data)
    amounts_array = np.array(data["amounts"])

    df["amounts"] = amounts_array

    quantities_array = np.array(data["quantities"])
    df["unit_price"] = compute_unit_prices(data["amounts"], quantities_array)

    summary = df.groupby("categories").agg(
        total_amount=("amounts", "sum"),
        avg_unit_price=("unit_price", "mean"),
        count=("quantities", "sum"),
    ).reset_index()

    return summary


def get_top_category(summary_df):
    """Retourne la catégorie avec le plus gros montant total."""
    top_idx = summary_df["total_amount"].idxmax()
    return top_idx


def run_analysis():
    """Point d'entrée de l'analyse — doit retourner un dict avec les résultats."""
    data = load_sales_data()

    big_sales = filter_above_threshold(data["amounts"], 200.0)

    summary = build_summary_dataframe(data)

    top_cat = get_top_category(summary)

    return {
        "big_sales": list(big_sales) if not isinstance(big_sales, list) else big_sales,
        "summary": summary.to_dict("records"),
        "top_category": top_cat,
    }
