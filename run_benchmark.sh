#!/bin/bash
# AI Agent Benchmark Runner
# Usage: ./run_benchmark.sh <challenge_number> [agent_command]

set -e

CHALLENGE=$1
AGENT_CMD=${2:-"echo 'No agent command provided'"}

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo " AI Agent Benchmark"
echo "=========================================="

run_challenge() {
    local num=$1
    local branch=$2
    local validator=$3

    echo -e "\n${YELLOW}Challenge $num: Starting...${NC}"
    echo "Branch: $branch"

    # Checkout the challenge branch
    git checkout "$branch" 2>/dev/null

    # Record start time
    local start_time=$(date +%s)

    # Run the agent (user provides the command)
    echo "Running agent..."
    eval "$AGENT_CMD"

    # Record end time
    local end_time=$(date +%s)
    local elapsed=$((end_time - start_time))

    # Run validation
    echo -e "\nRunning validation..."
    if python3 "$validator" 2>&1; then
        echo -e "${GREEN}Challenge $num: PASSED (${elapsed}s)${NC}"
        return 0
    else
        echo -e "${RED}Challenge $num: FAILED (${elapsed}s)${NC}"
        return 1
    fi
}

case $CHALLENGE in
    1)
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
        echo "Running all challenges (2-5)..."
        passed=0
        failed=0
        for i in 2 3 4 5; do
            branches=("" "challenge/hardcoded-creds" "challenge/monolith-pipeline" "challenge/add-checkpointing" "challenge/data-quality")
            validators=("" "validate_challenge2.py" "validate_challenge3.py" "validate_challenge4.py" "validate_challenge5.py")
            if run_challenge $i "${branches[$((i-1))]}" "${validators[$((i-1))]}"; then
                ((passed++))
            else
                ((failed++))
            fi
        done
        echo -e "\n=========================================="
        echo -e "Results: ${GREEN}$passed passed${NC}, ${RED}$failed failed${NC}"
        echo "=========================================="
        ;;
    *)
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
