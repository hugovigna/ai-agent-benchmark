#!/bin/bash
# =============================================================================
# AI Agent Benchmark Runner
# =============================================================================
#
# CE QUE FAIT CE SCRIPT :
# Automatise le lancement d'un challenge et sa validation.
# Il checkout la bonne branche, lance l'agent IA (Claude par défaut),
# puis exécute le script de validation pour vérifier le résultat.
#
# USAGE :
#   ./run_benchmark.sh <numéro_challenge>                    # Avec Claude (défaut)
#   ./run_benchmark.sh <numéro_challenge> "autre_agent.sh"   # Avec un autre agent
#   ./run_benchmark.sh all                                   # Tous les challenges
#
# EXEMPLES :
#   ./run_benchmark.sh 2                          # Challenge 2 avec Claude
#   ./run_benchmark.sh all                        # Tous les challenges avec Claude
#   ./run_benchmark.sh 3 "aider --message 'Lis TASK.md et résous le challenge'"
#   ./run_benchmark.sh 5 "copilot-cli solve"
#
# PRÉREQUIS :
#   - Claude CLI installé (brew install claude ou npm install -g @anthropic-ai/claude-code)
#   - Être dans le repo git_test
#   - Pas de session Claude interactive ouverte (sinon conflit)
# =============================================================================

set +e  # On ne quitte PAS à la première erreur (les validateurs retournent exit 1 = FAIL, c'est normal)

# --- Argument 1 : numéro du challenge (1-5 ou "all") ---
CHALLENGE=$1

# --- Argument 2 : commande pour lancer l'agent IA (optionnel) ---
# Par défaut : Claude en mode non-interactif avec auto-accept de tous les outils
DEFAULT_AGENT='claude -p "Lis TASK.md et résous le challenge décrit dedans. Modifie les fichiers nécessaires." --allowedTools "Edit,Write,Read,Glob,Grep,Bash"'
AGENT_CMD=${2:-$DEFAULT_AGENT}

# --- Répertoire racine du benchmark (chemin absolu) ---
BENCH_DIR="$(cd "$(dirname "$0")" && pwd)"

# --- Copie des scripts agent dans un dossier temp (ils disparaissent lors des git checkout) ---
AGENT_TMPDIR=$(mktemp -d)
cp "$BENCH_DIR/"*_agent.py "$AGENT_TMPDIR/" 2>/dev/null || true
trap "rm -rf '$AGENT_TMPDIR'" EXIT

# --- Couleurs pour l'affichage dans le terminal ---
RED='\033[0;31m'      # Rouge = échec
GREEN='\033[0;32m'    # Vert = succès
YELLOW='\033[1;33m'   # Jaune = en cours
BLUE='\033[0;34m'     # Bleu = info
NC='\033[0m'          # Reset couleur (No Color)

echo "=========================================="
echo " AI Agent Benchmark"
echo "=========================================="
echo -e "${BLUE}Agent: ${AGENT_CMD}${NC}"

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

    echo -e "\n${YELLOW}==========================================${NC}"
    echo -e "${YELLOW}Challenge $num: Starting...${NC}"
    echo "Branch: $branch"
    echo "Validator: $validator"
    echo -e "${YELLOW}==========================================${NC}"

    # --- Étape 1 : Se placer sur la branche du challenge ---
    git checkout "$branch" 2>/dev/null
    echo -e "${BLUE}On branch: $(git branch --show-current)${NC}"

    # Remplace les chemins relatifs *_agent.py dans la commande par leur chemin absolu
    local agent_cmd_resolved="$AGENT_CMD"
    for f in "$AGENT_TMPDIR/"*_agent.py; do
        [ -f "$f" ] || continue
        local base=$(basename "$f")
        agent_cmd_resolved="${agent_cmd_resolved//$base/$f}"
    done

    # --- Étape 2 : Chronomètre - début ---
    local start_time=$(date +%s)

    # --- Étape 3 : Lancer l'agent IA ---
    echo -e "\n${BLUE}Running agent...${NC}"
    eval "$agent_cmd_resolved"
    local agent_exit=$?

    # --- Étape 4 : Chronomètre - fin ---
    local end_time=$(date +%s)
    local elapsed=$((end_time - start_time))

    echo -e "\n${BLUE}Agent finished (exit code: $agent_exit, duration: ${elapsed}s)${NC}"

    # --- Étape 5 : Valider le résultat ---
    echo -e "\n${BLUE}Running validation...${NC}"
    local result=0
    if python3 "$validator" 2>&1; then
        echo -e "\n${GREEN}>>> Challenge $num: PASSED (${elapsed}s) <<<${NC}"
    else
        echo -e "\n${RED}>>> Challenge $num: FAILED (${elapsed}s) <<<${NC}"
        result=1
    fi

    # --- Étape 6 : Restaurer la branche à son état d'origine et revenir sur main ---
    git checkout -- . 2>/dev/null || true
    git clean -fd 2>/dev/null || true
    git checkout main 2>/dev/null
    return $result
}

# =============================================================================
# FONCTION : reset_branch
# Remet la branche dans son état initial avant de lancer l'agent.
# Important pour que chaque run parte d'un état propre.
# =============================================================================
reset_branch() {
    local branch=$1
    echo -e "${BLUE}Resetting branch $branch...${NC}"
    git checkout "$branch" 2>&1 || true
    git checkout -- . 2>&1 || true    # Annule les modifications non commitées
    git clean -fd 2>&1 || true        # Supprime les fichiers non trackés
    echo -e "${BLUE}Branch reset done.${NC}"
}

