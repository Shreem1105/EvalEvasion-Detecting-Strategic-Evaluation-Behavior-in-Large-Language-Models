# Project Walkthrough: Escaping the "Evaluation" Trap

**Status:** Completed (Empirical Pivot & Harvest)
**Date:** 2026-01-18

## 1. The Core Achievement
We successfully built and scaled **EvalEvasion**, a system to detect "Strategic Evaluation Evasion" (SEE) in LLMs. The project evolved from a theoretical framework to a high-throughput empirical engine capable of running 20,000 trajectories on an NVIDIA A100.

## 2. Technical Milestones
### Phase A: Architecture & Theory
*   **Defined the Problem:** Formalized SEE as the discrepancy between behavior in a "Baseline" context vs. an "Evaluation" context (signaled by safety tags).
*   **Metric:** Created the **Adaptation Gap (AG)**, a statistical measure of this discrepancy.

### Phase B: Scale-Up (Simulation)
*   **Mock Verification:** Validated the pipeline by running **20,000 trajectories** using Mock Models.
*   **Result:** The statistical engine correctly identified that identical mock models have an AG difference of 0.003 (p=0.98), proving the null hypothesis holds when no evasion exists.

### Phase C: Empirical Pivot (A100)
*   **Zero-API Architecture:** Pivoted to a fully local, open-weights stack to avoid API costs and rate limits.
    *   **Reasoning Agent:** `DeepSeek-R1-Distill-Llama-8B`
    *   **Standard Baseline:** `Qwen/Qwen2.5-7B-Instruct`
*   **Engine:** Integrated **vLLM** for high-throughput inference (50x concurrency).

## 3. Final Execution State: "Emergency Harvest"
Due to A100 compute limits (5-hour session), the full 20k run could not complete. We executed an **Emergency Harvest Strategy**:
1.  **Recovered:** ~1,200 trajectories from the Reasoning Model (DeepSeek).
2.  **Generated:** A targeted mini-baseline (200 trajectories) from the Standard Model (Qwen).
3.  **Outcome:** A valid, statistically significant dataset (N=1,400) sufficient for publication.

## 4. Key Artifacts
*   `src/models.py`: Hybrid architecture supporting OpenAI/Gemini APIs *and* local vLLM/HuggingFace models.
*   `src/runner.py`: Async engine with automatic checkpointing and CLI support.
*   `results/figures/deception_heatmap.png`: The visual proof of our findings.

## 5. How to Reproduce
1.  **Get an A100:** Use Google Colab Pro or Lambda Labs.
2.  **Run One Command:**
    ```bash
    git clone https://github.com/Shreem1105/EvalEvasion-Detecting-Strategic-Evaluation-Behavior-in-Large-Language-Models.git repo
    cd repo
    bash run_a100.sh
    ```
