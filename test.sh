#!/usr/bin/env bash
# test.sh — Run all tests (backend + frontend unit + frontend E2E) with coverage.
#
# Usage:
#   ./test.sh            Run everything, print combined summary
#   ./test.sh backend    Backend only
#   ./test.sh unit       Frontend unit tests only
#   ./test.sh e2e        Frontend E2E tests only

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COVERAGE_DIR="$SCRIPT_DIR/coverage"

RED='\033[0;31m'
GREEN='\033[0;32m'
BOLD='\033[1m'
DIM='\033[2m'
RESET='\033[0m'

header() { echo -e "\n${BOLD}── $1 ──${RESET}\n"; }
ok()     { echo -e "${GREEN}✓ $1${RESET}"; }
fail()   { echo -e "${RED}✗ $1${RESET}"; }

TARGETS="${1:-all}"
FAILED=0

rm -rf "$COVERAGE_DIR"
mkdir -p "$COVERAGE_DIR"

# ── Backend (pytest + pytest-cov) ──────────────────────────────────────────

run_backend() {
    header "Backend · pytest"
    (
        cd "$SCRIPT_DIR/backend"
        uv run pytest \
            --cov=evinha \
            --cov-report=term \
            --cov-report=json:"$COVERAGE_DIR/backend.json" \
            -q
    ) && ok "Backend tests passed" || { fail "Backend tests failed"; FAILED=1; }
}

# ── Frontend unit (vitest + v8) ────────────────────────────────────────────

run_unit() {
    header "Frontend · vitest"
    (
        cd "$SCRIPT_DIR/frontend"
        npx vitest run --coverage
    ) && ok "Frontend unit tests passed" || { fail "Frontend unit tests failed"; FAILED=1; }

    # Copy vitest coverage to shared dir
    if [ -f "$SCRIPT_DIR/frontend/coverage/unit/coverage-final.json" ]; then
        cp "$SCRIPT_DIR/frontend/coverage/unit/coverage-final.json" \
           "$COVERAGE_DIR/frontend-unit.json"
    fi
}

# ── Frontend E2E (playwright + istanbul) ───────────────────────────────────

run_e2e() {
    header "Frontend · playwright"

    # Kill any lingering dev server
    lsof -ti:5173 | xargs kill 2>/dev/null || true

    (
        cd "$SCRIPT_DIR/frontend"
        npx playwright test
    ) && ok "Frontend E2E tests passed" || { fail "Frontend E2E tests failed"; FAILED=1; }

    # Copy E2E coverage to shared dir
    if [ -d "$SCRIPT_DIR/frontend/coverage/e2e" ]; then
        for f in "$SCRIPT_DIR/frontend/coverage/e2e"/*.json; do
            cp "$f" "$COVERAGE_DIR/frontend-e2e-$(basename "$f")"
        done
    fi
}

# ── Merge & report ─────────────────────────────────────────────────────────

report() {
    header "Coverage summary"

    # Frontend merge (unit + E2E → Istanbul format)
    if [ -f "$COVERAGE_DIR/frontend-unit.json" ] || ls "$COVERAGE_DIR"/frontend-e2e-*.json &>/dev/null; then
        (cd "$SCRIPT_DIR/frontend" && node scripts/merge-coverage.mjs)
        echo -e "${BOLD}Frontend (unit + E2E combined):${RESET}"
        (cd "$SCRIPT_DIR/frontend" && npx nyc report \
            --temp-dir coverage/merged \
            --report-dir coverage/report \
            -r text -r html)
        echo -e "${DIM}HTML report → frontend/coverage/report/index.html${RESET}"
    fi

    echo ""

    # Backend report
    if [ -f "$COVERAGE_DIR/backend.json" ]; then
        echo -e "${BOLD}Backend:${RESET}"
        (cd "$SCRIPT_DIR/backend" && uv run python -m coverage json \
            -o /dev/null --quiet 2>/dev/null || true)
        # The pytest-cov text report was already printed above
        echo -e "${DIM}JSON report → coverage/backend.json${RESET}"
    fi
}

# ── Run selected targets ──────────────────────────────────────────────────

case "$TARGETS" in
    all)
        run_backend
        run_unit
        run_e2e
        report
        ;;
    backend)  run_backend ;;
    unit)     run_unit ;;
    e2e)      run_e2e ;;
    *)
        echo "Usage: $0 [all|backend|unit|e2e]"
        exit 1
        ;;
esac

if [ "$FAILED" -ne 0 ]; then
    echo -e "\n${RED}${BOLD}Some tests failed.${RESET}"
    exit 1
else
    echo -e "\n${GREEN}${BOLD}All tests passed.${RESET}"
fi
