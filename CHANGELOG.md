# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Open-source governance assets: `CODE_OF_CONDUCT.md`, `CHANGELOG.md`,
  `AUTHORS.md`, and GitHub Actions CI workflows.
- Bilingual (中文 / English) `README.md` with a friendly open-source presentation.
- Standalone Chinese README (`README.zh-CN.md`) for better zh-CN discoverability.
- Embedded social-preview banner + Star History chart + Support section in `README.md`.
- Strengthened `.gitignore` to keep personal/sensitive data out of the repo.

### Changed
- Brand unified to **DawnForge** (`reasonix` → `DawnForge`) across code, docs,
  skills, and memory; technical paths (`reasonix_sentou`, `reasonix.toml`) preserved.
- Removed sensitive/historical artifacts (CTF exam data, personal walkthroughs,
  internal research) from the public repository.
- Swapped the visitor counter badge to the more reliable `hits.sh` service.
- `scripts/download-tools.ps1` rewritten to use the native GitHub API instead of
  the `gh` CLI (no `gh` install required), with optional `GITHUB_TOKEN` support
  to avoid rate-limiting and a fix for the `Test-Path` skip-check bug.

### Removed
- `ctf_exam_web01/`, `解题思路/`, `vulnclaw-research/`, `vulnclaw-vs-reasonix/`,
  and internal experiment docs (see `.gitignore` / git history note).

---

## [0.1.0] - 2026-08-06

### Added
- Evidence-enforced anti-hallucination loop (`scripts/evidence_pack/`):
  `harvest → archive → report`, with per-conclusion `EVID` ids and
  character-by-character verification.
- Multi-agent persona and skill library serving Claude Code / Codex / OpenCode /
  Cline / Trae via `AGENTS.md` + `skills/pentest_skills/`.
- Experience system: `memory/pentest-experience-NNN.md`, `memory/attack-chains.yaml`,
  `memory/cost-stats.csv`, and indexing via `scripts/exp-add.py`.
- Local training ranges (`targets/`): DVWA / Juice Shop / WebGoat / VAmPI with an
  8-week learning path.
- Orchestration & health tooling: `scripts/ai-pentest-orchestrator.py`,
  `scripts/format-results.py`, `scripts/check-scope.py`, `scripts/health-check.py`.
- Security boundaries: authorization whitelist check, three combat modes
  (`safe / normal / aggressive`), `.gov`/`.mil` and cloud-metadata blocking.

---