#!/usr/bin/env python3
"""
Validation script for Challenge 8: Debugging.

Tests all 4 bug files to verify they produce correct results.
"""

import sys
import os
import time
import threading
import subprocess

# Add project root to path
sys.path.insert(0, os.getcwd())

passed = 0
failed = 0


def check(label, condition, detail=""):
    global passed, failed
    if condition:
        print(f"  ✅ {label}")
        passed += 1
    else:
        print(f"  ❌ {label}" + (f" — {detail}" if detail else ""))
        failed += 1


def run_with_timeout(func, timeout_seconds=10):
    """Run a function with a timeout using threading."""
    result_holder = [None]
    error_holder = [None]

    def wrapper():
        try:
            result_holder[0] = func()
        except Exception as e:
            error_holder[0] = str(e)

    thread = threading.Thread(target=wrapper)
    thread.daemon = True
    thread.start()
    thread.join(timeout=timeout_seconds)

    if thread.is_alive():
        return "timeout", f"Timeout after {timeout_seconds}s"

    if error_holder[0] is not None:
        return "error", error_holder[0]

    return "ok", result_holder[0]


# =============================================================================
# Bug 1: Type errors
# =============================================================================
def validate_type_errors():
    print("\n🐛 Bug 1 — Erreurs de type (bug_type_error.py)")

    try:
        from src.bug_type_error import run_analysis
    except Exception as e:
        check("Import réussi", False, str(e))
        return

    check("Import réussi", True)

    status, result = run_with_timeout(run_analysis, timeout_seconds=10)

    if status == "timeout":
        check("Exécution termine", False, "timeout")
        return
    if status == "error":
        check("Exécution sans erreur", False, result)
        return

    check("Exécution sans erreur", True)
    check("Retourne un dict", isinstance(result, dict))

    if not isinstance(result, dict):
        return

    # Check big_sales
    big_sales = result.get("big_sales", [])
    check("big_sales est une liste", isinstance(big_sales, list))
    if isinstance(big_sales, list) and len(big_sales) > 0:
        check("big_sales contient des floats > 200",
              all(isinstance(x, (int, float)) and x > 200 for x in big_sales))
    else:
        check("big_sales non vide", False, f"got {big_sales}")

    # Check summary
    summary = result.get("summary", [])
    check("summary est une liste de dicts", isinstance(summary, list) and len(summary) > 0)
    if isinstance(summary, list) and len(summary) > 0:
        required_keys = {"categories", "total_amount", "avg_unit_price", "count"}
        first_keys = set(summary[0].keys())
        check("summary a les bonnes clés", required_keys.issubset(first_keys),
              f"manque: {required_keys - first_keys}")

    # Check top_category
    top_cat = result.get("top_category")
    check("top_category est un string", isinstance(top_cat, str), f"got {type(top_cat).__name__}: {top_cat}")
    check("top_category est A, B ou C", top_cat in ("A", "B", "C"), f"got '{top_cat}'")


# =============================================================================
# Bug 2: Infinite loops
# =============================================================================
def validate_infinite_loops():
    print("\n🐛 Bug 2 — Boucles infinies (bug_infinite_loop.py)")

    try:
        from src.bug_infinite_loop import run_all_tasks
    except Exception as e:
        check("Import réussi", False, str(e))
        return

    check("Import réussi", True)

    start = time.time()
    status, result = run_with_timeout(run_all_tasks, timeout_seconds=5)
    elapsed = time.time() - start

    if status == "timeout":
        check("Termine en < 5s", False, f"timeout après {elapsed:.1f}s — boucle infinie probable")
        return
    if status == "error":
        check("Exécution sans erreur", False, result)
        return

    check("Termine en < 5s", elapsed < 5, f"{elapsed:.1f}s")
    check("Retourne un dict", isinstance(result, dict))

    if not isinstance(result, dict):
        return

    # Check fetch result
    fetch = result.get("fetch", {})
    check("fetch retourne un dict avec status", isinstance(fetch, dict) and "status" in fetch)

    # Check convergence
    conv = result.get("convergence", {})
    check("convergence retourne un dict", isinstance(conv, dict))
    if isinstance(conv, dict):
        check("convergence a convergé", conv.get("converged", False) == True,
              f"converged={conv.get('converged')}")

    # Check queue
    q = result.get("queue", {})
    check("queue retourne un dict", isinstance(q, dict))
    if isinstance(q, dict):
        results_list = q.get("results", [])
        check("queue.results non vide", len(results_list) > 0)
        # Items not divisible by 3 (1,2,4,5,7,8) should be doubled
        expected_values = sorted([2, 4, 8, 10, 14, 16])
        actual_sorted = sorted(results_list)
        check("queue.results contient les bonnes valeurs",
              actual_sorted == expected_values,
              f"attendu {expected_values}, got {actual_sorted}")


