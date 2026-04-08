#!/usr/bin/env python3
"""
Validation script for Challenge 9: Pandas Pipeline.

Runs src/sales_analysis.py and checks that all metrics are numerically correct.
Bugs are silent (no exceptions) — only wrong values reveal them.
"""

import sys
import os
import math

sys.path.insert(0, os.getcwd())

passed = 0
failed = 0

# Ground truth computed manually from the CSV data
EXPECTED = {
    'total_revenue': 3520.0,
    'revenue_by_region': {'north': 1470.0, 'south': 1910.0, 'west': 140.0},
    'top_category': 'Electronics',
    'avg_order_value': 440.0,
    'monthly_revenue': {'2024-01': 2060.0, '2024-02': 1460.0},
}


def check(label, condition, detail=""):
    global passed, failed
    if condition:
        print(f"  ✅ {label}")
        passed += 1
    else:
        print(f"  ❌ {label}" + (f" — {detail}" if detail else ""))
        failed += 1


def approx_equal(a, b, tol=0.01):
    return math.isclose(float(a), float(b), rel_tol=tol)


def main():
    global passed, failed

    print("=" * 60)
    print("  Challenge 9 — Validation Pipeline Pandas")
    print("=" * 60)

    # --- Import ---
    try:
        from src.sales_analysis import run_analysis
    except ImportError as e:
        print(f"\n❌ Import impossible: {e}")
        sys.exit(1)

    # --- Run ---
    print("\n⚙️  Exécution de run_analysis()...")
    try:
        result = run_analysis()
    except Exception as e:
        print(f"\n❌ Erreur à l'exécution: {e}")
        sys.exit(1)

    check("Retourne un dict", isinstance(result, dict))
    if not isinstance(result, dict):
        sys.exit(1)

    # --- Total revenue ---
    print("\n💰 Total revenue")
    tr = result.get('total_revenue')
    check("Clé 'total_revenue' présente", tr is not None)
    if tr is not None:
        check(
            f"Valeur correcte (attendu 3520.0, obtenu {tr})",
            approx_equal(tr, EXPECTED['total_revenue']),
            "Indice: vérifier le calcul du discount et le filtre sur status"
        )

    # --- Revenue by region ---
    print("\n🗺️  Revenue by region")
    rbr = result.get('revenue_by_region', {})
    check("Clé 'revenue_by_region' présente", bool(rbr))
    for region, expected_val in EXPECTED['revenue_by_region'].items():
        actual = rbr.get(region)
        check(
            f"  {region}: attendu {expected_val}, obtenu {actual}",
            actual is not None and approx_equal(actual, expected_val),
        )

    # --- Top category ---
    print("\n🏆 Top category")
    tc = result.get('top_category')
    check("Clé 'top_category' présente", tc is not None)
    check(
        f"Valeur correcte (attendu 'Electronics', obtenu '{tc}')",
        tc == EXPECTED['top_category'],
        "Indice: vérifier l'ordre du sort et l'index sélectionné"
    )

    # --- Avg order value ---
    print("\n📊 Avg order value")
    aov = result.get('avg_order_value')
    check("Clé 'avg_order_value' présente", aov is not None)
    if aov is not None:
        check(
            f"Valeur correcte (attendu 440.0, obtenu {aov})",
            approx_equal(aov, EXPECTED['avg_order_value']),
        )

    # --- Monthly revenue ---
    print("\n📅 Monthly revenue")
    mr = result.get('monthly_revenue', {})
    check("Clé 'monthly_revenue' présente", bool(mr))
    # Keys must be strings like "2024-01", not integers like 1
    key_types_ok = all(isinstance(k, str) and '-' in str(k) for k in mr.keys())
    check(
        f"Clés au format 'YYYY-MM' (obtenu: {list(mr.keys())})",
        key_types_ok,
        "Indice: dt.month retourne un entier et perd l'année"
    )
    for month, expected_val in EXPECTED['monthly_revenue'].items():
        actual = mr.get(month)
        check(
            f"  {month}: attendu {expected_val}, obtenu {actual}",
            actual is not None and approx_equal(actual, expected_val),
        )

    # --- Summary ---
    print("\n" + "=" * 60)
    total = passed + failed
    print(f"  Résultat: {passed}/{total} checks passés")
    if failed == 0:
        print("  🎉 CHALLENGE 9 RÉUSSI !")
    else:
        print(f"  ⚠️  {failed} check(s) échoué(s)")
    print("=" * 60)

    sys.exit(0 if failed == 0 else 1)


if __name__ == '__main__':
    main()
