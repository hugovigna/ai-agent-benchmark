"""
Bug 1 : Erreur de type — mélange list / np.array / pd.Series

Ce module calcule des statistiques sur des données de ventes.
Il y a des erreurs de type qui font planter le code à l'exécution.
"""

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
    """Calcule le prix unitaire = montant / quantité.

    BUG: amounts est une list Python, quantities est un np.array.
    La division list / np.array ne donne pas le résultat attendu
    quand on essaie ensuite de l'utiliser comme pd.Series.
    """
    prices = amounts / quantities  # BUG: amounts est une list, pas un array
    return prices


def filter_above_threshold(values, threshold):
    """Filtre les valeurs au-dessus d'un seuil.

    BUG: utilise len() sur le résultat d'un masque booléen numpy
    appliqué à une list Python.
    """
    mask = np.array(values) > threshold
    filtered = values[mask]  # BUG: values est une list, pas indexable par masque bool
    return filtered


def build_summary_dataframe(data):
    """Construit un DataFrame résumé par catégorie.

    BUG: passe un np.array là où une pd.Series est attendue pour groupby.
    """
    df = pd.DataFrame(data)
    amounts_array = np.array(data["amounts"])

    # BUG: on écrase la colonne avec un np.array puis on essaie .groupby dessus
    df["amounts"] = amounts_array

    # Calcul des prix unitaires (propagation du bug de compute_unit_prices)
    quantities_array = np.array(data["quantities"])
    df["unit_price"] = compute_unit_prices(data["amounts"], quantities_array)

    summary = df.groupby("categories").agg(
        total_amount=("amounts", "sum"),
        avg_unit_price=("unit_price", "mean"),
        count=("quantities", "sum"),
    ).reset_index()

    return summary


def get_top_category(summary_df):
    """Retourne la catégorie avec le plus gros montant total.

    BUG: .idxmax() retourne un index entier, pas directement la catégorie.
    On l'utilise comme si c'était le nom de la catégorie.
    """
    top_idx = summary_df["total_amount"].idxmax()
    # BUG: top_idx est un entier (index), on le traite comme le nom de catégorie
    return top_idx  # Devrait être summary_df.loc[top_idx, "categories"]


def run_analysis():
    """Point d'entrée de l'analyse — doit retourner un dict avec les résultats."""
    data = load_sales_data()

    # Étape 1 : filtrer les gros montants
    big_sales = filter_above_threshold(data["amounts"], 200.0)

    # Étape 2 : construire le résumé
    summary = build_summary_dataframe(data)

    # Étape 3 : top catégorie
    top_cat = get_top_category(summary)

    return {
        "big_sales": list(big_sales) if not isinstance(big_sales, list) else big_sales,
        "summary": summary.to_dict("records"),
        "top_category": top_cat,
    }
