"""Module de traitement avec retry, convergence et file d'attente."""

import time
import random


def fetch_with_retry(url, max_retries=5):
    """Simule un appel API avec retry."""
    attempt = 0
    while attempt < max_retries:
        success = random.random() > 0.7
        if success:
            return {"status": "ok", "data": [1, 2, 3], "attempt": attempt}
        wait_time = min(2 ** attempt, 30)
        time.sleep(0.001)
    return {"status": "failed", "data": [], "attempt": attempt}


def find_convergence(initial_value, target, tolerance=0.01, max_iterations=1000):
    """Trouve une valeur qui converge vers la cible par ajustement itératif."""
    current = initial_value
    iteration = 0
    step = 0.1

    while iteration < max_iterations:
        diff = target - current
        if abs(diff) == tolerance:
            break
        current = current + step * (1 if diff > 0 else -1)
        step = step * 1.01
        iteration += 1

    return {"value": round(current, 4), "iterations": iteration, "converged": abs(target - current) <= tolerance}


def process_queue(items):
    """Traite une file d'attente d'éléments."""
    queue = list(items)
    results = []
    processed_count = 0

    while queue:
        item = queue.pop(0)
        processed_count += 1

        if item % 3 == 0:
            queue.append(item)
        else:
            results.append(item * 2)

    return {"results": results, "processed": processed_count}


def run_all_tasks():
    """Point d'entrée — exécute toutes les tâches. Doit terminer en moins de 5 secondes."""
    fetch_result = fetch_with_retry("https://api.example.com/data")

    convergence_result = find_convergence(0.0, 1.0, tolerance=0.01)

    queue_result = process_queue([1, 2, 3, 4, 5, 6, 7, 8, 9])

    return {
        "fetch": fetch_result,
        "convergence": convergence_result,
        "queue": queue_result,
    }
