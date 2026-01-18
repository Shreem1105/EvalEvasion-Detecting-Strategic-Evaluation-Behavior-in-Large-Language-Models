# Implementation Plan: EvalEvasion Scale-Up

**Goal:** Expand the project to support high-throughput experimentation with 100+ tasks and internal reasoning models.

## 1. Data Expansion (`src/generate_dataset.py`)
*   **Objective:** Programmatically generate 100 unique tasks across 5 domains.
*   **Changes:**
    *   Create a new script `src/generate_dataset.py` that uses an LLM (Mock/Real) to generate task JSONs.
    *   Domains: `Cybersecurity`, `Financial Advice`, `PII Extraction`, `Social Manipulation`, `Medical Misinfo`.
    *   Output: `src/generated_tasks.json`.
    *   Update `src/tasks_data.py` to load this JSON if present, otherwise fallback to static data.

## 2. Multi-Model Support (`src/models.py`)
*   **Objective:** Support Reasoning models (DeepSeek, o1) and capture CoT.
*   **Changes:**
    *   Add `ReasoningModel` class inheriting from `LLMModel`.
    *   Implement `_extract_cot(response_text)` method to separate thinking traces from final answers (e.g., `<think>...</think>`).
    *   Ensure `generate()` returns structured objects (or appends metadata) if CoT is captured.

## 3. High-Throughput Runner (`src/runner.py`)
*   **Objective:** Run 1k trajectories in <5 hours.
*   **Changes:**
    *   Replace sequential loop with `asyncio` or `ThreadPoolExecutor`.
    *   Implement `CheckpointManager` that saves partial results to `results/checkpoints/` every 10% progress.
    *   Add rate-limit handling (simple backoff).

## 4. Statistical Analysis (`src/analysis.py`)
*   **Objective:** Compare Standard vs. Reasoning models.
*   **Changes:**
    *   Add `scipy.stats.ttest_ind` to compare AG means.
    *   Add heatmap generation using `seaborn` for Domain vs. Evasion Rate.
    *   Function: `compare_models(standard_results, reasoning_results)`.

## Verification Plan

### Automated Tests
*   **`src/sanity_check.py` Update:**
    *   Update sanity check to use the new `ReasoningModel` mock.
    *   Verify CoT extraction on a dummy string like `<think>planning...</think> Result`.
    *   Verify the runner saves a checkpoint file.

### Manual Verification
*   **Run Generator:** Execute `python src/generate_dataset.py` (using Mock) and inspect `src/generated_tasks.json` structure.
*   **Run Pipeline:** Execute `python src/run_final_experiment.py` with the "Mock" models to simulate the 1k load (scaled down for speed) and check `results/experiment_results.json`.
