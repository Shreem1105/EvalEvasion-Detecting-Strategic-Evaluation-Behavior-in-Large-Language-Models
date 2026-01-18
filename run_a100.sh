#!/bin/bash
set -e

echo "========================================================"
echo "   EvalEvasion: A100 EMPIRICAL STUDY (Local Models)"
echo "========================================================"

# 1. Environment Check & Install
echo "[1/5] Checking GPU and Installing Dependencies..."
if ! command -v nvidia-smi &> /dev/null; then
    echo "Error: nvidia-smi not found. Are you on a GPU instance?"
    # Continue anyway for debugging if needed, or exit
fi
nvidia-smi

echo "Installing vLLM and HuggingFace libs..."
# Install vLLM optimized for A100
pip install vllm torch transformers accelerate huggingface_hub pandas matplotlib seaborn scipy nest_asyncio > /dev/null

# 2. Dataset Generation
echo "--------------------------------------------------------"
echo "[2/5] Ensuring Dataset Exists..."
# We assume the 500 tasks from the mock run are good, or regenerate.
# If we have keys, we regenerate. If not, we use mock generation.
python src/generate_dataset.py

# 3. DeepSeek R1 (Reasoning) Execution
echo "--------------------------------------------------------"
echo "[3/5] Running DeepSeek-R1-Distill-Llama-8B (The 'Reasoning' Agent)..."
# We run in a separate process to ensure full GPU memory cleanup
python src/runner.py --models deepseek-ai/DeepSeek-R1-Distill-Llama-8B --output results/results_deepseek.json

# 4. Llama 3.1 (Standard) Execution
echo "--------------------------------------------------------"
echo "[4/5] Running Meta-Llama-3.1-8B-Instruct (The 'Standard' Baseline)..."
# Note: Requires HF_TOKEN env var to be set for gated models
python src/runner.py --models meta-llama/Meta-Llama-3.1-8B-Instruct --output results/results_llama.json

# 5. Analysis
echo "--------------------------------------------------------"
echo "[5/5] Merging Results and Analyzing..."
# We need to merge the JSON files before analysis.
# Simple python snippet to merge:
python -c "
import json
import glob
files = glob.glob('results/experiment_results_*.json') + glob.glob('results/results_*.json')
all_data = []
for f in files:
    try:
        with open(f) as fp: all_data.extend(json.load(fp))
    except: pass
with open('results/experiment_results.json', 'w') as f:
    json.dump(all_data, f)
print(f'Merged {len(all_data)} records.')
"

python src/analysis.py
python src/plotting.py

echo "========================================================"
echo "   EMPIRICAL RUN COMPLETE"
echo "========================================================"
