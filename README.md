<div align="center">

# Agent 24

### Local AI-assisted security assessment workspace

![Source release](https://img.shields.io/badge/release-source-2563eb?style=flat-square)
![Local first](https://img.shields.io/badge/design-local--first-0f766e?style=flat-square)

**Coded by [zaid.dev](https://github.com/gamerock587)** · **invnty**

Python · FastAPI · Local models

</div>

---

## What it does

- Bounded assessments with explicit target scope
- Evidence capture and local reports
- Pause, resume and resource-aware workers

## Quick start

**Requirements:** Python 3.12+, local Qwen service and a compatible d1/llama.cpp runtime.

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-app.txt
copy config/settings.example.json config/settings.json
python launch.py
```

## Before you run

This release contains the application, not the separately licensed research collections, model weights or llama.cpp binaries. Configure model paths before use. Test only systems you own or are authorized to assess.

## Documentation

See [USAGE.md](USAGE.md) for the original detailed operating guide.

## Privacy and configuration

This source export excludes local credentials, databases, sessions, logs, recordings,
personal spreadsheets and compiled distributions. Supply your own configuration.
The ignore rules help prevent accidental commits; they do not replace reviewing files.

## Contributing

Describe the problem, include reproducible steps with synthetic data, and keep changes focused.
Never include tokens, private recordings, customer data or personal contact lists in an issue.
Validation and remaining limitations are recorded in [RELEASE_REVIEW.md](RELEASE_REVIEW.md).

## License and attribution

Original application code is licensed under [MIT](LICENSE). Third-party components retain
their own licenses and authorship; see THIRD-PARTY-NOTICES.md and any bundled license files.

The 72 original draft workflows are included with their source references. External upstream skill collections and practice target lists are intentionally not bundled. Workflows are guidance, not independently certified security assessments.
