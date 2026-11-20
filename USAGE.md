# Agent 24 usage

Create a Python 3.12+ environment and install requirements-app.txt. Copy config/settings.example.json to config/settings.json. Configure local Qwen and d1 services, llama.cpp/model/projector paths and your private local key file. Models and runtimes are separate downloads under their own licenses.

Run python launch.py and open http://127.0.0.1:7884. Use only targets you own or have explicit authorization to assess. Start with a narrowly scoped local test target. Configure request budgets, hostname boundary and rate limits before starting. Pause or stop jobs through the UI. scripts/stop.py stops the app's own processes.

This release includes enabled assessment adapters and 72 original draft workflows, not the private research workspace or upstream skill collections. Draft guidance is not a verified exploit implementation. The optional practice target list starts empty. Reports and assessment state are generated locally and ignored by Git.

Install requirements-dev.txt and run python -m pytest tests -q for controlled local tests. Read RELEASE_REVIEW.md and TOOL_COVERAGE.md for verified checks and limits.
