#!/bin/bash
# =============================================================================
# AI Agent Benchmark Runner
# =============================================================================
#
# CE QUE FAIT CE SCRIPT :
# Automatise le lancement d'un challenge et sa validation.
# Il checkout la bonne branche, lance la commande de l'agent IA,
# puis exécute le script de validation pour vérifier le résultat.
#
# USAGE :
#   ./run_benchmark.sh <numéro_challenge> [commande_agent]
#
# EXEMPLES :
#   ./run_benchmark.sh 2                        # Juste voir les consignes
#   ./run_benchmark.sh 2 "claude-code solve"    # Lancer un agent IA dessus
#   ./run_benchmark.sh all "mon_agent.sh"       # Lancer tous les challenges
# =============================================================================

set -e  # Arrêter le script à la première erreur

# --- Argument 1 : numéro du challenge (1-5 ou "all") ---
CHALLENGE=$1

# --- Argument 2 : commande pour lancer l'agent IA (optionnel) ---
# Si pas fourni, affiche juste un message
AGENT_CMD=${2:-"echo 'No agent command provided'"}

# --- Couleurs pour l'affichage dans le terminal ---
RED='\033[0;31m'      # Rouge = échec
GREEN='\033[0;32m'    # Vert = succès
YELLOW='\033[1;33m'   # Jaune = en cours
NC='\033[0m'          # Reset couleur (No Color)

echo "=========================================="
echo " AI Agent Benchmark"
echo "=========================================="

# =============================================================================
# FONCTION : run_challenge
# Lance un challenge complet : checkout branche → agent → validation
#
# Paramètres :
#   $1 = numéro du challenge (ex: 2)
#   $2 = nom de la branche git (ex: "challenge/hardcoded-creds")
#   $3 = chemin du script de validation (ex: "validate_challenge2.py")
# =============================================================================
run_challenge() {
    local num=$1
    local branch=$2
    local validator=$3

    echo -e "\n${YELLOW}Challenge $num: Starting...${NC}"
    echo "Branch: $branch"

    # --- Étape 1 : Se placer sur la branche du challenge ---
    # Le 2>/dev/null masque les messages de git checkout
    git checkout "$branch" 2>/dev/null

    # --- Étape 2 : Chronomètre - début ---
    # date +%s = timestamp Unix en secondes (pour mesurer la durée)
    local start_time=$(date +%s)

    # --- Étape 3 : Lancer l'agent IA ---
    # eval exécute la commande passée en string
    # C'est ici que l'agent IA fait son travail (modifier les fichiers, etc.)
    echo "Running agent..."
    eval "$AGENT_CMD"

    # --- Étape 4 : Chronomètre - fin ---
    local end_time=$(date +%s)
    local elapsed=$((end_time - start_time))  # Durée en secondes

    # --- Étape 5 : Valider le résultat ---
    # Le script Python retourne exit code 0 (succès) ou 1 (échec)
    echo -e "\nRunning validation..."
    if python3 "$validator" 2>&1; then
        echo -e "${GREEN}Challenge $num: PASSED (${elapsed}s)${NC}"
        return 0
    else
        echo -e "${RED}Challenge $num: FAILED (${elapsed}s)${NC}"
        return 1
    fi
}

# =============================================================================
# DISPATCH : quel challenge lancer selon l'argument $1
# =============================================================================
case $CHALLENGE in
    1)
        # Le challenge 1 (merge conflict) est spécial : il faut merger
        # deux branches manuellement, pas juste checkout une branche
        echo "Challenge 1: Merge Conflict Resolution"
        echo "Manual setup required:"
        echo "  git merge feature/update-config feature/refactor-config"
        echo "  Then let the agent resolve conflicts"
        ;;
    2)
        run_challenge 2 "challenge/hardcoded-creds" "validate_challenge2.py"
        ;;
    3)
        run_challenge 3 "challenge/monolith-pipeline" "validate_challenge3.py"
        ;;
    4)
        run_challenge 4 "challenge/add-checkpointing" "validate_challenge4.py"
        ;;
    5)
        run_challenge 5 "challenge/data-quality" "validate_challenge5.py"
        ;;
    all)
        # --- Mode "all" : lance les challenges 2 à 5 en séquence ---
        # (Le challenge 1 est exclu car il nécessite un setup manuel)
        echo "Running all challenges (2-5)..."
        passed=0
        failed=0
        for i in 2 3 4 5; do
            # Tableaux avec les branches et validateurs pour chaque challenge
            # L'index 0 est vide car les challenges commencent à 1
            branches=("" "challenge/hardcoded-creds" "challenge/monolith-pipeline" "challenge/add-checkpointing" "challenge/data-quality")
            validators=("" "validate_challenge2.py" "validate_challenge3.py" "validate_challenge4.py" "validate_challenge5.py")
            if run_challenge $i "${branches[$((i-1))]}" "${validators[$((i-1))]}"; then
                ((passed++))
            else
                ((failed++))
            fi
        done
        # --- Résumé final ---
        echo -e "\n=========================================="
        echo -e "Results: ${GREEN}$passed passed${NC}, ${RED}$failed failed${NC}"
        echo "=========================================="
        ;;
    *)
        # --- Message d'aide si argument invalide ---
        echo "Usage: $0 <1|2|3|4|5|all> [agent_command]"
        echo ""
        echo "Challenges:"
        echo "  1 - Merge Conflict Resolution"
        echo "  2 - Replace Hardcoded Credentials"
        echo "  3 - Refactor Monolith Pipeline"
        echo "  4 - Add Checkpointing System"
        echo "  5 - Data Quality Module"
        echo "  all - Run challenges 2-5"
        ;;
esac
