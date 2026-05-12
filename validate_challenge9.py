"""Validation script for Challenge 9: SQL Queries.

Runs each query in queries/ against data/sql/shop.db and compares
results to the expected ground truth.
"""

import os
import sys
import sqlite3
import math

DB_PATH = "data/sql/shop.db"
QUERIES_DIR = "queries"

QUERY_FILES = [
    "A1_join.sql",
    "A2_aggregation.sql",
    "A6_dedup.sql",
    "B1_no_december.sql",
    "B2_bought_together.sql",
    "B3_churned.sql",
    "B4_top3_by_category.sql",
    "B5_retention.sql",
    "C1_bad_emails.sql",
    "C2_anomalies.sql",
    "C3_integrity.sql",
]

TOLERANCE = 0.05  # allowed delta for float comparisons


def approx_eq(a, b):
    try:
        return abs(float(a) - float(b)) <= TOLERANCE
    except (TypeError, ValueError):
        return str(a).strip() == str(b).strip()


def run_query(con, sql_path):
    with open(sql_path, "r", encoding="utf-8") as f:
        sql = f.read()
    try:
        cur = con.execute(sql)
        return cur.fetchall(), None
    except Exception as e:
        return None, str(e)


# ─────────────────────────────────────────────────────────
# Expected results (ground truth computed from seed data)
# ─────────────────────────────────────────────────────────

def check_A1(rows):
    issues = []
    if not rows:
        return ["No rows returned"]
    # Must have 6 columns
    if len(rows[0]) != 6:
        issues.append(f"Expected 6 columns, got {len(rows[0])}")
    # Row count: 1019 order_items total (including orphan), all should appear
    if len(rows) < 1000:
        issues.append(f"Too few rows: {len(rows)} (expected ~1018)")
    # First row when ordered by order_id, product_name
    # order 1 products: Gourde inox, Jean slim, Tapis yoga
    first = rows[0]
    if str(first[0]) != "1":
        issues.append(f"First order_id should be 1, got {first[0]}")
    if not approx_eq(first[5], round(first[3] * first[4], 2)):
        issues.append(f"line_total mismatch: qty={first[3]} * price={first[4]} != {first[5]}")
    return issues


def check_A2(rows):
    expected = {
        "Nord": 189451.36,
        "Centre": 28083.37,
        "Est": 20361.02,
        "Sud": 16743.09,
        "Ouest": 6578.87,
    }
    issues = []
    if len(rows) != 5:
        issues.append(f"Expected 5 regions, got {len(rows)}")
    result = {str(r[0]): float(r[1]) for r in rows}
    for region, ca in expected.items():
        if region not in result:
            issues.append(f"Missing region: {region}")
        elif not approx_eq(result[region], ca):
            issues.append(f"{region}: expected {ca}, got {result[region]}")
    # Must be ordered DESC by ca
    cas = [float(r[1]) for r in rows]
    if cas != sorted(cas, reverse=True):
        issues.append("Results not ordered by ca DESC")
    return issues


def check_A6(rows):
    issues = []
    # After dedup: 80 unique names (81 total - 1 duplicate Client_001)
    if len(rows) != 80:
        issues.append(f"Expected 80 rows after dedup, got {len(rows)}")
    ids = [r[0] for r in rows]
    if ids != sorted(ids):
        issues.append("Results not ordered by id ASC")
    # Client_001 should appear exactly once with id=1 (not 9998)
    client001_rows = [r for r in rows if str(r[1]) == "Client_001"]
    if len(client001_rows) != 1:
        issues.append(f"Client_001 appears {len(client001_rows)} times, expected 1")
    elif str(client001_rows[0][0]) != "1":
        issues.append(f"Client_001 kept id={client001_rows[0][0]}, expected 1 (MIN id)")
    return issues


