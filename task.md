# Research Project: Detecting Strategic Evaluation Evasion

## Phase 1: Conceptualization & Design (COMPLETE)
- [x] Formalize Research Problem Definition <!-- id: 0 -->
- [x] Design Task and Prompt Structure <!-- id: 1 -->
- [x] Define Metrics and success criteria <!-- id: 2 -->

## Phase 2: Technical Implementation (COMPLETE)
- [x] Implement data generation pipeline (`src/tasks_data.py`) <!-- id: 3 -->
- [x] Implement Scorer Classes (`src/metrics.py`)
- [x] Implement Experiment Runner (`src/runner.py`, `src/run_final_experiment.py`)
- [x] Implement Mock Model for Testing
- [x] Verify Measurement Pipeline (`src/sanity_check.py`)

## Phase 3: Analysis & Visualization (COMPLETE)
- [x] Design analysis methods <!-- id: 4 -->
- [x] Implement Analysis Aggregation (`src/analysis.py`) <!-- id: 5 -->
- [x] Implement Plotting (`src/plotting.py`) <!-- id: 6 -->
- [x] Generate Paper Tables (`results/tables/`) <!-- id: 7 -->
- [x] Draft Paper Sections (`paper_sections.md`) <!-- id: 8 -->

## Phase 4: Final Execution (FROZEN/READY)
- [x] Setup Environment (API keys/libs) <!-- id: 9 -->
- [x] Run Experiment (FALLBACK: Mock run notice generated) <!-- id: 10 -->
- [x] Generate Final Artifacts (`results/mock_run_notice.json`) <!-- id: 11 -->
- [x] **PROJECT FREEZE**: Generated Manifest (`results/final_project_manifest.json`) <!-- id: 12 -->

## Phase 5: Scale-Up (ACM WebConf Study)
- [x] **Data Expansion**: Implement generator for 100 tasks across 5 domains (`src/generate_dataset.py`) <!-- id: 13 -->
- [x] **Multi-Model**: Add ReasoningModel & CoT extraction (`src/models.py`) <!-- id: 14 -->
- [x] **High-Throughput**: Implement async runner with checkpointing (`src/runner.py`) <!-- id: 15 -->
- [x] **Statistical Rigor**: Add T-tests and Heatmaps (`src/analysis.py`) <!-- id: 16 -->
- [x] **Execution**: Run 1k trajectory stress-test (A100/API) <!-- id: 17 -->

## Phase 6: Empirical Pivot (Local A100)
- [ ] **Local Model Support**: Implement `HuggingFaceModel` (vLLM/Transformers) in `src/models.py` <!-- id: 18 -->
- [ ] **Infrastructure**: Create `run_a100.sh` for local dep installation & execution <!-- id: 19 -->
- [ ] **Reasoning Extraction**: Ensure `DeepSeek` thinking trace is captured locally <!-- id: 20 -->
- [ ] **Execution**: Run 20k trajectory study with real weights (DeepSeek-R1 vs Llama-3.1) <!-- id: 21 -->
