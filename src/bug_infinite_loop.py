"""
Bug 2 : Boucle infinie

Ce module implémente un système de retry avec backoff exponentiel
et un algorithme de convergence. Il contient des boucles qui ne
terminent jamais à cause de bugs dans les conditions de sortie.
"""

import time
import random


def fetch_with_retry(url, max_retries=5):
    """Simule un appel API avec retry.

    BUG: le compteur de retry n'est jamais incrémenté,
    donc la boucle ne termine jamais.
    """
    attempt = 0
    while attempt < max_retries:
        success = random.random() > 0.7  # 30% chance de succès
        if success:
            return {"status": "ok", "data": [1, 2, 3], "attempt": attempt}
        # BUG: on a oublié d'incrémenter attempt
        wait_time = min(2 ** attempt, 30)
        time.sleep(0.001)  # réduit pour les tests
    return {"status": "failed", "data": [], "attempt": attempt}


def find_convergence(initial_value, target, tolerance=0.01, max_iterations=1000):
    """Trouve une valeur qui converge vers la cible par ajustement itératif.

    BUG: la condition de sortie compare avec = au lieu de <=,
    et le pas d'ajustement change de signe à chaque itération,
    créant une oscillation infinie.
    """
    current = initial_value
    iteration = 0
    step = 0.1

    while iteration < max_iterations:
        diff = target - current
        if abs(diff) == tolerance:  # BUG: == au lieu de <=, n'atteindra jamais exactement
            break
        # BUG: step ne se réduit pas, et on alterne le signe → oscillation
        current = current + step * (1 if diff > 0 else -1)
        step = step * 1.01  # BUG: le pas GRANDIT au lieu de rétrécir
        iteration += 1

    return {"value": round(current, 4), "iterations": iteration, "converged": abs(target - current) <= tolerance}


def process_queue(items):
    """Traite une file d'attente d'éléments.

    BUG: quand un élément échoue, il est remis en queue
    sans limite, causant une boucle infinie si un élément
    échoue toujours.
    """
    queue = list(items)
    results = []
    processed_count = 0

    while queue:
        item = queue.pop(0)
        processed_count += 1

        if item % 3 == 0:
            # Simule un échec pour les multiples de 3
            queue.append(item)  # BUG: remet en queue sans limite → infini
        else:
            results.append(item * 2)

    return {"results": results, "processed": processed_count}


def run_all_tasks():
    """Point d'entrée — exécute toutes les tâches.
    Doit terminer en moins de 5 secondes.
    """
    # Task 1: fetch avec retry
    fetch_result = fetch_with_retry("https://api.example.com/data")

    # Task 2: convergence
    convergence_result = find_convergence(0.0, 1.0, tolerance=0.01)

    # Task 3: process queue
    queue_result = process_queue([1, 2, 3, 4, 5, 6, 7, 8, 9])

    return {
        "fetch": fetch_result,
        "convergence": convergence_result,
        "queue": queue_result,
    }