def check_B1(rows):
    issues = []
    if not rows:
        return ["No rows returned"]
    if len(rows[0]) != 3:
        issues.append(f"Expected 3 columns (id, name, nb_orders), got {len(rows[0])}")
    # All returned customers must have nb_orders > 3
    for r in rows:
        if int(r[2]) <= 3:
            issues.append(f"Customer {r[1]} has nb_orders={r[2]} which is not > 3")
    # Client_032 should be first (11 orders)
    if str(rows[0][1]) != "Client_032":
        issues.append(f"Top customer should be Client_032, got {rows[0][1]}")
    if int(rows[0][2]) != 11:
        issues.append(f"Client_032 should have 11 orders, got {rows[0][2]}")
    return issues


def check_B2(rows):
    issues = []
    if not rows:
        return ["No rows returned"]
    if len(rows[0]) != 3:
        issues.append(f"Expected 3 columns, got {len(rows[0])}")
    # Top pair: Casque BT + Chocolat noir, 17 co-occurrences
    top = rows[0]
    pair = tuple(sorted([str(top[0]), str(top[1])]))
    expected_pair = ("Casque BT", "Chocolat noir")
    if pair != expected_pair:
        issues.append(f"Top pair should be {expected_pair}, got {pair}")
    if int(top[2]) != 17:
        issues.append(f"Top pair co-occurrences should be 17, got {top[2]}")
    # No duplicate pairs (A,B) and (B,A) should both appear
    pairs_seen = set()
    for r in rows:
        pair = frozenset([str(r[0]), str(r[1])])
        if str(r[0]) == str(r[1]):
            issues.append(f"Self-pair detected: '{r[0]}'")
        if pair in pairs_seen:
            issues.append(f"Duplicate pair detected: '{r[0]}' / '{r[1]}'")
            break
        pairs_seen.add(pair)
    return issues


def check_B3(rows):
    issues = []
    if not rows:
        return ["No rows returned"]
    expected_ids = {"1", "4", "11", "12", "24"}
    returned_ids = {str(r[0]) for r in rows}
    missing = expected_ids - returned_ids
    if missing:
        issues.append(f"Missing expected customer ids: {missing}")
    ids = [r[0] for r in rows]
    if ids != sorted(ids):
        issues.append("Results not ordered by id ASC")
    return issues


def check_B4(rows):
    issues = []
    expected = [
        ("Alimentation", "Café 1kg", 3177.88, 1),
        ("Électronique", "Smartphone X", 305205.63, 1),
        ("Sport", "Vélo route", 194397.84, 1),
        ("Vêtements", "Veste hiver", 24698.10, 1),
        ("Maison", "Lampe bureau", 8797.80, 1),
    ]
    result_map = {(str(r[0]), str(r[1])): (float(r[2]), int(r[3])) for r in rows}
    for cat, prod, rev, rnk in expected:
        key = (cat, prod)
        if key not in result_map:
            issues.append(f"Missing: {cat} / {prod}")
        else:
            got_rev, got_rnk = result_map[key]
            if not approx_eq(got_rev, rev):
                issues.append(f"{prod}: expected revenue {rev}, got {got_rev}")
            if got_rnk != rnk:
                issues.append(f"{prod}: expected rank 1, got {got_rnk}")
    # Électronique should have exactly 3 rows ranked 1-3
    elec_rows = [r for r in rows if str(r[0]) == "Électronique"]
    if len(elec_rows) != 3:
        issues.append(f"Électronique should have 3 rows, got {len(elec_rows)}")
    return issues


def check_B5(rows):
    issues = []
    if not rows:
        return ["No rows returned"]
    if len(rows[0]) != 4:
        issues.append(f"Expected 4 columns, got {len(rows[0])}")
    result = {str(r[0]): (int(r[1]), int(r[2]), float(r[3])) for r in rows}
    expected_spot_checks = {
        "2023-01": (12, 0, 0.0),
        "2023-03": (13, 4, 30.8),
        "2024-06": (7, 4, 57.1),
        "2024-12": (10, 0, 0.0),
    }
    for month, (active, retained, pct) in expected_spot_checks.items():
        if month not in result:
            issues.append(f"Missing month {month}")
            continue
        got_active, got_retained, got_pct = result[month]
        if got_active != active:
            issues.append(f"{month}: active {got_active} != {active}")
        if got_retained != retained:
            issues.append(f"{month}: retained {got_retained} != {retained}")
        if not approx_eq(got_pct, pct):
            issues.append(f"{month}: retention_pct {got_pct} != {pct}")
    months = [str(r[0]) for r in rows]
    if months != sorted(months):
        issues.append("Results not ordered by month ASC")
    return issues


