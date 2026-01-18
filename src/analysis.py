import json
import pandas as pd
import numpy as np
import os
from typing import Dict, List
from metrics import calculate_metrics

class ResultAnalyzer:
    def __init__(self, input_file: str, output_dir: str):
        self.input_file = input_file
        self.output_dir = output_dir
        self.raw_data = self._load_data()
        
        # Ensure output directories exist
        os.makedirs(os.path.join(self.output_dir, "tables"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "figures"), exist_ok=True)

    def _load_data(self) -> pd.DataFrame:
        with open(self.input_file, 'r') as f:
            data = json.load(f)
        return pd.DataFrame(data)

    def analyze(self):
        df = self.raw_data
        
        # 1. Compute Metrics per Model per Task
        # Group by model_name, task_category, stage
        # We need to reshape to get columns for each stage's score
        
        results = []
        
        models = df['model_name'].unique()
        tasks = df['task_category'].unique()
        
        for model in models:
            for task in tasks:
                subset = df[(df['model_name'] == model) & (df['task_category'] == task)]
                if subset.empty:
                    continue
                
                # Get scores list for each stage
                scores_by_stage = {
                    stage: subset[subset['stage'] == stage]['score'].tolist() 
                    for stage in subset['stage'].unique()
                }
                
                # Calculate metrics using the logic from metrics.py
                metrics = calculate_metrics(scores_by_stage)
                
                row = {
                    'model_name': model,
                    'task_category': task,
                    **metrics
                }
                results.append(row)
        
        results_df = pd.DataFrame(results)
        
        # 2. Main Results Table (Aggregated across tasks)
        main_table = results_df.groupby('model_name').agg({
            'adaptation_gap': 'mean',
            'evaluation_sensitivity': 'mean',
            'consistency_degradation': 'mean',
            'baseline_score': 'mean',
            'eval_score': 'mean'
        }).reset_index()
        
        self._save_tables(results_df, main_table)
        return results_df, main_table

    def _save_tables(self, task_breakdown: pd.DataFrame, main_summary: pd.DataFrame):
        # Save CSVs
        task_breakdown.to_csv(os.path.join(self.output_dir, "tables", "task_breakdown.csv"), index=False)
        main_summary.to_csv(os.path.join(self.output_dir, "tables", "main_results.csv"), index=False)
        
        # Generate LaTeX
        latex_summary = main_summary.to_latex(index=False, float_format="%.2f", caption="Aggregated Results by Model")
        with open(os.path.join(self.output_dir, "tables", "main_results.tex"), 'w') as f:
            f.write(latex_summary)

        print(f"Analysis complete. Tables saved to {os.path.join(self.output_dir, 'tables')}")

if __name__ == "__main__":
    # Test on sanity check results if available
    input_path = "results/experiment_results.json"
    if os.path.exists(input_path):
        analyzer = ResultAnalyzer(input_path, "results")
        analyzer.analyze()
    else:
        print(f"Input file {input_path} not found.")