# =============================================================================
# DISPATCH : quel challenge lancer selon l'argument $1
# =============================================================================
case $CHALLENGE in
    1)
        # Le challenge 1 (merge conflict) est spécial : il faut merger
        # deux branches manuellement, pas juste checkout une branche
        echo "Challenge 1: Merge Conflict Resolution"
        echo ""
        echo "Ce challenge nécessite un setup manuel :"
        echo "  1. git checkout main"
        echo "  2. git merge feature/update-config    # OK, fast-forward"
        echo "  3. git merge feature/refactor-config   # CONFLIT ici"
        echo "  4. Lancer l'agent pour résoudre le conflit"
        echo ""
        echo "Ou en une commande :"
        echo "  git checkout main && git merge feature/update-config && git merge feature/refactor-config; claude -p 'Résous le conflit de merge dans config/settings.py. Garde les valeurs de production ET les nouvelles sections monitoring/alerting.'"
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
    6)
        run_challenge 6 "challenge/retrodoc" "validate_challenge6.py"
        ;;
    7)
        run_challenge 7 "challenge/mapping" "validate_challenge7.py"
        ;;
    8)
        run_challenge 8 "challenge/debugging" "validate_challenge8.py"
        ;;
    all)
        # --- Mode "all" : lance les challenges 2 à 8 en séquence ---
        echo "Running all challenges (2-8)..."
        echo ""
        passed=0
        failed=0
        total_start=$(date +%s)

        # Tableaux indexés par numéro de challenge
        branches=(
            ""                              # index 0 (inutilisé)
            ""                              # index 1 (challenge 1 = manuel)
            "challenge/hardcoded-creds"     # index 2
            "challenge/monolith-pipeline"   # index 3
            "challenge/add-checkpointing"   # index 4
            "challenge/data-quality"        # index 5
            "challenge/retrodoc"           # index 6
            "challenge/mapping"            # index 7
            "challenge/debugging"          # index 8
        )
        names=(
            ""                              # index 0
            ""                              # index 1
            "Hardcoded Credentials"         # index 2
            "Monolith Pipeline"             # index 3
            "Add Checkpointing"             # index 4
            "Data Quality"                  # index 5
            "Rétrodocumentation"            # index 6
            "Mapping Codebase"              # index 7
            "Debugging"                     # index 8
        )
        validators=(
            ""                              # index 0
            ""                              # index 1
            "validate_challenge2.py"        # index 2
            "validate_challenge3.py"        # index 3
            "validate_challenge4.py"        # index 4
            "validate_challenge5.py"        # index 5
            "validate_challenge6.py"        # index 6
            "validate_challenge7.py"        # index 7
            "validate_challenge8.py"        # index 8
        )

        declare -a scores=()
        total_passed=0
        total_checks=0
        for i in 2 3 4 5 6 7 8; do
            # Reset la branche pour un état propre avant chaque challenge
            reset_branch "${branches[$i]}"
            run_challenge $i "${branches[$i]}" "${validators[$i]}"
            scores[$i]=$(eval echo "\$CHALLENGE_SCORE_$i")
        done

        total_end=$(date +%s)
        total_elapsed=$((total_end - total_start))

        # --- Tableau récapitulatif ---
        echo -e "\n=========================================="
        echo " BENCHMARK RESULTS"
        echo "=========================================="
        printf "  %-4s %-24s %s\n" "#" "Challenge" "Score"
        echo "  ---- ------------------------ --------"
        for i in 2 3 4 5 6 7 8; do
            local score="${scores[$i]:-0/0}"
            local p="${score%%/*}"
            local t="${score##*/}"
            total_passed=$((total_passed + p))
            total_checks=$((total_checks + t))
            if [ "$p" = "$t" ] && [ "$t" != "0" ]; then
                local color="$GREEN"
            elif [ "$p" = "0" ]; then
                local color="$RED"
            else
                local color="$YELLOW"
            fi
            printf "  ${color}%-4s %-24s %s${NC}\n" "$i" "${names[$i]}" "$score"
        done
        echo "  ---- ------------------------ --------"
        printf "  %-4s %-24s %s\n" "" "TOTAL" "${total_passed}/${total_checks}"
        echo "=========================================="
        echo -e "  Duration: ${total_elapsed}s"
        echo "=========================================="

        # Retour sur main
        git checkout main 2>/dev/null
        ;;
    *)
        # --- Message d'aide si argument invalide ---
        echo "Usage: $0 <1|2|3|4|5|6|7|8|all> [agent_command]"
        echo ""
        echo "Challenges:"
        echo "  1   - Merge Conflict Resolution (setup manuel)"
        echo "  2   - Replace Hardcoded Credentials"
        echo "  3   - Refactor Monolith Pipeline"
        echo "  4   - Add Checkpointing System"
        echo "  5   - Data Quality Module"
        echo "  6   - Rétrodocumentation"
        echo "  7   - Mapping Codebase"
        echo "  8   - Debugging (4 bugs)"
        echo "  all - Run challenges 2-8 en séquence"
        echo ""
        echo "Exemples:"
        echo "  $0 2                    # Challenge 2 avec Claude (défaut)"
        echo "  $0 all                  # Tous avec Claude"
        echo '  $0 3 "aider --msg ..."  # Challenge 3 avec Aider'
        echo ""
        echo "Agent par défaut:"
        echo "  $DEFAULT_AGENT"
        ;;
esac
