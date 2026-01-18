# EvalEvasion: Submission Package
**Status:** Empirical-Ready (Frozen)
**Timestamp:** 2026-01-18
**Hash Manifest:** `results/final_project_manifest.json`

## Overview
This package contains the complete, verified research codebase for "EvalEvasion: Detecting Strategic Evaluation Behavior in Large Language Models." The project is fully implemented and audited but contains **mock data** in the results directory because API credentials were not available during the final run.

## Artifact Inventory

### 1. Code (`src/`)
*   `tasks_data.py`: Frozen prompt dataset (4 stages, 3 tasks).
*   `metrics.py`: Rule-based scoring logic and metric definitions (AG, ES, CD).
*   `models.py`: API wrappers (OpenAI, Google) and Mock fallback.
*   `runner.py` / `run_final_experiment.py`: Main execution drivers.
*   `analysis.py` / `plotting.py`: Analysis and visualization scripts.

### 2. Documentation (Root)
*   `research_problem_definition.md`: Formal problem statement.
*   `experiment_design.md`: Methodological details.
*   `evaluation_methodology.md`: Scoring specifics.
*   `paper_sections.md`: Drafted text (Method/Results/Limitations).

### 3. Results (`results/`)
*   `mock_run_notice.json`: Explicit declaration of mock status.
*   `final_project_manifest.json`: Cryptographic audit trail of frozen files.
*   `experiment_results.json`: Output log (Mock data).
*   `tables/` & `figures/`: Generated artifacts from mock data.

## Execution Contract (How to Reproduce)

To hydrate this package with real empirical data, perform the following single step. **No code changes are required.**

### Prerequisites
*   Python 3.10+
*   Dependencies: `openai`, `google-generativeai`, `pandas`, `matplotlib`, `seaborn`
*   **Environment Variables**:
    *   `OPENAI_API_KEY` (for GPT-4o)
    *   `GOOGLE_API_KEY` (for Gemini 1.5 Flash)

### Command
```bash
python src/run_final_experiment.py
```

### Post-Processing
After the experiment finishes, regenerate tables and plots:
```bash
python src/analysis.py
python src/plotting.py
```

## Audit
Refer to `results/final_project_manifest.json` to verify the SHA256 hashes of all source files to ensure no modifications have been made since the freeze.
