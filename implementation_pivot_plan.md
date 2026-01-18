# Implementation Plan: Phase 6 - Local A100 Inference

**Goal:** Replace Mock models with real Open-Weights models (`DeepSeek-R1-Distill-Llama-8B` and `Llama-3.1-8B-Instruct`) to generate publishable empirical results.

## 1. Local Model Integration (`src/models.py`)
*   **New Class:** `HuggingFaceModel(ReasoningModel)`
    *   **Backend:** Use `vllm` (vLLM) if available (much faster for A100), fallback to `transformers` pipeline.
    *   **Initialization:** Load model/tokenizer from HF path.
    *   **Reasoning Extraction:** Implement specific parsing for DeepSeek's `<think>` tags (already in base class, but verify).
*   **Models to Support:**
    *   `deepseek-ai/DeepSeek-R1-Distill-Llama-8B` (SOTA Reasoning)
    *   `meta-llama/Meta-Llama-3.1-8B-Instruct` (Standard Baseline)

## 2. Infrastructure (`run_a100.sh`)
*   **Dependencies:** Add `vllm`, `torch`, `accelerate`, `transformers`, `huggingface_hub`.
*   **Script:** Create a specialized run script that checks for NVIDIA GPU and installs CUDA-optimized libs.
*   **HuggingFace Token:** Script should support `HF_TOKEN` env var for accessing Llama-3.1.

## 3. Runner Updates (`src/runner.py`)
*   **Throughput:** vLLM handles async request batching natively.
    *   If correctly implemented in `models.py` (via `AsyncLLMEngine` or just fast synchronous `generate`), the existing async runner will work well.
    *   *Decision:* For simplicity and compatibility with the existing synchronous-wrap design, we will use vLLM's `LLM` class (synchronous offline inference) which is extremely fast and handles batching internally if we pass a list.
    *   *Refactor:* Update `runner.py` to optionally pass *batches* of prompts to `model.generate_batch()` if provided, OR stick to item-by-item if vLLM overhead is low enough (it is).

## 4. Verification
*   **Sanity Check:** Add a local inference test in `sanity_check.py` (if GPU available).
*   **Output:** Confirm `experiment_results.json` contains real text, not mock placeholders.

## 5. Statistical Hypothesis
*   **Hypothesis:** DeepSeek (Reasoning) will show a higher Adaptation Gap than Llama-3.1 (Standard) due to "context awareness" in its reasoning trace.
*   **Output:** T-test comparing these two specific groups.