# =============================================================================
# Bug 3: Wrong file paths
# =============================================================================
def validate_wrong_paths():
    print("\n🐛 Bug 3 — Chemins incorrects (bug_wrong_path.py)")

    try:
        from src.bug_wrong_path import process_files
    except Exception as e:
        check("Import réussi", False, str(e))
        return

    check("Import réussi", True)

    status, result = run_with_timeout(process_files, timeout_seconds=10)

    if status == "timeout":
        check("Exécution termine", False, "timeout")
        return
    if status == "error":
        check("Exécution sans erreur", False, result)
        return

    check("Exécution sans erreur", True)
    check("Retourne un dict", isinstance(result, dict))

    if not isinstance(result, dict):
        return

    check("status == 'ok'", result.get("status") == "ok", f"got '{result.get('status')}'")

    data = result.get("data", {})
    check("data contient config", "config" in data)
    check("data contient reference_count", "reference_count" in data)
    check("data contient mapping_keys", "mapping_keys" in data)

    if "config" in data:
        check("config.version existe", "version" in data["config"])

    if "reference_count" in data:
        check("reference_count == 5", data["reference_count"] == 5,
              f"got {data['reference_count']}")

    if "mapping_keys" in data:
        expected_keys = sorted(["electronics", "food", "clothing", "books"])
        check("mapping_keys correct", sorted(data["mapping_keys"]) == expected_keys,
              f"got {data['mapping_keys']}")

    # Check output file has .json extension
    output = result.get("output", "")
    check("output a l'extension .json", output.endswith(".json"),
          f"got '{output}'")


# =============================================================================
# Bug 4: Slow code (vectorization)
# =============================================================================
def validate_slow_code():
    print("\n🐛 Bug 4 — Code lent à vectoriser (bug_slow_code.py)")

    try:
        from src.bug_slow_code import run_analysis, generate_test_data
    except Exception as e:
        check("Import réussi", False, str(e))
        return

    check("Import réussi", True)

    # First run and check correctness
    status, result = run_with_timeout(lambda: run_analysis(100_000), timeout_seconds=30)

    if status == "timeout":
        check("Exécution termine (30s max)", False, "timeout")
        return
    if status == "error":
        check("Exécution sans erreur", False, result)
        return

    check("Exécution sans erreur", True)
    check("Retourne un dict", isinstance(result, dict))

    if not isinstance(result, dict):
        return

    elapsed = result.get("elapsed_seconds", 999)
    check(f"Performance < 2s (actual: {elapsed}s)", elapsed < 2.0,
          f"{elapsed}s — trop lent")

    # Check correctness of results
    regional = result.get("regional_stats", {})
    check("Stats régionales pour 4 régions", len(regional) == 4,
          f"got {len(regional)} régions")

    if regional:
        for region, stats in regional.items():
            if not isinstance(stats, dict):
                check(f"Stats '{region}' est un dict", False)
                break
            required = {"total", "mean", "max", "min", "count"}
            if not required.issubset(set(stats.keys())):
                check(f"Stats '{region}' a toutes les clés", False,
                      f"manque: {required - set(stats.keys())}")
                break
        else:
            check("Stats régionales bien formées", True)

    discount = result.get("discount_impact", {})
    check("Impact discount pour 4 catégories", len(discount) == 4,
          f"got {len(discount)}")

    categories = result.get("revenue_categories", {})
    check("Catégories de revenu présentes", len(categories) > 0)
    if categories:
        expected_cats = {"low", "medium", "high"}
        check("3 catégories (low/medium/high)", set(categories.keys()) == expected_cats,
              f"got {set(categories.keys())}")

    # Verify numerical accuracy by computing reference values
    try:
        import numpy as np
        import pandas as pd
        df = generate_test_data(100_000)
        ref_net = df["price"] * df["quantity"] * (1 - df["discount_pct"]) * (1 + df["tax_rate"])

        # Check that regional totals sum up to approximately the same total
        if regional:
            computed_total = sum(s.get("total", 0) for s in regional.values())
            expected_total = float(ref_net.sum())
            rel_error = abs(computed_total - expected_total) / expected_total if expected_total > 0 else 0
            check(f"Résultats numériques corrects (erreur relative: {rel_error:.6f})",
                  rel_error < 0.01,
                  f"total attendu ≈ {expected_total:.0f}, obtenu {computed_total:.0f}")
    except Exception as e:
        check("Vérification numérique", False, str(e))


# =============================================================================
# Main
# =============================================================================
def main():
    global passed, failed

    print("=" * 60)
    print("  Challenge 8 — Validation Debugging")
    print("=" * 60)

    validate_type_errors()
    validate_infinite_loops()
    validate_wrong_paths()
    validate_slow_code()

    # Clean up any generated output files
    results_file = os.path.join(os.getcwd(), "data", "results.json")
    if os.path.exists(results_file):
        os.remove(results_file)

    # --- Summary ---
    print("\n" + "=" * 60)
    total = passed + failed
    print(f"  Résultat: {passed}/{total} checks passés")
    if failed == 0:
        print("  🎉 CHALLENGE 8 RÉUSSI !")
    else:
        print(f"  ⚠️  {failed} check(s) échoué(s)")
    print("=" * 60)

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
