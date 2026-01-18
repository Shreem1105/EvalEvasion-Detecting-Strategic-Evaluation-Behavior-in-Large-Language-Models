#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status

echo "========================================================"
echo "   EvalEvasion: A100 Colab Simulation Runner"
echo "========================================================"

# 1. Install Dependencies
echo "[1/4] Installing Python Dependencies..."
pip install openai google-generativeai pandas matplotlib seaborn scipy nest_asyncio > /dev/null
echo "Dependencies installed."

# 2. Generate Dataset
echo "--------------------------------------------------------"
echo "[2/4] Generating Scaled Dataset (Mock Mode)..."
python src/generate_dataset.py

# 3. Run Experiment
echo "--------------------------------------------------------"
echo "[3/4] Running High-Throughput Experiment..."
echo "      Concurrency: 50 | Models: 5 | Tasks: 100/domain"
python src/runner.py

# 4. Analysis & Plotting
echo "--------------------------------------------------------"
echo "[4/4] Analyzing Results & Generating Artifacts..."
python src/analysis.py
python src/plotting.py

echo "========================================================"
echo "   SUCCESS! All tasks completed."
echo "========================================================"
echo "Results available in:"
echo "  - results/experiment_results.json"
echo "  - results/tables/"
echo "  - results/figures/"