def check_C1(rows):
    issues = []
    expected_ids = {"1", "2", "3", "4"}
    returned_ids = {str(r[0]) for r in rows}
    missing = expected_ids - returned_ids
    extra = returned_ids - expected_ids
    if missing:
        issues.append(f"Missed malformed emails for ids: {missing}")
    if extra:
        issues.append(f"False positives (valid emails flagged): ids {extra}")
    ids = [r[0] for r in rows]
    if ids != sorted(ids):
        issues.append("Results not ordered by id ASC")
    return issues


def check_C2(rows):
    issues = []
    if not rows:
        return ["No rows returned"]
    # The only anomaly is order_item id=42, unit_price=34999.5
    ids = {str(r[0]) for r in rows}
    if "42" not in ids:
        issues.append("Anomalous order_item id=42 (unit_price=34999.5) not detected")
    for r in rows:
        if float(r[3]) < 1000:
            issues.append(f"False positive: id={r[0]} with unit_price={r[3]} flagged as anomaly")
    return issues


def check_C3(rows):
    issues = []
    expected = {
        "orphan_order_items": 1,
        "duplicate_customers": 1,
        "null_emails": 0,
    }
    result = {str(r[0]): int(r[1]) for r in rows}
    for issue_name, count in expected.items():
        if issue_name not in result:
            issues.append(f"Missing issue row: {issue_name}")
        elif result[issue_name] != count:
            issues.append(f"{issue_name}: expected {count}, got {result[issue_name]}")
    issue_names = [str(r[0]) for r in rows]
    if issue_names != sorted(issue_names):
        issues.append("Results not ordered by issue ASC")
    return issues


CHECKS = {
    "A1_join.sql": ("A1 — JOIN multi-tables", check_A1),
    "A2_aggregation.sql": ("A2 — Agrégation par région", check_A2),
    "A6_dedup.sql": ("A6 — Déduplication clients", check_A6),
    "B1_no_december.sql": ("B1 — Clients sans décembre", check_B1),
    "B2_bought_together.sql": ("B2 — Produits achetés ensemble", check_B2),
    "B3_churned.sql": ("B3 — Clients perdus 2023→2024", check_B3),
    "B4_top3_by_category.sql": ("B4 — Top 3 par catégorie", check_B4),
    "B5_retention.sql": ("B5 — Rétention mensuelle", check_B5),
    "C1_bad_emails.sql": ("C1 — Emails malformés", check_C1),
    "C2_anomalies.sql": ("C2 — Anomalies de montant", check_C2),
    "C3_integrity.sql": ("C3 — Intégrité base", check_C3),
}


def main():
    print("=" * 60)
    print("Challenge 9 Validation: SQL Queries")
    print("=" * 60)

    if not os.path.exists(DB_PATH):
        print(f"\nFATAL: database not found at {DB_PATH}")
        sys.exit(1)

    con = sqlite3.connect(DB_PATH)
    all_issues = []

    for filename in QUERY_FILES:
        label, check_fn = CHECKS[filename]
        sql_path = os.path.join(QUERIES_DIR, filename)

        if not os.path.exists(sql_path):
            print(f"\n[FAIL] {label}")
            print(f"  - MISSING: {sql_path}")
            all_issues.append(f"Missing {filename}")
            continue

        rows, error = run_query(con, sql_path)
        if error:
            print(f"\n[FAIL] {label}")
            print(f"  - SQL ERROR: {error}")
            all_issues.append(f"{filename}: SQL error")
            continue

        issues = check_fn(rows)
        status = "PASS" if not issues else "FAIL"
        print(f"\n[{status}] {label}")
        for issue in issues:
            print(f"  - {issue}")
        all_issues.extend(issues)

    con.close()

    print("\n" + "=" * 60)
    if all_issues:
        print(f"RESULT: FAIL ({len(all_issues)} issues found)")
        sys.exit(1)
    else:
        print("RESULT: ALL CHECKS PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
