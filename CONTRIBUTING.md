# Contributing to Personal Life OS

## Before you contribute
By submitting a pull request you agree that your contribution may be
included in both the open-source (AGPL v3) and commercial versions
of Personal Life OS. See CLA in `.github/`.

## Setup
```bash
cd backend && python -m venv .venv && .venv\Scripts\activate  # Windows
pip install -r requirements-dev.txt
cd ../frontend && npm install
```

## Submitting a PR
1. Fork the repo
2. Create a branch: `git checkout -b feature/your-feature`
3. Write tests for new logic
4. Run `pytest` and `npm test` — both must pass
5. Open a PR against `main`
